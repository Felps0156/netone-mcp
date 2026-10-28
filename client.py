"""Own a token-configured HTTP client without approved query operations."""

import logging
from types import TracebackType

from anyio import CancelScope
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


async def _reject_unapproved_request(request: httpx.Request) -> None:
    """Fail before transport; no method, path or body is released yet."""
    raise BlockedOperationError()


class NetOneClient:
    """Keep HTTP/authentication private and close resources asynchronously.

    Accept only settings supplied by the process configuration loader.
    There is intentionally no public HTTP request or commercial operation.
    """

    __slots__ = ('_http',)

    def __init__(self, settings: Settings) -> None:
        _silence_http_logging()
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
                },
                timeout=httpx.Timeout(settings.timeout_seconds),
                verify=True,
                trust_env=False,
                follow_redirects=False,
                transport=transport,
                event_hooks={'request': [_reject_unapproved_request]},
            )
        except Exception:
            raise NetOneClientError() from None

    @property
    def is_closed(self) -> bool:
        """Report lifecycle state without exposing configuration or HTTPX."""
        return self._http.is_closed

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
