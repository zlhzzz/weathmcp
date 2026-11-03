#!/usr/bin/env python3
"""
Demo entry point for weathmcp MCP server.
Usage: python demo.py
Runs the FastMCP server in stdio mode for quick testing.
"""
from server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
