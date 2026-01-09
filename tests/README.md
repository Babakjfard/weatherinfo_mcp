# MCP Protocol Conformance Test Suite

The Test Suite that implements comprehensive testing based on the official MCP specification version 2025-06-18. The test suite provides full validation of MCP protocol compliance and WeatherInfoMCP-specific functionality.

## Current Status

- ✅ **Complete Framework**: Full test suite with comprehensive architecture
- ✅ **MCP Specification 2025-06-18**: Official specification implementation
- ✅ **JSON-RPC 2.0 Compliance**: Complete JSON-RPC 2.0 testing
- ✅ **Tool Manifest Validation**: Comprehensive tool validation
- ✅ **Session Lifecycle**: Complete session management testing
- ✅ **Tool Execution**: Full tool execution compliance testing
- ✅ **WeatherInfoMCP-Specific Tests**: All WeatherInfoMCP tools validated

## Test Coverage

This conformance test suite covers:

1. **MCP Protocol Compliance**: Tests against MCP specification version 2025-06-18
2. **JSON-RPC 2.0 Compliance**: Standard JSON-RPC 2.0 validation
3. **Session Management**: Session initialization, lifecycle, and termination
4. **Tool Manifest Validation**: Tool structure, metadata, and schema validation
5. **Tool Execution**: Parameter validation, response structure, and execution correctness
6. **Error Handling**: Error codes, error messages, and recovery mechanisms
7. **WeatherInfoMCP Tools**: Validation of all 8 WeatherInfoMCP tools (create_location, get_current_observation, get_temperature_from_observation, get_humidity_from_observation, get_weather_description_from_observation, get_wind_info_from_observation, get_alerts, get_HeatRisk)
8. **Unit Tests**: Isolated testing of core Location service and tool functions

## Test Suite Components

The test suite consists of several test modules:

### Main Test Files

- **`comprehensive_stdio_tests.py`**: Main conformance test suite for stdio-based MCP servers
  - Base MCP protocol tests
  - WeatherInfoMCP-specific functionality tests
  - MCP Inspector integration tests
- **`test_session_lifecycle.py`**: Specialized, detailed session lifecycle tests (7 tests covering handshake, version negotiation, state transitions, termination, timeouts). More comprehensive than the basic connection test in `comprehensive_stdio_tests.py`
- **`test_error_handling.py`**: Specialized, detailed error handling tests (10 tests covering error structure, message clarity, method not found, invalid params, validation errors, API errors, stability, retry logic, timeouts, cancellation). Not covered by `comprehensive_stdio_tests.py`
- **`simple_stdio_test.py`**: Simple diagnostic script for quick server connectivity check (largely superseded by `comprehensive_stdio_tests.py`, but useful for quick diagnostics)
- **`stdio_mcp_conformance_framework.py`**: Basic conformance framework with 4 core tests (connection, tool manifest, tool execution, session lifecycle). Can be run independently, but largely superseded by `comprehensive_stdio_tests.py`

### Unit Tests

- **`test_nws_location_service.py`**: Unit tests for the `Location` class using `unittest`
- **`test_nws_weather_tools.py`**: Unit tests for MCP tool functions using `unittest`

### Test Framework Features

- **Connection Testing**: Server reachability and initialization
- **JSON-RPC Compliance**: Standard JSON-RPC 2.0 validation
- **Tool Manifest Validation**: Tool structure and metadata validation
- **Error Handling**: Comprehensive error testing framework
- **Reporting**: Detailed test reports with MCP spec section mapping

### Key Features

- **Async/Await Support**: Full async testing capabilities
- **Schema Validation**: JSON schema validation for all messages
- **Detailed Reporting**: Comprehensive test reports with timing and details
- **Extensible Design**: Easy to add new test cases once spec is available
- **CI/CD Compatible**: Tests can be integrated into CI/CD pipelines (JUnit XML output supported)

## Installation

### Prerequisites

First, ensure the main package is installed (see main [README.md](../README.md)):

```bash
cd ..  # Go to project root
uv sync  # Install package and dependencies
```

### Install Test Framework Dependencies

```bash
# Using Makefile (recommended)
make install

# Or manually using uv
uv pip install -r requirements-framework.txt

# Or using pip
pip install -r requirements-framework.txt
```

## Usage

### Running Tests

The easiest way to run tests is using the Makefile:

```bash
# Run all tests
make test-all

# Run specific test suites
make test-base              # Base MCP protocol tests
make test-weatherinfo_mcp   # WeatherInfoMCP-specific tests
make test-inspector         # MCP Inspector tests
make test-lifecycle         # Session lifecycle tests
make test-errors           # Error handling tests
make test-stdio            # Simple stdio test

# Verbose output
make test-verbose
```

### Manual Test Execution

You can also run tests directly using Python. First, navigate to the `tests/` directory and activate the virtual environment:

```bash
cd tests
source ../.venv/bin/activate  # On Windows: ..\.venv\Scripts\activate
```

Then run tests with `python`:

```bash
# Comprehensive tests
python comprehensive_stdio_tests.py --test-type all --output ../test_results/comprehensive_conformance_report.txt

# Session lifecycle tests
python test_session_lifecycle.py --output ../test_results/session_lifecycle_report.txt

# Error handling tests
python test_error_handling.py --output ../test_results/error_handling_report.txt

# Simple diagnostic test (no output file needed)
python simple_stdio_test.py
```

**Note:** If the virtual environment is not activated, you can use the full path: `../.venv/bin/python` instead of `python`.

### Command Line Options

**`comprehensive_stdio_tests.py`** supports:
- `--test-type`: Test category (`base`, `weatherinfo_mcp`, `inspector`, `all`)
- `--timeout`: Request timeout in seconds (default: 30)
- `--output`: Output file path for test report (recommended: `../test_results/filename.txt`)
- `--verbose`: Enable verbose logging
- `--server-command`: Command to start the MCP server (optional, uses venv Python by default)
- `--server-args`: Arguments to pass to the server (optional)
- `--server-cwd`: Working directory for the server (optional)

**`test_session_lifecycle.py`** and **`test_error_handling.py`** support:
- `--timeout`: Request timeout in seconds (default: 30)
- `--output`: Output file path for test report
- `--verbose`: Enable verbose logging
- `--server-command`: Command to start the MCP server (optional, uses venv Python by default)
- `--server-args`: Arguments to pass to the server (optional)
- `--server-cwd`: Working directory for the server (optional)

### Running Unit Tests

The unit tests use Python's standard `unittest` framework. Run from the `tests/` directory:

```bash
# Run all unit tests using pytest
cd tests
pytest test_nws_location_service.py test_nws_weather_tools.py -v

# Or using unittest directly
python -m unittest test_nws_location_service test_nws_weather_tools

# Or from project root
pytest tests/test_nws_location_service.py tests/test_nws_weather_tools.py -v
```

### Test Reports

Test reports are saved to the `test_results/` directory (one level up from `tests/`):
- `comprehensive_conformance_report.txt` - Full test results (all test categories)
- `base_conformance_report.txt` - Base MCP protocol tests
- `weatherinfo_mcp_conformance_report.txt` - WeatherInfoMCP-specific tests
- `inspector_conformance_report.txt` - MCP Inspector integration tests
- `session_lifecycle_report.txt` - Session management and protocol version tests
- `error_handling_report.txt` - Error handling and recovery tests

The `test_results/` directory is created automatically when running tests via the Makefile.

## Test Categories by Test File

### `comprehensive_stdio_tests.py` - Main Conformance Tests

**Base MCP Protocol Tests** (`--test-type base`):
- Connection and initialization: Validates server connection, initialization handshake, and required fields (protocolVersion, capabilities, serverInfo)
- Tool manifest compliance: Validates tool structure, metadata, and schemas (name, description, inputSchema)
- Tool execution compliance: Tests tool execution with parameter validation and response structure validation

**Note:** These tests validate MCP protocol compliance through the stdio transport layer, which uses JSON-RPC 2.0 for communication. Explicit JSON-RPC 2.0 compliance testing (batch requests, content-type validation, etc.) is covered in the specialized `test_error_handling.py` suite.

**WeatherInfoMCP-Specific Tests** (`--test-type weatherinfo_mcp`):
- Tool availability validation: Verifies all 8 expected WeatherInfoMCP tools are present
- Location creation functionality: Tests `create_location` tool with address input and validates returned location data structure (address, latitude, longitude, station_url)
- Weather observation retrieval: Tests `get_current_observation` tool by creating a location first, then fetching and validating observation data structure

**MCP Inspector Tests** (`--test-type inspector`):
- Inspector tool availability
- Inspector integration validation

### `test_session_lifecycle.py` - Session Lifecycle Tests

- Session initialization handshake
- Protocol version negotiation
- Capability negotiation
- Session state transitions
- Pre-initialization request rejection
- Session termination and cleanup
- Timeout and keepalive handling

### `test_error_handling.py` - Error Handling Tests

- Error response structure compliance
- Error message clarity
- Method not found errors
- Invalid parameters errors
- Validation error handling
- External API error handling
- Server stability after errors
- Retry logic support
- Timeout and cancellation handling

### `test_nws_location_service.py` & `test_nws_weather_tools.py` - Unit Tests

- Isolated testing of Location class functionality
- Isolated testing of tool functions without MCP layer
- Mock-based testing for external API dependencies

## Test Suite Structure

```
tests/
├── comprehensive_stdio_tests.py          # Main conformance test suite
├── test_session_lifecycle.py            # Session lifecycle tests
├── test_error_handling.py               # Error handling tests
├── simple_stdio_test.py                 # Simple diagnostic test
├── stdio_mcp_conformance_framework.py   # Basic framework (4 core tests, largely superseded)
├── test_nws_location_service.py         # Unit tests (unittest)
├── test_nws_weather_tools.py            # Unit tests (unittest)
├── Makefile                             # Test runner automation
└── requirements-framework.txt           # Test dependencies

test_results/                             # Test reports (created automatically)
├── comprehensive_conformance_report.txt
├── base_conformance_report.txt
├── weatherinfo_mcp_conformance_report.txt
├── inspector_conformance_report.txt
├── session_lifecycle_report.txt
└── error_handling_report.txt
```

## Integration with Official Specification

The test suite is based on the MCP specification version 2025-06-18 and validates protocol compliance through:
- MCP Python SDK implementation patterns
- JSON-RPC 2.0 standards
- Observable MCP protocol behavior
- FastMCP framework conventions

## Development Workflow

1. **Framework Development**: ✅ Complete
2. **Test Implementation**: ✅ Complete - Tests implemented based on MCP 2025-06-18 specification
3. **Validation and Testing**: ✅ Complete - Comprehensive test coverage for protocol compliance
4. **Documentation**: ✅ Complete - Framework and test documentation available

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-06-18) (Official - needs access)
- [MCP Inspector Tool](https://modelcontextprotocol.io/docs/tools/inspector) (Official - needs access)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [WeatherInfoMCP Documentation](../README.md)

## License

MIT License - See LICENSE file for details.

## Support

For questions about this framework or MCP conformance testing, please:

1. Check the official MCP specification (when available)
2. Review the framework documentation
3. Submit issues or questions to the project repository

---

**Framework Version**: 1.0.0  
**Last Updated**: 2025-10-23  
**Status**: ✅ Framework Complete - Testing MCP specification version 2025-06-18  
**MCP Specification**: https://modelcontextprotocol.io/specification/2025-06-18