"""
Command-line interface for the Figma Data MCP Server.

This module provides the main entry point for the figma-mcp command
that will be available after installing the package via pip.
"""
import argparse
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from .main import mcp


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="figma-mcp",
        description="Figma Data MCP Server - Extract Figma design data for AI coding agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  figma-mcp                          # Run with stdio transport (default)
  figma-mcp --transport http         # Run with HTTP transport on port 8000
  figma-mcp --transport http --port 9000  # Run with HTTP transport on port 9000
  figma-mcp --transport sse --port 8080   # Run with SSE transport on port 8080
  figma-mcp --env-file custom.env    # Use custom environment file
  figma-mcp --debug                  # Enable debug mode

Supported transports:
  stdio           - Standard input/output (default, for MCP clients)
  http            - HTTP transport (alias for streamable-http)
  streamable-http - HTTP transport with streaming support
  sse             - Server-Sent Events transport

Environment Variables:
  FIGMA_API_KEY   - Your Figma Personal Access Token (required)
        """,
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "streamable-http", "sse"],
        default="stdio",
        help="Transport protocol to use (default: stdio)",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for HTTP-based transports (default: 8000)",
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address for HTTP-based transports (default: 127.0.0.1)",
    )
    
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to environment file (default: .env)",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.1",
    )
    
    return parser


def check_figma_api_key() -> str:
    """Check if Figma API key is available and return it."""
    figma_api_key = os.getenv("FIGMA_API_KEY")
    if not figma_api_key:
        print("ERROR: FIGMA_API_KEY environment variable not set.")
        print()
        print("To get your Figma Personal Access Token:")
        print("1. Go to Figma and log in to your account")
        print("2. Go to 'Help and account' > 'Account settings'")
        print("3. Scroll down to 'Personal access tokens'")
        print("4. Click 'Create a new personal access token'")
        print("5. Give it a name and click 'Create token'")
        print("6. Copy the token and set it in your .env file:")
        print("   FIGMA_API_KEY=your_token_here")
        print()
        sys.exit(1)
    return figma_api_key


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set debug mode if requested
    if args.debug:
        os.environ["FIGMA_MCP_DEBUG"] = "1"
    
    # Load environment variables from specified file
    if os.path.exists(args.env_file):
        load_dotenv(args.env_file)
    else:
        # Try to load from default locations
        load_dotenv()
    
    # Check for Figma API key
    figma_api_key = check_figma_api_key()
    
    # Normalize transport (http is alias for streamable-http)
    transport = args.transport
    if transport == "http":
        transport = "streamable-http"
    
    # Start the server
    try:
        if transport in ["streamable-http", "sse"]:
            print(f"Starting Figma Data MCP Server with {transport} transport on {args.host}:{args.port}")
            mcp.run(transport=transport, host=args.host, port=args.port)
        else:
            print("Starting Figma Data MCP Server on STDIO...")
            mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 