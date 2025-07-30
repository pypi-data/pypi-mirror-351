"""Simple MCP package for demonstrating Model Context Protocol."""

from simple_mcp.simple_mcp import mcp

def main() -> None:
    """Run the simple-mcp command."""
    print("Starting Simple MCP server...")
    mcp.run()
