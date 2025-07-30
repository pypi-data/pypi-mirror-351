"""
MCP Kubectl - A Model Context Protocol server for Kubernetes.
"""

__version__ = "1.1.0"

# Import core MCP server
from .mcp_server import MCPServer

__all__ = ["MCPServer"]
