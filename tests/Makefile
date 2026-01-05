# MCP Protocol Conformance Test Suite Makefile
#
# This Makefile provides convenient targets for running the comprehensive
# MCP protocol conformance test suite with stdio transport.

# Use Python from the parent directory's virtual environment (portable, works on any system)
# Priority: 1) Parent .venv 2) Activated venv (if VIRTUAL_ENV set) 3) python3 from PATH 4) python from PATH
PYTHON := $(shell if [ -f "../.venv/bin/python" ]; then echo "../.venv/bin/python"; \
	elif [ -n "$$VIRTUAL_ENV" ] && [ -f "$$VIRTUAL_ENV/bin/python" ]; then echo "$$VIRTUAL_ENV/bin/python"; \
	elif command -v python3 >/dev/null 2>&1; then echo "python3"; \
	else echo "python"; fi)

# Test results directory (one level up from tests/)
TEST_RESULTS_DIR := ../test_results

.PHONY: help install ensure-test-results-dir test test-base test-weatherinfo_mcp test-inspector test-all test-verbose test-lifecycle test-errors clean

# Default target
help:
	@echo "MCP Protocol Conformance Test Suite"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install         - Install test suite dependencies"
	@echo "  test            - Run all conformance tests (default)"
	@echo "  test-base       - Run base MCP protocol conformance tests"
	@echo "  test-weatherinfo_mcp    - Run WeatherInfo_MCP-specific conformance tests"
	@echo "  test-inspector  - Run MCP Inspector integration tests"
	@echo "  test-all        - Run all tests (base + WeatherInfo_MCP + Inspector)"
	@echo "  test-verbose    - Run tests with verbose output"
	@echo "  test-stdio       - Run simple stdio-based test"
	@echo "  test-lifecycle   - Run session lifecycle and protocol version tests"
	@echo "  test-errors      - Run error handling and recovery tests"
	@echo "  clean           - Clean up generated files"
	@echo ""
	@echo "Environment variables:"
	@echo "  OUTPUT_FILE     - Output file for test report (default: comprehensive_conformance_report.txt)"
	@echo "  VERBOSE         - Enable verbose logging (set to any value)"
	@echo ""
	@echo "Examples:"
	@echo "  make test                 # Run all tests"
	@echo "  make test-base            # Run base MCP protocol tests"
	@echo "  make test-weatherinfo_mcp         # Run WeatherInfo_MCP-specific tests"
	@echo "  make test-inspector       # Run MCP Inspector tests"
	@echo "  make test-all             # Run all comprehensive tests"
	@echo "  make test-verbose          # Run with verbose output"
	@echo "  make test-lifecycle        # Run session lifecycle tests"
	@echo "  make test-errors           # Run error handling tests"
	@echo "  make clean                # Clean up generated files"

# Install dependencies
# Try uv first, fall back to pip if uv is not available
install:
	@echo "Installing MCP conformance framework dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "Using uv..."; \
		uv pip install -r requirements-framework.txt; \
	else \
		echo "Using pip..."; \
		$(PYTHON) -m pip install -r requirements-framework.txt; \
	fi

# Ensure test results directory exists
ensure-test-results-dir:
	@mkdir -p $(TEST_RESULTS_DIR)

# Run all conformance tests (default)
test: ensure-test-results-dir test-all

# Run base MCP protocol conformance tests
test-base: ensure-test-results-dir
	@echo "Running base MCP protocol conformance tests (stdio-based)..."
	@echo ""
	$(PYTHON) comprehensive_stdio_tests.py --test-type base --output $(TEST_RESULTS_DIR)/base_conformance_report.txt

# Run WeatherInfo_MCP-specific conformance tests
test-weatherinfo_mcp: ensure-test-results-dir
	@echo "Running WeatherInfo_MCP-specific conformance tests (stdio-based)..."
	@echo ""
	$(PYTHON) comprehensive_stdio_tests.py --test-type weatherinfo_mcp --output $(TEST_RESULTS_DIR)/weatherinfo_mcp_conformance_report.txt

# Run MCP Inspector integration tests
test-inspector: ensure-test-results-dir
	@echo "Running MCP Inspector integration tests (stdio-based)..."
	@echo ""
	$(PYTHON) comprehensive_stdio_tests.py --test-type inspector --output $(TEST_RESULTS_DIR)/inspector_conformance_report.txt

# Run all tests (base + WeatherInfo_MCP + Inspector)
test-all: ensure-test-results-dir
	@echo "Running all MCP conformance tests (stdio-based)..."
	@echo ""
	$(PYTHON) comprehensive_stdio_tests.py \
		--test-type all \
		--output $(TEST_RESULTS_DIR)/$(or $(OUTPUT_FILE),comprehensive_conformance_report.txt)

# Run tests with verbose output
test-verbose: ensure-test-results-dir
	@echo "Running MCP conformance tests with verbose output..."
	@echo ""
	$(PYTHON) comprehensive_stdio_tests.py \
		--test-type all \
		--verbose \
		--output $(TEST_RESULTS_DIR)/$(or $(OUTPUT_FILE),comprehensive_conformance_report.txt)

# Run simple stdio test
test-stdio:
	@echo "Running simple stdio-based test..."
	@echo ""
	$(PYTHON) simple_stdio_test.py

# Run session lifecycle and protocol version tests
test-lifecycle: ensure-test-results-dir
	@echo "Running MCP Session Lifecycle and Protocol Version Negotiation tests..."
	@echo ""
	$(PYTHON) test_session_lifecycle.py \
		--output $(TEST_RESULTS_DIR)/session_lifecycle_report.txt

# Run error handling and recovery tests
test-errors: ensure-test-results-dir
	@echo "Running MCP Error Handling and Recovery tests..."
	@echo ""
	$(PYTHON) test_error_handling.py \
		--output $(TEST_RESULTS_DIR)/error_handling_report.txt

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	rm -f $(TEST_RESULTS_DIR)/*_conformance_report.txt
	rm -f $(TEST_RESULTS_DIR)/*_lifecycle_report.txt
	rm -f $(TEST_RESULTS_DIR)/*_handling_report.txt
	rm -f $(TEST_RESULTS_DIR)/comprehensive_conformance_report.txt
	rm -f $(TEST_RESULTS_DIR)/*.log
	rm -f *_conformance_report.txt
	rm -f *_lifecycle_report.txt
	rm -f *_handling_report.txt
	rm -f comprehensive_conformance_report.txt
	rm -f *.log
	rm -rf __pycache__
	rm -rf .pytest_cache
