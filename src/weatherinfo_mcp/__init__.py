"""WeatherInfo MCP - An MCP to provide access to environmental data to AI agents."""

__version__ = "0.1.0"

# Main public API
from weatherinfo_mcp.core.nws_location_service import Location

__all__ = ["Location", "__version__"]
