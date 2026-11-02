"""Read-only, memory-only catalog/stock orchestration outside the MCP server.

Pass an initialized generic MCP ClientSession (including a Hermes-managed
session adapter). This module never loads configuration, opens a connection,
writes files or registers tools. Invocation still requires operator authority.
"""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Protocol, TypeGuard
import unicodedata

from anyio import fail_after


class ToolSession(Protocol):
    async def call_tool(
        self, name: str, arguments: dict[str, Any],
    ) -> Any: ...


@dataclass
class _Traversal:
    records: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    conflicts: set[str] = field(default_factory=set)
    last_page: int = 0
    total_pages: int | None = None
    total_elements: int | None = None
    rows_received: int = 0
    complete: bool = False

    def summary(self) -> dict[str, object]:
        return {
            'last_page': self.last_page, 'total_pages': self.total_pages,
            'total_elements': self.total_elements,
            'rows_received': self.rows_received,
            'collection_complete': self.complete,
            'records': [record for group in self.records.values()
                        for record in group],
        }


def _integer(value: object, lower: int, upper: int) -> TypeGuard[int]:
    return type(value) is int and lower <= value <= upper


def _quantity(value: object) -> Decimal | None:
    if value is None:
        return None
    if not isinstance(value, str) or not 1 <= len(value) <= 256:
        raise ValueError
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ValueError from None
    if not amount.is_finite():
        raise ValueError
    return amount


def _records(value: object, size: int) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > size:
        raise ValueError
    for record in value:
        if not isinstance(record, dict):
            raise ValueError
        identity = record.get('reduced_id')
        if (
            not isinstance(identity, str) or not 1 <= len(identity) <= 256
            or not identity.strip()
            or any(unicodedata.category(c).startswith('C') for c in identity)
        ):
            raise ValueError
        _quantity(record.get('quantity'))
    return value


def _validate_block(
    data: dict[str, Any], state: _Traversal, page: int, size: int,
) -> list[dict[str, Any]]:
    """Validate cross-call progress atomically, including terminal counts."""
    records = _records(data.get('items'), size)
    pages, elements = data.get('total_pages'), data.get('total_elements')
    if (
        not _integer(pages, 0, 1_000_000)
        or elements is not None and not _integer(elements, 0, 1_000_000_000)
        or data.get('pages_fetched') != 1
        or type(data.get('pages_fetched')) is not int
        or data.get('page_size') != size
        or type(data.get('page_size')) is not int
        or data.get('start_page') != page
        or data.get('first_page') != page
        or data.get('last_page') != page
        or any(type(data.get(k)) is not int for k in
               ('start_page', 'first_page', 'last_page'))
        or not _integer(data.get('rows_received'), 0, size)
        or data['rows_received'] != len(records)
        or data.get('returned_count') != len(records)
        or type(data.get('returned_count')) is not int
        or state.total_pages is not None and pages != state.total_pages
        or state.last_page and elements != state.total_elements
        or pages == 0 and (page != 1 or records)
        or pages > 0 and page > pages
        or not records and (page != 1 or pages > 1)
    ):
        raise ValueError
    terminal = page >= pages
    expected_partial = page != 1 or not terminal
    expected_status = ('partial' if expected_partial else
                       'found' if records else 'not_found')
    if (
        data.get('partial') is not expected_partial
        or data.get('complete_dataset') is not (not expected_partial)
        or data.get('status') != expected_status
        or data.get('block_complete') is not True
        or data.get('endpoint_exhausted') is not terminal
        or (data.get('next_page') is not None if terminal else
            type(data.get('next_page')) is not int
            or data.get('next_page') != page + 1)
        or elements is not None and (
            elements > pages * size
            or state.rows_received + len(records) > elements
            or terminal and state.rows_received + len(records) != elements
        )
    ):
        raise ValueError
    return records


async def collect_catalog_inventory(
    session: ToolSession, *, page_size: int = 50, max_calls: int = 200,
    max_pages: int = 200, max_rows: int = 10_000,
    timeout_seconds: int = 60,
) -> dict[str, object]:
    """Traverse both existing list tools, then reconcile exact reduced IDs.

    Limits are global across both endpoints, not per tool. Each call asks for
    exactly one fixed-size page and remains subject to server configuration.
    Stop on the first error, duplicate, conflict or inconsistent progress;
    never retry. Unknown/missing stock is never zero. No source sums or
    product-ID joins are performed. All retained records are returned in
    memory only; the caller owns session lifecycle and authorized disclosure.
    """
    for value, upper in ((page_size, 50), (max_calls, 1_000_000),
                         (max_pages, 1_000_000), (max_rows, 1_000_000),
                         (timeout_seconds, 3600)):
        if not _integer(value, 1, upper):
            raise ValueError('Campaign limits must be bounded strict integers.')
    catalog, inventory = _Traversal(), _Traversal()
    calls = pages_fetched = rows_received = 0
    warnings = ['visible_endpoints_not_snapshot_or_global_erp',
                'inventory_scope_unverified', 'inventory_freshness_unverified']
    error = None

    def warn(code: str) -> None:
        if code not in warnings:
            warnings.append(code)

    def merge(state: _Traversal, records: list[dict[str, Any]]) -> bool:
        anomaly = False
        for record in records:
            group = state.records.setdefault(record['reduced_id'], [])
            if record in group:
                warn('duplicate_rows_removed')
                anomaly = True
            else:
                if group:
                    warn('conflicting_rows_preserved')
                    anomaly = True
                group.append(record.copy())
        return anomaly

    async def traverse(name: str, state: _Traversal) -> bool:
        nonlocal calls, pages_fetched, rows_received, error
        while not state.complete:
            if calls >= max_calls or pages_fetched >= max_pages:
                warn('campaign_page_or_call_limit_reached')
                return False
            if max_rows - rows_received < page_size:
                warn('campaign_row_limit_reached')
                return False
            page = state.last_page + 1
            if page > 1_000_000:
                warn('campaign_page_range_limit_reached')
                return False
            calls += 1
            try:
                reply = await session.call_tool(name, {
                    'start_page': page, 'page_size': page_size,
                    'max_results': page_size, 'max_pages': 1,
                })
            except Exception:
                error = 'mcp_call_failed'
                return False
            data = getattr(reply, 'structuredContent', None)
            if getattr(reply, 'isError', True) or not isinstance(data, dict):
                error = 'mcp_tool_failed'
                return False
            # Count fetched work even when the returned page is rejected.
            fetched, received = data.get('pages_fetched'), data.get('rows_received')
            if _integer(fetched, 0, 1):
                pages_fetched += fetched
            if _integer(received, 0, page_size):
                rows_received += received
            if data.get('error') is not None or data.get('status') == 'error':
                error = 'upstream_collection_failed'
                return False
            # Collector-normalized conflicting rows are useful evidence, but
            # cannot advance a safe page. Preserve them without a balance sum.
            source_warnings = data.get('warnings')
            if not isinstance(source_warnings, list) or any(
                not isinstance(w, str) for w in source_warnings
            ):
                error = 'inconsistent_paging_or_records'
                return False
            unsafe = {'duplicate_rows_removed', 'conflicting_rows_preserved',
                      'pagination_no_progress', 'pagination_metadata_missing'}
            flagged = unsafe.intersection(source_warnings)
            if flagged:
                for code in flagged:
                    warn(code)
                try:
                    records = _records(data.get('items'), page_size)
                except ValueError:
                    error = 'inconsistent_paging_or_records'
                    return False
                merge(state, records)
                if 'conflicting_rows_preserved' in flagged:
                    # The block warning has no per-row provenance. Conservatively
                    # exclude every identity in it, even if projection hid a diff.
                    state.conflicts.update(r['reduced_id'] for r in records)
                return False
            try:
                records = _validate_block(data, state, page, page_size)
            except (ValueError, TypeError, KeyError):
                error = 'inconsistent_paging_or_records'
                return False
            if merge(state, records):
                return False
            state.last_page = page
            state.rows_received += len(records)
            state.total_pages = data['total_pages']
            state.total_elements = data.get('total_elements')
            state.complete = data['endpoint_exhausted']
        return True

    try:
        with fail_after(timeout_seconds):
            if await traverse('list_products', catalog):
                await traverse('list_inventory', inventory)
    except TimeoutError:
        error = 'campaign_timeout'

    items: list[dict[str, object]] = []
    for identity, products in catalog.records.items():
        stocks = inventory.records.get(identity, [])
        quantity = stocks[0].get('quantity') if len(stocks) == 1 else None
        amount = _quantity(quantity)
        if (len(products) > 1 or len(stocks) > 1
                or identity in catalog.conflicts or identity in inventory.conflicts):
            stock_status, quantity = 'conflict', None
        elif not stocks:
            stock_status = 'not_found' if inventory.complete else 'unknown'
        elif amount is None:
            stock_status = 'unknown'
        else:
            stock_status = ('positive' if amount > 0 else 'zero'
                            if amount == 0 else 'negative')
        items.append({
            'reduced_id': identity, 'catalog_records': products,
            'inventory_records': stocks, 'quantity': quantity,
            'stock_status': stock_status,
        })
    collection_complete = catalog.complete and inventory.complete
    partial = not collection_complete or any(
        item['stock_status'] in ('unknown', 'conflict') for item in items
    )
    if any(item['stock_status'] == 'unknown' for item in items):
        warn('quantity_unknown')
    return {
        'status': ('error' if error and not items else 'partial' if partial
                   else 'found' if items else 'not_found'),
        'partial': partial, 'error': error, 'warnings': warnings,
        'collection_complete': collection_complete,
        'complete_dataset': collection_complete and not partial,
        'items': items, 'returned_count': len(items),
        'catalog': catalog.summary(), 'inventory': inventory.summary(),
        'inventory_only_ids': sorted(inventory.records.keys()
                                     - catalog.records.keys()),
        'calls_made': calls, 'pages_fetched': pages_fetched,
        'rows_received': rows_received,
        'limits': {'page_size': page_size, 'max_calls': max_calls,
                   'max_pages': max_pages, 'max_rows': max_rows,
                   'timeout_seconds': timeout_seconds},
    }
