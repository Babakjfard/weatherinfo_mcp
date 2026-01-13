# WeatherInfoMCP

[![DOI](https://zenodo.org/badge/1119762721.svg)](https://doi.org/10.5281/zenodo.18227188)

An MCP (Model Context Protocol) server that provides access to environmental weather data for AI agents through the National Weather Service (NWS) API.

## Features

- 🌍 **Location Management**: Create locations from addresses or coordinates
- 🌤️ **Weather Observations**: Fetch real-time weather data from NWS stations
- 📊 **Data Extraction**: Extract specific weather metrics (temperature, humidity, wind, descriptions)
- ⚠️ **Weather Alerts**: Get active weather alerts for locations
- 🌡️ **HeatRisk Guidance**: Access HeatRisk information and CDC dashboard links

## Usage

### Using Directly from GitHub (No Installation Required) ⚡

The easiest way to use WeatherInfoMCP is directly from GitHub without cloning or installing anything locally. This method uses `uvx` (from the `uv` package manager) to automatically download, install, and run the MCP server from the repository.

**Prerequisites:**
- [uv](https://github.com/astral-sh/uv) must be installed (it provides the `uvx` command)

**How it works:**
- `uvx` automatically creates an isolated environment, installs the package from GitHub, and runs it
- No local repository clone needed
- No manual dependency management
- Always uses the latest version from the repository

#### With OpenAI Agents SDK

```python
from agents import Agent
from agents.mcp import MCPServerStdio

# Configuration for direct GitHub usage
PARAMS_WEATHER_MCP = {
    "name": "weatherinfo-mcp",
    "command": "uvx",
    "args": ["--from", "git+https://github.com/Babakjfard/weatherinfo_mcp.git", "weatherinfo-mcp"]
}

weather_server = MCPServerStdio(params=PARAMS_WEATHER_MCP)
agent = Agent(
    name="weather-agent",
    model="gpt-4",
    mcp_servers=[weather_server]
)
```

#### With Claude Desktop

Add this to your Claude Desktop configuration file (typically `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "weatherinfo-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Babakjfard/weatherinfo_mcp.git", "weatherinfo-mcp"]
    }
  }
}
```

**Benefits of this approach:**
- ✅ Zero setup - no cloning, no installation, no virtual environment management
- ✅ Always up-to-date - uses the latest version from GitHub
- ✅ Isolated - `uvx` manages dependencies in isolated environments
- ✅ Portable - works the same way on any system with `uv` installed

**Note:** The first run may take a moment as `uvx` downloads and sets up the package. Subsequent runs are faster due to caching.

### As an MCP Server

The package can be used as an MCP server with any MCP-compatible client:

```bash
python -m weatherinfo_mcp.mcp_tools.main
```

Or using the installed script:
```bash
weatherinfo-mcp
```

### With AI Agent Frameworks

#### OpenAI Agents SDK

If the package is installed in editable mode (`pip install -e .` or `uv sync`), you can use:

```python
from agents import Agent
from agents.mcp import MCPServerStdio

params = {
    "name": "weatherinfo-mcp",
    "command": "python",
    "args": ["-m", "weatherinfo_mcp.mcp_tools.main"],
    # PYTHONPATH not needed if package is installed
}

weather_server = MCPServerStdio(params=params)
agent = Agent(
    name="weather-agent",
    model="gpt-4",
    mcp_servers=[weather_server]
)
```

If the package is not installed, specify the source directory:

```python
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
params = {
    "name": "weatherinfo-mcp",
    "command": "python",
    "args": ["-m", "weatherinfo_mcp.mcp_tools.main"],
    "env": {
        "PYTHONPATH": os.path.join(project_root, "src")
    }
}
```

#### Claude Desktop Configuration

If the package is installed:

```json
{
  "mcpServers": {
    "weatherinfo-mcp": {
      "command": "python",
      "args": ["-m", "weatherinfo_mcp.mcp_tools.main"]
    }
  }
}
```

If the package is not installed, use the full path to the virtual environment Python and set PYTHONPATH:

```json
{
  "mcpServers": {
    "weatherinfo-mcp": {
      "command": "/full/path/to/project/.venv/bin/python",
      "args": ["-m", "weatherinfo_mcp.mcp_tools.main"],
      "env": {
        "PYTHONPATH": "/full/path/to/weatherinfo_mcp/src"
      }
    }
  }
}
```

**Note**: Using the virtual environment Python (`/full/path/to/project/.venv/bin/python`) ensures all dependencies are available.

## Available Tools

The MCP server provides the following tools:

1. **`create_location`** - Create a location object from an address or coordinates
2. **`get_current_observation`** - Fetch current weather observation data
3. **`get_temperature_from_observation`** - Extract temperature value (Celsius)
4. **`get_humidity_from_observation`** - Extract relative humidity (%)
5. **`get_weather_description_from_observation`** - Extract weather description
6. **`get_wind_info_from_observation`** - Extract wind speed and direction
7. **`get_alerts`** - Get active weather alerts for a location
8. **`get_HeatRisk`** - Get HeatRisk guidance and CDC dashboard information

## Prerequisites

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Internet connection (for NWS API access)

## Installation

### Using uv (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url> weatherinfo_mcp
   cd weatherinfo_mcp
   ```

2. **Install dependencies and create virtual environment:**
   ```bash
   uv sync
   ```

   This will:
   - Create a virtual environment in `.venv/`
   - Install all required dependencies
   - Install the package in editable mode

3. **Activate the virtual environment (optional, but recommended):**
   ```bash
   source .venv/bin/activate
   ```

4. **Install notebook dependencies (optional, for running example notebooks):**
   ```bash
   uv pip install -r notebooks/requirements.txt
   ```

5. **Set up Jupyter kernel (for Jupyter notebooks):**
   ```bash
   # Register the kernel with Jupyter
   .venv/bin/python -m ipykernel install --user --name=weatherinfo_mcp --display-name="Python (weatherinfo_mcp)"
   ```
   
   After this, you'll see "Python (weatherinfo_mcp)" in your Jupyter notebook kernel selector.

### Using pip

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url> weatherinfo_mcp
   cd weatherinfo_mcp
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

## Running Tests

The project includes a comprehensive test suite to verify MCP protocol compliance and functionality. Once available, use the following instructions:

### Prerequisites for Testing

Install test framework dependencies:
```bash
cd tests
make install
```

This will automatically use `uv` if available, or fall back to `pip`.

Alternatively, install manually:
```bash
# Using uv (if available)
uv pip install -r requirements-framework.txt

# Or using pip
pip install -r requirements-framework.txt
```

### Running All Tests

```bash
cd tests
make test-all
```

This will run:
- Base MCP protocol conformance tests
- WeatherInfoMCP-specific functionality tests
- MCP Inspector integration tests

### Running Specific Test Suites

```bash
# Base MCP protocol tests only
make test-base

# WeatherInfoMCP-specific tests only
make test-weatherinfo_mcp

# Session lifecycle tests
make test-lifecycle

# Error handling tests
make test-errors

# Simple stdio test
make test-stdio

# Verbose output
make test-verbose
```

### Test Reports

Test reports are saved to `tests/` directory:
- `comprehensive_conformance_report.txt` - Full test results
- `base_conformance_report.txt` - Base protocol tests
- `weatherinfo_mcp_conformance_report.txt` - Package-specific tests
- `session_lifecycle_report.txt` - Session management tests
- `error_handling_report.txt` - Error handling tests

## Configuration

The package uses the NWS API which is free and requires no API key. The service automatically handles:
- Location geocoding using geopy
- Finding nearest NWS weather stations
- Fetching real-time observations

## Development

### Project Structure

```
weatherinfo_mcp/
├── src/
│   └── weatherinfo_mcp/
│       ├── __init__.py
│       ├── core/
│       │   └── nws_location_service.py  # Location service
│       └── mcp_tools/
│           ├── main.py                  # MCP server entry point
│           └── nws_weather_tools.py     # MCP tool definitions
├── tests/                                # Test suite
│   ├── Makefile                         # Test runner
│   ├── comprehensive_stdio_tests.py     # Comprehensive tests
│   ├── test_nws_location_service.py     # Unit tests
│   ├── test_nws_weather_tools.py        # Unit tests
│   └── ...
├── notebooks/                           # Example notebooks
├── pyproject.toml                       # Package configuration
├── uv.lock                              # Dependency lock file
└── README.md                            # This file
```

### Setting Up Development Environment

1. Follow the installation steps above
2. Install additional development tools as needed:
   ```bash
   # Install common development tools (optional)
   uv pip install pytest black flake8 mypy
   # Or
   pip install pytest black flake8 mypy
   ```

### Running Individual Unit Tests

```bash
# Using pytest
pytest tests/test_nws_location_service.py -v
pytest tests/test_nws_weather_tools.py -v

# Or using Python directly
python -m pytest tests/
```

### Code Quality

```bash
# Format code (if black is installed)
black src/

# Lint code (if flake8 is installed)
flake8 src/
```

## Troubleshooting

### Virtual Environment Issues

If tests fail with "python: No such file or directory":
- Ensure you've activated the virtual environment: `source .venv/bin/activate`
- Or the Makefile will automatically detect the venv if present

### Module Import Errors

If you get import errors:
```bash
# Reinstall the package in editable mode
uv sync
# Or
pip install -e .
```

### Test Failures

If tests fail due to NWS API errors:
- Check your internet connection
- The NWS API may occasionally be unavailable (tests should handle this gracefully)
- Some test failures may be due to temporary API outages, not code issues

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Author

Babak J.Fard - babak.jfard@gmail.com

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [National Weather Service API](https://www.weather.gov/documentation/services-web-api)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)

