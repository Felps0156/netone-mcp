"""Start the bounded read-only MCP stdio server with safe diagnostics."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
import sys

from mcp.server.fastmcp import FastMCP

from client import NetOneClient, NetOneClientError
from config import ConfigurationError, Settings, load_config
from mcp_tools import NetOneMCP


class _SafeDiagnosticFormatter(logging.Formatter):
    """Keep diagnostic identity without rendering untrusted log contents."""

    def format(self, record: logging.LogRecord) -> str:
        component = next((
            name for name in ('mcp', 'httpx', 'httpcore')
            if record.name == name or record.name.startswith(name + '.')
        ), 'library')
        level = {
            logging.DEBUG: 'DEBUG', logging.INFO: 'INFO',
            logging.WARNING: 'WARNING', logging.ERROR: 'ERROR',
            logging.CRITICAL: 'CRITICAL',
        }.get(record.levelno, 'UNKNOWN')
        return (
            f'level={level} component={component} '
            f'code={component}_diagnostic'
        )


def _configure_safe_logging(level: str) -> None:
    """Own stderr logging, including SDK calls to the root logger."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_SafeDiagnosticFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
    names = {'mcp', 'httpx', 'httpcore'}
    names.update(
        name for name in logging.Logger.manager.loggerDict
        if name.startswith(('mcp.', 'httpx.', 'httpcore.'))
    )
    for name in names:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.disabled = False
        logger.propagate = True
        logger.setLevel(logging.NOTSET)


def create_server(settings: Settings) -> FastMCP:
    """Bind one process-owned client to the approved stdio tool registry."""
    _configure_safe_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastMCP) -> AsyncIterator[dict[str, NetOneClient]]:
        async with NetOneClient(settings) as client:
            yield {'netone_client': client}

    return NetOneMCP(
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
