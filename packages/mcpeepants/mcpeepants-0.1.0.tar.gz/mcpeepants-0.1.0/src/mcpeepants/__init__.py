"""mcpeepants - Extensible MCP server with plugin support."""

__version__ = "0.1.0"

from .server import create_server, main, mcp

__all__ = ["create_server", "main", "mcp"]
