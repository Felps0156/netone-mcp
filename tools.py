"""Bounded commercial application queries, without MCP registration."""

from dataclasses import replace
import re
from typing import Literal, cast
import unicodedata

from client import NetOneClient
from catalog import CatalogRecord, QueryResult


def _filtered_result(
    result: QueryResult, items: tuple[CatalogRecord, ...], warning: str,
) -> dict[str, object]:
    """Retain collection failures and completeness when selecting records."""
    status = result.status
    if status not in ('partial', 'error'):
        status = 'found' if items else 'not_found'
    return replace(
        result, items=items, status=status,
        warnings=(*result.warnings, warning),
    ).as_json()


def _validate_code_input(code: object, max_results: object) -> None:
    """Validate without transforming source codes or echoing rejected data."""
    if (
        not isinstance(code, str) or not 1 <= len(code) <= 256
        or not code.strip()
        or any(unicodedata.category(char).startswith('C') for char in code)
    ):
        raise ValueError('Code must be 1 to 256 characters without controls.')
    if type(max_results) is not int or not 1 <= max_results <= 1000:
        raise ValueError('max_results must be an integer from 1 to 1000.')


def _validate_search_limits(max_results: object, max_items: object) -> None:
    for value in (max_results, max_items):
        if type(value) is not int or not 1 <= value <= 1000:
            raise ValueError('Search limits must be integers from 1 to 1000.')


def _search_result(
    result: QueryResult, items: tuple[CatalogRecord, ...], warning: str,
    max_results: int, max_items: int,
) -> dict[str, object]:
    """Separate source traversal completeness from output truncation."""
    truncated = len(items) > max_items
    selected = replace(
        result,
        status=('error' if result.status == 'error' else 'partial')
        if truncated else result.status,
        partial=result.partial or truncated,
        complete_dataset=result.complete_dataset and not truncated,
        warnings=(*result.warnings, 'output_limit_reached')
        if truncated else result.warnings,
    )
    output = _filtered_result(selected, items[:max_items], warning)
    output.update(
        requested_max_results=max_results, requested_max_items=max_items,
        output_limit=min(max_items, result.inspection_limit or max_results),
        matched_count=len(items), output_truncated=truncated,
        collection_complete=result.complete_dataset,
    )
    return output


async def search_products(
    client: NetOneClient, query: str, max_results: int = 100,
    *, max_items: int = 20,
) -> dict[str, object]:
    """Filter a bounded product traversal, not a remote text-search result.

    The row budget includes nonmatches and duplicates and is capped by the
    client configuration. Partial collection remains partial even when no
    text matches. Source values and collection metadata stay unchanged.
    """
    if (
        not isinstance(query, str) or not 1 <= len(query) <= 200
        or not query.strip()
        or any(unicodedata.category(char).startswith('C') for char in query)
    ):
        raise ValueError('Query must be 1 to 200 characters without controls.')
    _validate_search_limits(max_results, max_items)
    needle = query.strip().casefold()
    result = await client._collect('products', max_results=max_results)
    items = tuple(
        item for item in result.items
        if any(
            value is not None and needle in value.casefold()
            for value in (item.description, item.product_mask, item.sku)
        )
    )
    return _search_result(
        result, items, 'local_text_search', max_results, max_items,
    )


# Related names are possible alternatives, not proof of product equivalence.
_REVIEWED_RELATED_TERMS = {
    'manopla': ('punho',),
    'punho': ('manopla',),
}


def _search_term(value: object) -> str:
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 200
        or not value.strip() or not _lexical_text(value).strip()
        or any(unicodedata.category(char).startswith('C') for char in value)
    ):
        raise ValueError('Search terms must be 1 to 200 characters without controls.')
    return value.strip()


def _search_terms(values: object) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)) or len(values) > 20:
        raise ValueError('Search terms must be a list of at most 20 strings.')
    return tuple(_search_term(value) for value in values)


def _lexical_text(value: str) -> str:
    """Fold comparison copies only; source text and exact codes stay intact."""
    return ''.join(
        char for char in unicodedata.normalize('NFKD', value.casefold())
        if not unicodedata.category(char).startswith('M')
    )


def _lexical_pattern(value: str) -> re.Pattern[str]:
    return re.compile(r'(?<!\w)' + re.escape(_lexical_text(value)) + r'(?!\w)')


def _composed_query(original: str) -> tuple[str, tuple[str, ...], bool]:
    """Split only an unambiguous reviewed leading type, never infer a brand."""
    parts = original.split(maxsplit=1)
    if len(parts) == 1:
        return original, (), True
    normalized = _lexical_text(original)
    occurrences = sum(
        len(_lexical_pattern(term).findall(normalized))
        for term in _REVIEWED_RELATED_TERMS
    )
    if _lexical_text(parts[0]) in _REVIEWED_RELATED_TERMS and occurrences == 1:
        return parts[0], (_search_term(parts[1]),), True
    return original, (), False


async def search_products_expanded(
    client: NetOneClient, query: str, *,
    required_terms: tuple[str, ...] = (),
    suggested_terms: tuple[str, ...] = (),
    max_results: int = 100, max_items: int = 20,
) -> dict[str, object]:
    """Search a product term and separate textual restrictions, locally.

    Related terms are possible matches, not proof of equivalence. A complete
    traversal is neither a snapshot nor proof of semantic coverage.
    """
    original = _search_term(query)
    required = _search_terms(required_terms)
    suggested = _search_terms(suggested_terms)
    _validate_search_limits(max_results, max_items)
    product_term, restrictions, alternatives = _composed_query(original)
    required = (*required, *restrictions)
    reviewed = _REVIEWED_RELATED_TERMS.get(_lexical_text(product_term), ())
    if not alternatives:
        reviewed, suggested = (), ()
    terms: list[tuple[str, str]] = []
    seen: set[str] = set()
    for kind, term_candidates in (
        ('direct', (product_term,)), ('reviewed', reviewed),
        ('suggested', suggested),
    ):
        for candidate in term_candidates:
            key = _lexical_text(candidate)
            if key not in seen:
                seen.add(key)
                terms.append((candidate, kind))
    patterns = [(term, kind, _lexical_pattern(term)) for term, kind in terms]
    required_patterns = [_lexical_pattern(term) for term in required]
    result = await client._collect('products', max_results=max_results)
    if 'duplicate_rows_removed' in result.warnings:
        result = replace(result, status='partial', partial=True,
                         complete_dataset=False)
    candidates: list[tuple[CatalogRecord, dict[str, object], int]] = []
    unverified = 0
    for item in result.items:
        description = _lexical_text(item.description or '')
        matched = [(term, kind) for term, kind, pattern in patterns
                   if pattern.search(description) is not None]
        if matched and any(
            pattern.search(description) is None for pattern in required_patterns
        ):
            unverified += 1
            continue
        if matched:
            candidates.append((item, {
                'matched_terms': [term for term, _ in matched],
                'match_type': matched[0][1],
            }, {'direct': 0, 'reviewed': 1, 'suggested': 2}[matched[0][1]]))
    candidates.sort(key=lambda candidate: candidate[2])
    output = _search_result(
        result, tuple(item for item, _, _ in candidates),
        'local_related_text_search', max_results, max_items,
    )
    output['matches'] = [match for _, match, _ in candidates[:max_items]]
    output['search_terms'] = [
        {'term': term, 'type': kind} for term, kind in terms
    ]
    output['required_terms'] = list(required)
    output['unverified_restriction_count'] = unverified
    warnings = cast(list[str], output['warnings'])
    warnings.append('traversal_not_snapshot_or_semantic_coverage')
    if not alternatives:
        warnings.append('ambiguous_query_literal_only')
    return output


async def get_product_details(
    client: NetOneClient, product_id: int, max_results: int = 20,
) -> dict[str, object]:
    """Return bounded reduced records for one strictly validated product ID."""
    if (
        type(product_id) is not int
        or not 0 <= product_id <= 9223372036854775807
    ):
        raise ValueError('product_id must be an integer from 0 to 2**63 - 1.')
    if type(max_results) is not int or not 1 <= max_results <= 1000:
        raise ValueError('max_results must be an integer from 1 to 1000.')
    result = await client._collect(
        'products', max_results=max_results, product_id=product_id,
    )
    return result.as_json()


async def _search_exact_code(
    client: NetOneClient, code: str, max_results: int,
    field: Literal['sku', 'ean'],
) -> dict[str, object]:
    """Compare one source field exactly within a bounded local traversal."""
    _validate_code_input(code, max_results)
    result = await client._collect('products', max_results=max_results)
    items = tuple(
        item for item in result.items if getattr(item, field) == code
    )
    return _filtered_result(result, items, f'local_exact_{field}_search')


async def search_product_by_code(
    client: NetOneClient, code: str, max_results: int = 20,
) -> dict[str, object]:
    """Prefer the commercial mask/code; keep API codigoSku separate.

    The provider's mask-filter equality is not assumed. Select exact masks
    locally from its bounded filtered response, preserving partial/errors.
    """
    _validate_code_input(code, max_results)
    result = await client._collect(
        'products', max_results=max_results, product_mask=code,
    )
    items = tuple(item for item in result.items if item.product_mask == code)
    return _filtered_result(result, items, 'remote_product_code_exact_match')


async def search_product_by_sku(
    client: NetOneClient, sku: str, max_results: int = 20,
) -> dict[str, object]:
    """Match codigoSku exactly; a bounded miss never proves global absence."""
    return await _search_exact_code(client, sku, max_results, 'sku')


async def search_product_by_ean(
    client: NetOneClient, ean: str, max_results: int = 20,
) -> dict[str, object]:
    """Match ean exactly without trimming, coercion or checksum inference."""
    return await _search_exact_code(client, ean, max_results, 'ean')


async def get_product_price(
    client: NetOneClient, product_id: str, max_results: int = 20,
    *, currency: Literal['BRL'] | None = None,
) -> dict[str, object]:
    """Select nominal source prices by exact local normalized product ID.

    Currency is trusted operator context, not an API field or conversion.
    A limited miss cannot establish global absence or a final quote.
    """
    _validate_code_input(product_id, max_results)
    if currency is not None and (
        not isinstance(currency, str) or currency != 'BRL'
    ):
        raise ValueError('Currency must be BRL or unknown.')
    result = await client._collect('prices', max_results=max_results)
    items = tuple(item for item in result.items
                  if item.product_id == product_id)
    output = _filtered_result(
        result, items, 'local_exact_product_id_price_search',
    )
    warnings = [*result.warnings, 'local_exact_product_id_price_search',
                'nominal_prices_not_final_quote']
    if currency is None:
        warnings.append('currency_unknown')
    if any(item.price is None and item.wholesale_price is None
           for item in items):
        warnings.append('price_missing')
    output.update(
        currency=currency,
        currency_source='operator_confirmation' if currency else None,
        price_kind='source_retail_and_wholesale', warnings=warnings,
    )
    return output


async def check_inventory(
    client: NetOneClient, reduced_id: str, max_results: int = 20,
) -> dict[str, object]:
    """Select an exact local reduced identity in the user's stock scope.

    Quantities are source physical-minus-reservations values, not a promise
    of sellability. Deposit identity and stock freshness remain unverified.
    """
    _validate_code_input(reduced_id, max_results)
    result = await client._collect('stock', max_results=max_results)
    items = tuple(item for item in result.items
                  if item.reduced_id == reduced_id)
    output = _filtered_result(
        result, items, 'local_exact_reduced_id_stock_search',
    )
    warnings = [*result.warnings, 'local_exact_reduced_id_stock_search',
                'inventory_scope_unverified', 'inventory_freshness_unverified']
    if any(item.quantity is None for item in items):
        warnings.append('quantity_missing')
    output.update(
        inventory_scope={
            'selection': 'configured_user_deposit', 'deposit_id': None,
            'branch_id': None, 'quantity_basis': 'physical_minus_reservations',
        },
        warnings=warnings,
    )
    return output


async def list_products(
    client: NetOneClient, max_results: int = 20, *,
    page_size: int | None = None, max_pages: int = 1,
) -> dict[str, object]:
    """List from page one, fetching at most one page unless explicitly set.

    Limits count received rows, not distinct products. A complete traversal
    describes only the provider-visible endpoint, not an ERP-wide snapshot.
    """
    if type(max_results) is not int or not 1 <= max_results <= 1000:
        raise ValueError('max_results must be an integer from 1 to 1000.')
    if type(max_pages) is not int or not 1 <= max_pages <= 100:
        raise ValueError('max_pages must be an integer from 1 to 100.')
    result = await client._collect(
        'products', max_results=max_results,
        page_size=page_size, max_pages=max_pages,
    )
    return replace(
        result, warnings=(*result.warnings, 'provider_visible_catalog_only'),
    ).as_json()
