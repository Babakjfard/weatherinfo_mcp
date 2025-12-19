"""
Entry point for the weatherinfo-mcp CLI.

This module defines the main() function, which runs the MCP server.
Calling `weatherinfo-mcp` from the command line (configured in pyproject.toml) will
invoke this main() function.
"""

from weatherinfo_mcp.core.nws_location_service import Location
from weatherinfo_mcp.mcp_tools.nws_weather_tools import mcp


def main():
    """
    Main entry point for the CLI and MCP server.
    This will start the FastMCP server and block until exit.
    """
    print("Starting WeatherInfo MCP server...")
    mcp.run()

    
if __name__ == "__main__":
    main()
