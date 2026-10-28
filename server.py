"""Start an MCP stdio server without commercial tools."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
import sys

from mcp.server.fastmcp import FastMCP

from client import NetOneClient, NetOneClientError
from config import ConfigurationError, Settings, load_config


class _SafeDiagnosticFormatter(logging.Formatter):
    """Never render SDK messages, validation inputs or exception details."""

    def format(self, record: logging.LogRecord) -> str:
        return 'mcp_diagnostic: Diagnostic details suppressed for security.'


def _configure_safe_logging(level: str) -> None:
    """Own stderr logging, including SDK calls to the root logger."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_SafeDiagnosticFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
    names = {'mcp'}
    names.update(
        name for name in logging.Logger.manager.loggerDict
        if name.startswith('mcp.')
    )
    for name in names:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(logging.NOTSET)


def create_server(settings: Settings) -> FastMCP:
    """Bind a process-owned HTTP client to the empty stdio server lifespan."""
    _configure_safe_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastMCP) -> AsyncIterator[dict[str, NetOneClient]]:
        async with NetOneClient(settings) as client:
            yield {'netone_client': client}

    return FastMCP(
        'netone-mcp', lifespan=lifespan, log_level=settings.log_level,
    )


def main() -> int:
    """Validate once, then run stdio with managed resources and safe errors."""
    try:
        settings = load_config()
    except ConfigurationError as error:
        print(f'{error.code}: {error}', file=sys.stderr)
        return 1
    try:
        create_server(settings).run(transport='stdio')
    except Exception:
        # SDK lifecycle failures may be wrapped in exception groups.
        error = NetOneClientError()
        print(f'{error.code}: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
