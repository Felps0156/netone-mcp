"""Start an MCP stdio server without commercial tools."""

import sys

from mcp.server.fastmcp import FastMCP

from config import ConfigurationError, load_config


server = FastMCP('netone-mcp')


def main() -> int:
    """Validate configuration before starting the empty MCP registry."""
    try:
        load_config()
    except ConfigurationError as error:
        print(f'{error.code}: {error}', file=sys.stderr)
        return 1
    server.run(transport='stdio')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
