"""Start an MCP stdio server without commercial tools."""

from mcp.server.fastmcp import FastMCP


server = FastMCP('netone-mcp')


if __name__ == '__main__':
    server.run(transport='stdio')
