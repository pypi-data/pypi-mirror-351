"""
Challenge MCP - A Model Context Protocol server for challenge management.

This package provides a FastMCP server with authentication for managing challenges,
participants, and related data through a REST API.
"""

__version__ = "0.1.0"
__author__ = "Challenge MCP Team"
__email__ = "team@challenge-mcp.com"

from .server import mcp, AppContext
from .authfastmcp import AuthFastMCP

__all__ = [
    "mcp",
    "AppContext",
    "AuthFastMCP",
    "__version__",
    "__author__",
    "__email__",
]
