"""Own a token-configured HTTP client without approved query operations."""

from decimal import Decimal, DecimalException
import json
import logging
import sys
from types import TracebackType
from types import MappingProxyType

from anyio import CancelScope, fail_after, move_on_after
import httpx

from config import Settings


class NetOneClientError(Exception):
    """Expose a fixed diagnostic, never a third-party exception or request."""

    code = 'client_error'

    def __init__(self) -> None:
        super().__init__(
            'NetOne HTTP client initialization or cleanup failed.'
        )


class BlockedOperationError(NetOneClientError):
    """Reject every request until operations receive individual approval."""

    code = 'blocked_operation'

    def __init__(self) -> None:
        Exception.__init__(self, 'No NetOne HTTP operation is approved.')


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
_QUERY_PATHS = MappingProxyType({
    'products': '/app-web/api/v2/produto/reduzidos',
    'prices': '/app-web/api/v2/produto/precos',
    'stock': '/app-web/api/v2/produto/estoque',
})


def _validate_query(page: object, limit: object, maximum: int) -> None:
    """Reject untyped, unbounded filters before creating a request."""
    if (
        type(page) is not int or not 1 <= page <= 1_000_000
        or type(limit) is not int or not 1 <= limit <= maximum
    ):
        raise BlockedOperationError()


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate field')
        result[key] = value
    return result


async def _read_json_response(response: httpx.Response) -> dict[str, object]:
    """Consume a streamed, uncompressed response with fixed diagnostics."""
    code = None
    value = None
    try:
        status = response.status_code
        if status == 401:
            raise ResponseError('authentication_error')
        if status == 403:
            raise ResponseError('authorization_error')
        if status == 404:
            raise ResponseError('not_found')
        if status == 429:
            raise ResponseError('rate_limited')
        if not 200 <= status < 300:
            raise ResponseError('upstream_error')
        if response.headers.get('content-encoding', 'identity').lower() != (
            'identity'
        ):
            raise ResponseError('invalid_response')
        data = bytearray()
        async for chunk in response.aiter_raw():
            if len(data) + len(chunk) > _MAX_RESPONSE_BYTES:
                raise ResponseError('invalid_response')
            data.extend(chunk)
        try:
            value = json.loads(
                data, parse_float=Decimal, object_pairs_hook=_unique_object,
                parse_constant=lambda _: (_ for _ in ()).throw(ValueError()),
            )
        except (ValueError, UnicodeError, RecursionError, DecimalException):
            raise ResponseError('invalid_response') from None
        if not isinstance(value, dict):
            raise ResponseError('invalid_response')
    except ResponseError as error:
        code = error.code
    except httpx.TimeoutException:
        code = 'timeout'
    except httpx.DecodingError:
        code = 'invalid_response'
    except httpx.RequestError:
        code = 'connection_error'
    except Exception:
        code = 'invalid_response'
    finally:
        active_exception = sys.exc_info()[0] is not None
        close_failed = False
        try:
            with move_on_after(1, shield=True) as close_scope:
                await response.aclose()
            close_failed = close_scope.cancel_called
        except Exception:
            close_failed = True
        if close_failed and code is None and not active_exception:
            code = 'upstream_error'
    if code is not None:
        raise ResponseError(code)
    if not isinstance(value, dict):
        raise ResponseError('invalid_response')
    return value


def _silence_http_logging() -> None:
    """Suppress raw transport diagnostics in this dedicated MCP process."""
    names = {'httpx', 'httpcore'}
    names.update(
        name for name in logging.Logger.manager.loggerDict
        if name.startswith(('httpx.', 'httpcore.'))
    )
    for name in names:
        logger = logging.getLogger(name)
        logger.disabled = True
        logger.setLevel(logging.CRITICAL + 1)
        logger.propagate = False
        # Descendants created later inherit the disabled output boundary.
        if not logger.handlers:
            logger.addHandler(logging.NullHandler())


def _request_guard(settings: Settings):
    """Enforce the literal method, origin, route and closed body at send."""
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
        try:
            body = json.loads(
                request.content, object_pairs_hook=_unique_object,
            )
            if not isinstance(body, dict) or set(body) != {'page', 'limit'}:
                raise ValueError('Invalid fields')
            _validate_query(body['page'], body['limit'], settings.max_results)
        except (ValueError, TypeError, KeyError, httpx.RequestNotRead):
            raise BlockedOperationError() from None

    return guard


class NetOneClient:
    """Keep HTTP/authentication private and close resources asynchronously.

    Accept only settings supplied by the process configuration loader.
    There is intentionally no public HTTP request or commercial operation.
    """

    __slots__ = ('_http', '_max_results', '_deadline')

    def __init__(self, settings: Settings) -> None:
        _silence_http_logging()
        self._max_results = settings.max_results
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
                verify=True,
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
    ) -> dict[str, object]:
        """Run a bounded internally selected query; never accept a URL."""
        path = _QUERY_PATHS.get(operation)
        if path is None:
            raise BlockedOperationError()
        _validate_query(page, limit, self._max_results)
        code = None
        try:
            with fail_after(self._deadline):
                async with self._http.stream(
                    'POST', path, json={'page': page, 'limit': limit},
                ) as response:
                    result = await _read_json_response(response)
                    if not isinstance(result.get('result'), list):
                        raise ResponseError('invalid_response')
                    return result
        except TimeoutError:
            code = 'timeout'
        except httpx.TimeoutException:
            code = 'timeout'
        except httpx.RequestError:
            code = 'connection_error'
        except (BlockedOperationError, ResponseError):
            raise
        except Exception:
            code = 'upstream_error'
        if code is not None:
            raise ResponseError(code)
        raise ResponseError('upstream_error')

    async def __aenter__(self) -> 'NetOneClient':
        try:
            await self._http.__aenter__()
        except Exception:
            raise NetOneClientError() from None
        return self

    async def aclose(self) -> None:
        """Close the pool; callers must not log underlying exceptions."""
        try:
            with CancelScope(shield=True):
                await self._http.aclose()
        except Exception:
            raise NetOneClientError() from None

    async def __aexit__(
        self, exc_type: type[BaseException] | None,
        exc_value: BaseException | None, traceback: TracebackType | None,
    ) -> None:
        await self.aclose()
