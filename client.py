"""Own restricted query transport and bounded internal catalog collection."""

from datetime import datetime, timezone
from decimal import Decimal, DecimalException
import json
import sys
from types import TracebackType
import unicodedata

from anyio import fail_after, move_on_after
import httpx

from config import Settings
from catalog import CatalogRecord, NormalizationError, QueryResult
from catalog import normalize_record


class NetOneClientError(Exception):
    """Expose a fixed diagnostic, never a third-party exception or request."""

    code = 'client_error'

    def __init__(self) -> None:
        super().__init__(
            'NetOne HTTP client initialization or cleanup failed.'
        )


class BlockedOperationError(NetOneClientError):
    """Reject operations outside the documented internal query contract."""

    code = 'blocked_operation'

    def __init__(self) -> None:
        Exception.__init__(self, 'The NetOne query is not allowed.')


class ResponseError(Exception):
    """A fixed response diagnostic without upstream content."""

    _messages = {
        'authentication_error': 'NetOne authentication failed.',
        'authorization_error': 'NetOne authorization failed.',
        'not_found': 'The requested resource was not found.',
        'rate_limited': 'NetOne rate limit reached; try again later.',
        'upstream_error': 'NetOne returned an error.',
        'timeout': 'NetOne request timed out.',
        'connection_error': 'NetOne connection failed.',
        'invalid_response': 'NetOne returned an invalid response.',
    }

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(self._messages[code])


_MAX_RESPONSE_BYTES = 1_048_576
_CLEANUP_SECONDS = 1
_QUERY_PATHS = {
    'products': '/app-web/api/v2/produto/reduzidos',
    'prices': '/app-web/api/v2/produto/precos',
    'stock': '/app-web/api/v2/produto/estoque',
}


def _validate_query(page: object, limit: object, maximum: int) -> None:
    """Reject untyped, unbounded filters before creating a request."""
    if (
        type(page) is not int or not 1 <= page <= 1_000_000
        or type(limit) is not int or not 1 <= limit <= maximum
    ):
        raise BlockedOperationError()


def _validate_product_filter(
    operation: str, product_id: object, product_mask: object = None,
) -> None:
    """Allow one typed ID or commercial-code filter on products only."""
    if product_id is not None and (
        operation != 'products' or type(product_id) is not int
        or not 0 <= product_id <= 9223372036854775807
    ):
        raise BlockedOperationError()
    if product_mask is not None and (
        operation != 'products' or product_id is not None
        or not isinstance(product_mask, str)
        or not 1 <= len(product_mask) <= 256 or not product_mask.strip()
        or any(unicodedata.category(c).startswith('C') for c in product_mask)
    ):
        raise BlockedOperationError()


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate field')
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError('Non-finite JSON number')


async def _read_json_response(response: httpx.Response) -> dict[str, object]:
    """Read the public AsyncByteStream once and own its bounded cleanup.

    Iterating Response.aiter_raw() would auto-close outside our cancellation
    shield. The public stream protocol avoids that race without writing any
    HTTPX state or buffering the whole response before the byte limit.
    """
    try:
        errors = {
            401: 'authentication_error', 403: 'authorization_error',
            404: 'not_found', 429: 'rate_limited',
        }
        if response.status_code in errors:
            raise ResponseError(errors[response.status_code])
        if not response.is_success:
            raise ResponseError('upstream_error')
        if response.headers.get('content-encoding', 'identity').lower() != (
            'identity'
        ):
            raise ResponseError('invalid_response')
        data = bytearray()
        if not isinstance(response.stream, httpx.AsyncByteStream):
            raise ResponseError('invalid_response')
        async for chunk in response.stream:
            if len(data) + len(chunk) > _MAX_RESPONSE_BYTES:
                raise ResponseError('invalid_response')
            data.extend(chunk)
        try:
            value = json.loads(
                data, parse_float=Decimal, object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
        except (ValueError, UnicodeError, RecursionError, DecimalException):
            raise ResponseError('invalid_response') from None
        if not isinstance(value, dict) or not isinstance(
            value.get('result'), list,
        ):
            raise ResponseError('invalid_response')
        return value
    finally:
        # Cleanup must not hide an existing failure or external cancellation.
        active_exception = sys.exc_info()[0]
        try:
            with move_on_after(_CLEANUP_SECONDS, shield=True) as close_scope:
                await response.aclose()
            if close_scope.cancel_called and active_exception is None:
                raise ResponseError('upstream_error')
        except Exception:
            if active_exception is None:
                raise ResponseError('upstream_error') from None


def _request_guard(settings: Settings):
    """Check destination at send; _query alone constructs the closed body."""
    origin = httpx.URL(settings.base_url)

    async def guard(request: httpx.Request) -> None:
        url = request.url
        if (
            request.method != 'POST'
            or (url.scheme, url.host, url.port)
            != (origin.scheme, origin.host, origin.port)
            or request.headers.get('host', '').lower()
            != url.netloc.decode('ascii').lower()
            or url.path not in _QUERY_PATHS.values()
            or url.raw_path != url.path.encode('ascii')
            or url.query or url.fragment or url.userinfo
        ):
            raise BlockedOperationError()
    return guard


def _page_metadata(
    envelope: dict[str, object], requested: int,
) -> tuple[int | None, int | None]:
    """Validate published metadata without inventing absent totals."""
    for key in ('page', 'totalPages', 'totalElements'):
        value = envelope.get(key)
        if value is not None and (type(value) is not int or value < 0):
            raise ResponseError('invalid_response')
        if key in envelope and value is None:
            raise ResponseError('invalid_response')
    if 'page' in envelope and envelope['page'] != requested:
        raise ResponseError('invalid_response')
    pages_value = envelope.get('totalPages')
    elements_value = envelope.get('totalElements')
    pages = pages_value if isinstance(pages_value, int) else None
    elements = elements_value if isinstance(elements_value, int) else None
    if pages is not None and (
        pages < requested and not (requested == 1 and pages == 0)
    ):
        raise ResponseError('invalid_response')
    if 'page' not in envelope:
        return None, elements
    return pages, elements


class NetOneClient:
    """Keep HTTP/authentication private and close resources asynchronously.

    Accept only settings supplied by the process configuration loader.
    There is intentionally no public HTTP request or commercial operation.
    """

    __slots__ = ('_http', '_max_results', '_max_pages', '_deadline')

    def __init__(self, settings: Settings) -> None:
        self._max_results = settings.max_results
        self._max_pages = settings.max_pages
        self._deadline = settings.timeout_seconds * 4
        try:
            limits = httpx.Limits(
                max_connections=1, max_keepalive_connections=1,
            )
            transport = httpx.AsyncHTTPTransport(
                verify=True, trust_env=False, retries=0, limits=limits,
            )
            self._http = httpx.AsyncClient(
                base_url=settings.base_url,
                headers={
                    'netone-auth-token': settings.token.get_secret_value(),
                    'accept-encoding': 'identity',
                },
                timeout=httpx.Timeout(settings.timeout_seconds),
                trust_env=False,
                follow_redirects=False,
                transport=transport,
                event_hooks={'request': [_request_guard(settings)]},
            )
        except Exception:
            raise NetOneClientError() from None

    @property
    def is_closed(self) -> bool:
        """Report lifecycle state without exposing configuration or HTTPX."""
        return self._http.is_closed

    async def _query(
        self, operation: str, page: int, limit: int,
        *, product_id: int | None = None, product_mask: str | None = None,
    ) -> dict[str, object]:
        """Run a bounded internally selected query; never accept a URL."""
        path = _QUERY_PATHS.get(operation)
        if path is None:
            raise BlockedOperationError()
        _validate_query(page, limit, self._max_results)
        _validate_product_filter(operation, product_id, product_mask)
        body: dict[str, object] = {'page': page, 'limit': limit}
        if product_id is not None:
            body['idsProdutos'] = [product_id]
        if product_mask is not None:
            body['mascara'] = product_mask
        try:
            with fail_after(self._deadline):
                request = self._http.build_request(
                    'POST', path, json=body,
                )
                response = await self._http.send(request, stream=True)
                return await _read_json_response(response)
        except (TimeoutError, httpx.TimeoutException):
            code = 'timeout'
        except httpx.DecodingError:
            code = 'invalid_response'
        except httpx.RequestError:
            code = 'connection_error'
        except BlockedOperationError:
            raise
        except ResponseError as error:
            code = error.code
        except Exception:
            code = 'upstream_error'
        # Raise outside handlers so upstream exceptions do not retain context.
        raise ResponseError(code)

    async def _collect(
        self, operation: str, *, page_size: int | None = None,
        max_results: int | None = None, product_id: int | None = None,
        product_mask: str | None = None,
    ) -> QueryResult:
        """Collect internally; this does not authorize real calls or tools.

        The optional row budget is capped by configuration and stays local
        to this call. It counts received rows, including duplicates. Only
        page/limit and one optional typed products-only filter enter the
        guarded POST path. No resume cursor, tenant, arbitrary filter, URL
        or method is accepted.
        """
        if operation not in _QUERY_PATHS:
            raise BlockedOperationError()
        _validate_product_filter(operation, product_id, product_mask)
        if max_results is not None and (
            type(max_results) is not int or not 1 <= max_results <= 1000
        ):
            raise BlockedOperationError()
        budget = (
            self._max_results if max_results is None
            else min(max_results, self._max_results)
        )
        size = min(50, budget) if page_size is None else page_size
        _validate_query(1, size, budget)
        items: list[CatalogRecord] = []
        seen: dict[tuple[str | None, str], list[dict[str, object]]] = {}
        warnings: list[str] = []
        pages_fetched = 0
        rows_received = 0
        total_pages = None
        total_elements = None
        complete = False
        error_code = None

        def warn(code: str) -> None:
            if code not in warnings:
                warnings.append(code)

        async def collect_pages() -> None:
            nonlocal pages_fetched, rows_received, total_pages
            nonlocal total_elements, complete
            for page in range(1, self._max_pages + 1):
                # Changing limit mid-traversal can change offset semantics.
                if budget - rows_received < size:
                    warn('result_limit_reached')
                    return
                limit = size
                envelope = await self._query(
                    operation, page, limit, product_id=product_id,
                    product_mask=product_mask,
                )
                rows = envelope['result']
                if not isinstance(rows, list) or len(rows) > limit:
                    raise ResponseError('invalid_response')
                pages_fetched += 1
                rows_received += len(rows)
                pages, elements = _page_metadata(envelope, page)
                if (
                    total_pages is not None and pages != total_pages
                    or total_elements is not None
                    and elements != total_elements
                ):
                    raise ResponseError('invalid_response')
                # Reject a contradictory page before accepting any of its rows.
                if pages == 0 and rows:
                    raise ResponseError('invalid_response')
                if elements is not None and (
                    rows_received > elements
                    or pages is not None and page >= pages
                    and rows_received != elements
                ):
                    raise ResponseError('invalid_response')
                total_pages, total_elements = pages, elements
                normalized = [normalize_record(operation, row) for row in rows]
                if product_id is not None and any(
                    record.product_id != str(product_id)
                    for record in normalized
                ):
                    raise ResponseError('invalid_response')
                new_rows = 0
                for row, record in zip(rows, normalized):
                    key = (record.product_id, record.reduced_id)
                    previous = seen.setdefault(key, [])
                    if row in previous:
                        warn('duplicate_rows_removed')
                        continue
                    if previous:
                        warn('conflicting_rows_preserved')
                    previous.append(row)
                    items.append(record)
                    new_rows += 1
                    if record.last_changed_raw is not None:
                        warn('timestamp_semantics_unverified')
                if pages is None:
                    warn('pagination_metadata_missing')
                    return
                # An empty first terminal page is a valid empty query; later
                # empty/repeated pages cannot prove an advancing traversal.
                if not new_rows and (page > 1 or pages > 1):
                    warn('pagination_no_progress')
                    return
                if page >= pages:
                    complete = True
                    return
                if rows_received >= budget:
                    warn('result_limit_reached')
                    return
            warn('page_limit_reached')

        try:
            with fail_after(self._deadline):
                await collect_pages()
        except ResponseError as error:
            # A missing HTTP resource is not a valid empty product result.
            error_code = error.code
        except NormalizationError:
            error_code = 'invalid_response'
        except TimeoutError:
            error_code = 'timeout'
        if error_code is not None:
            warn('collection_interrupted')
        partial = not complete or 'conflicting_rows_preserved' in warnings
        status = (
            'partial' if partial else 'found' if items else 'not_found'
        )
        if error_code is not None and not items:
            status = 'error'
        return QueryResult(
            status=status, items=tuple(items), partial=partial,
            warnings=tuple(warnings), error=error_code, operation=operation,
            retrieved_at=(datetime.now(timezone.utc).isoformat()
                          if pages_fetched else None),
            pages_fetched=pages_fetched, rows_received=rows_received,
            total_pages=total_pages, total_elements=total_elements,
            complete_dataset=complete and not partial,
        )

    async def __aenter__(self) -> 'NetOneClient':
        try:
            await self._http.__aenter__()
        except Exception:
            raise NetOneClientError() from None
        return self

    async def aclose(self) -> None:
        """Close the pool; callers must not log underlying exceptions."""
        try:
            with move_on_after(_CLEANUP_SECONDS, shield=True) as scope:
                await self._http.aclose()
            if scope.cancel_called:
                raise NetOneClientError()
        except Exception:
            raise NetOneClientError() from None

    async def __aexit__(
        self, exc_type: type[BaseException] | None,
        exc_value: BaseException | None, traceback: TracebackType | None,
    ) -> None:
        try:
            await self.aclose()
        except NetOneClientError:
            # The body failure/cancellation has priority over cleanup failure.
            if exc_type is None:
                raise
