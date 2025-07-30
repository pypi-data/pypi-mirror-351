#!/usr/bin/env python3
"""
Simple CLI for the kubectl MCP server.
"""

import asyncio
import argparse
import logging
import sys
from .mcp_server import MCPServer

logger = logging.getLogger(__name__)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Kubectl MCP Server")
    parser.add_argument("command", choices=["serve"], help="Command to run")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", 
                       help="Transport method")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port for SSE transport")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    if args.command == "serve":
        asyncio.run(serve(args.transport, args.port))

async def serve(transport: str, port: int):
    """Serve the MCP server."""
    server = MCPServer("kubectl-mcp-server")
    
    if transport == "stdio":
        await server.serve_stdio()
    elif transport == "sse":
        await server.serve_sse(port)

if __name__ == "__main__":
    main()