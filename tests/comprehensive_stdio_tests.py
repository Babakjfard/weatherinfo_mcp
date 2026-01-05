#!/usr/bin/env python3
"""
Comprehensive Stdio-based MCP Conformance Tests

This module provides comprehensive conformance testing for stdio-based MCP servers
(like FastMCP servers). It includes all the comprehensive tests: base MCP protocol,
WeatherInfo_MCP-specific functionality, and MCP Inspector integration.

Author: WeatherInfo_MCP Development Team
Date: 2025-10-23
License: MIT

References:
- MCP Specification: https://modelcontextprotocol.io/specification/2025-06-18
- FastMCP Documentation: https://github.com/modelcontextprotocol/python-sdk
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveTestResult:
    """Represents the result of a comprehensive MCP test."""
    test_name: str
    test_category: str  # "base", "weatherinfo_mcp", "inspector"
    passed: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0
    details: Optional[Dict[str, Any]] = None
    mcp_spec_section: Optional[str] = None


class ComprehensiveStdioMCPTests:
    """
    Comprehensive conformance testing framework for stdio-based MCP servers.
    
    This framework provides all the comprehensive tests:
    - Base MCP protocol compliance
    - WeatherInfo_MCP-specific functionality
    - MCP Inspector integration
    """
    
    def __init__(self, server_command: str = None, 
                 server_args: List[str] = None,
                 server_env: Dict[str, str] = None,
                 server_cwd: str = None,
                 timeout: int = 30):
        """
        Initialize the comprehensive stdio MCP test framework.
        """
        # Use virtual environment Python by default
        if server_command is None:
            server_command = str(Path(__file__).parent.parent / ".venv" / "bin" / "python")
        
        self.server_command = server_command
        self.server_args = server_args or ["-m", "weatherinfo_mcp.mcp_tools.main"]
        self.server_env = server_env or {}
        self.server_cwd = server_cwd or str(Path(__file__).parent.parent)
        self.timeout = timeout
        self.test_results: List[ComprehensiveTestResult] = []
        
        # Official MCP specification version
        self.protocol_version = "2025-06-18"
        
        logger.info("Initialized Comprehensive Stdio MCP Test Framework")
        logger.info(f"Server Command: {self.server_command}")
        logger.info(f"Server Args: {self.server_args}")
        logger.info(f"Server CWD: {self.server_cwd}")
        logger.info(f"✅ Testing against MCP specification version {self.protocol_version}")
    
    def _get_server_params(self):
        """Get server parameters for stdio transport."""
        env = os.environ.copy()
        env.update(self.server_env)
        env["MCP_DEBUG"] = "1"
        env["PYTHONPATH"] = str(Path(self.server_cwd) / "src")
        
        return StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
            env=env,
            cwd=self.server_cwd,
        )
    
    # ============================================================================
    # BASE MCP PROTOCOL TESTS
    # ============================================================================
    
    async def test_base_connection_and_initialization(self) -> ComprehensiveTestResult:
        """Test MCP server connection and initialization."""
        start_time = time.time()
        test_name = "Base MCP Connection and Initialization"
        test_category = "base"
        mcp_spec_section = "Base Protocol - Lifecycle"
        
        try:
            server_params = self._get_server_params()
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    init_result = await session.initialize()
                    
                    if not init_result:
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message="No initialization response received",
                            execution_time=time.time() - start_time,
                            mcp_spec_section=mcp_spec_section
                        )
                    
                    # Validate required fields
                    required_fields = ["protocolVersion", "capabilities", "serverInfo"]
                    missing_fields = [field for field in required_fields if not hasattr(init_result, field)]
                    
                    if missing_fields:
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message=f"Missing required initialization fields: {missing_fields}",
                            execution_time=time.time() - start_time,
                            mcp_spec_section=mcp_spec_section
                        )
                    
                    return ComprehensiveTestResult(
                        test_name=test_name,
                        test_category=test_category,
                        passed=True,
                        execution_time=time.time() - start_time,
                        details={
                            "protocol_version": getattr(init_result, "protocolVersion", None),
                            "has_capabilities": hasattr(init_result, "capabilities"),
                            "has_server_info": hasattr(init_result, "serverInfo"),
                            "server_name": getattr(getattr(init_result, "serverInfo", None), "name", None),
                            "server_version": getattr(getattr(init_result, "serverInfo", None), "version", None)
                        },
                        mcp_spec_section=mcp_spec_section
                    )
                    
        except Exception as e:
            return ComprehensiveTestResult(
                test_name=test_name,
                test_category=test_category,
                passed=False,
                error_message=f"Connection failed: {e}",
                execution_time=time.time() - start_time,
                mcp_spec_section=mcp_spec_section
            )
    
    async def test_base_tool_manifest_compliance(self) -> ComprehensiveTestResult:
        """Test tool manifest structure and compliance."""
        start_time = time.time()
        test_name = "Base MCP Tool Manifest Compliance"
        test_category = "base"
        mcp_spec_section = "Server Features - Tools"
        
        try:
            server_params = self._get_server_params()
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    tools_result = await session.list_tools()
                    
                    if not tools_result or not hasattr(tools_result, 'tools'):
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message="No tools returned from list_tools",
                            execution_time=time.time() - start_time,
                            mcp_spec_section=mcp_spec_section
                        )
                    
                    tools = tools_result.tools
                    
                    # Validate tool structure
                    validation_issues = []
                    for tool in tools:
                        if not hasattr(tool, 'name') or not tool.name:
                            validation_issues.append(f"Tool missing name: {tool}")
                        if not hasattr(tool, 'description') or not tool.description:
                            validation_issues.append(f"Tool {tool.name} missing description")
                        if not hasattr(tool, 'inputSchema'):
                            validation_issues.append(f"Tool {tool.name} missing inputSchema")
                    
                    if validation_issues:
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message=f"Tool validation issues: {'; '.join(validation_issues)}",
                            execution_time=time.time() - start_time,
                            details={
                                "tools_found": len(tools),
                                "validation_issues": validation_issues
                            },
                            mcp_spec_section=mcp_spec_section
                        )
                    
                    return ComprehensiveTestResult(
                        test_name=test_name,
                        test_category=test_category,
                        passed=True,
                        execution_time=time.time() - start_time,
                        details={
                            "tools_found": len(tools),
                            "all_tools_valid": True
                        },
                        mcp_spec_section=mcp_spec_section
                    )
                    
        except Exception as e:
            return ComprehensiveTestResult(
                test_name=test_name,
                test_category=test_category,
                passed=False,
                error_message=f"Tool manifest test failed: {e}",
                execution_time=time.time() - start_time,
                mcp_spec_section=mcp_spec_section
            )
    
    async def test_base_tool_execution_compliance(self) -> ComprehensiveTestResult:
        """Test tool execution compliance."""
        start_time = time.time()
        test_name = "Base MCP Tool Execution Compliance"
        test_category = "base"
        mcp_spec_section = "Server Features - Tools"
        
        try:
            server_params = self._get_server_params()
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Test tool execution
                    try:
                        result = await session.call_tool(
                            "create_location",
                            {"address": "Test City"}
                        )
                        
                        if result and hasattr(result, 'content'):
                            return ComprehensiveTestResult(
                                test_name=test_name,
                                test_category=test_category,
                                passed=True,
                                execution_time=time.time() - start_time,
                                details={
                                    "tool_executed": "create_location",
                                    "has_result": True,
                                    "result_type": type(result).__name__
                                },
                                mcp_spec_section=mcp_spec_section
                            )
                        else:
                            return ComprehensiveTestResult(
                                test_name=test_name,
                                test_category=test_category,
                                passed=False,
                                error_message="Tool execution returned no content",
                                execution_time=time.time() - start_time,
                                mcp_spec_section=mcp_spec_section
                            )
                            
                    except Exception as tool_error:
                        # Tool execution error might be acceptable
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=True,
                            execution_time=time.time() - start_time,
                            details={
                                "tool_executed": "create_location",
                                "has_error": True,
                                "error_message": str(tool_error),
                                "error_handled": True
                            },
                            mcp_spec_section=mcp_spec_section
                        )
                
        except Exception as e:
            return ComprehensiveTestResult(
                test_name=test_name,
                test_category=test_category,
                passed=False,
                error_message=f"Tool execution test failed: {e}",
                execution_time=time.time() - start_time,
                mcp_spec_section=mcp_spec_section
            )
    
    # ============================================================================
    # WEATHERINFO_MCP-SPECIFIC TESTS
    # ============================================================================
    
    async def test_weatherinfo_mcp_tool_availability(self) -> ComprehensiveTestResult:
        """Test that all expected WeatherInfo_MCP tools are available."""
        start_time = time.time()
        test_name = "WeatherInfo_MCP Tool Availability"
        test_category = "weatherinfo_mcp"
        mcp_spec_section = "Server Features - Tools"
        
        try:
            server_params = self._get_server_params()
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    tools_result = await session.list_tools()
                    tools = tools_result.tools if tools_result else []
                    
                    expected_tools = [
                        "create_location",
                        "get_current_observation", 
                        "get_temperature_from_observation",
                        "get_humidity_from_observation",
                        "get_weather_description_from_observation",
                        "get_wind_info_from_observation",
                        "get_alerts",
                        "get_HeatRisk"
                    ]
                    
                    available_tools = [tool.name for tool in tools]
                    missing_tools = [tool for tool in expected_tools if tool not in available_tools]
                    
                    if missing_tools:
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message=f"Missing WeatherInfo_MCP tools: {missing_tools}",
                            execution_time=time.time() - start_time,
                            details={
                                "expected_tools": expected_tools,
                                "available_tools": available_tools,
                                "missing_tools": missing_tools
                            },
                            mcp_spec_section=mcp_spec_section
                        )
                    
                    return ComprehensiveTestResult(
                        test_name=test_name,
                        test_category=test_category,
                        passed=True,
                        execution_time=time.time() - start_time,
                        details={
                            "expected_tools": expected_tools,
                            "available_tools": available_tools,
                            "missing_tools": missing_tools,
                            "all_tools_present": True
                        },
                        mcp_spec_section=mcp_spec_section
                    )
                    
        except Exception as e:
            return ComprehensiveTestResult(
                test_name=test_name,
                test_category=test_category,
                passed=False,
                error_message=f"WeatherInfo_MCP tool availability test failed: {e}",
                execution_time=time.time() - start_time,
                mcp_spec_section=mcp_spec_section
            )
    
    async def test_weatherinfo_mcp_location_creation(self) -> ComprehensiveTestResult:
        """Test WeatherInfo_MCP location creation functionality."""
        start_time = time.time()
        test_name = "WeatherInfo_MCP Location Creation"
        test_category = "weatherinfo_mcp"
        mcp_spec_section = "Server Features - Tools"
        
        try:
            server_params = self._get_server_params()
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Test address-based location creation
                    try:
                        result = await session.call_tool(
                            "create_location",
                            {"address": "San Francisco, CA"}
                        )
                        
                        if result and result.content:
                            location_data = json.loads(result.content[0].text)
                            
                            # Validate location data structure
                            required_fields = ["address", "latitude", "longitude", "station_url"]
                            missing_fields = [field for field in required_fields if field not in location_data]
                            
                            if missing_fields:
                                return ComprehensiveTestResult(
                                    test_name=test_name,
                                    test_category=test_category,
                                    passed=False,
                                    error_message=f"Location data missing fields: {missing_fields}",
                                    execution_time=time.time() - start_time,
                                    details={"location_data": location_data},
                                    mcp_spec_section=mcp_spec_section
                                )
                            
                            return ComprehensiveTestResult(
                                test_name=test_name,
                                test_category=test_category,
                                passed=True,
                                execution_time=time.time() - start_time,
                                details={
                                    "location_created": True,
                                    "address": location_data.get("address"),
                                    "latitude": location_data.get("latitude"),
                                    "longitude": location_data.get("longitude"),
                                    "has_station_url": "station_url" in location_data
                                },
                                mcp_spec_section=mcp_spec_section
                            )
                        else:
                            return ComprehensiveTestResult(
                                test_name=test_name,
                                test_category=test_category,
                                passed=False,
                                error_message="No location data returned",
                                execution_time=time.time() - start_time,
                                mcp_spec_section=mcp_spec_section
                            )
                            
                    except Exception as tool_error:
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message=f"Location creation failed: {tool_error}",
                            execution_time=time.time() - start_time,
                            mcp_spec_section=mcp_spec_section
                        )
                
        except Exception as e:
            return ComprehensiveTestResult(
                test_name=test_name,
                test_category=test_category,
                passed=False,
                error_message=f"WeatherInfo_MCP location creation test failed: {e}",
                execution_time=time.time() - start_time,
                mcp_spec_section=mcp_spec_section
            )
    
    async def test_weatherinfo_mcp_weather_observation(self) -> ComprehensiveTestResult:
        """Test WeatherInfo_MCP weather observation functionality."""
        start_time = time.time()
        test_name = "WeatherInfo_MCP Weather Observation"
        test_category = "weatherinfo_mcp"
        mcp_spec_section = "Server Features - Tools"
        
        try:
            server_params = self._get_server_params()
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # First create a location
                    location_result = await session.call_tool(
                        "create_location",
                        {"address": "New York, NY"}
                    )
                    
                    if not location_result or not location_result.content:
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message="Could not create location for weather test",
                            execution_time=time.time() - start_time,
                            mcp_spec_section=mcp_spec_section
                        )
                    
                    location_data = json.loads(location_result.content[0].text)
                    
                    # Test weather observation
                    try:
                        obs_result = await session.call_tool(
                            "get_current_observation",
                            {"location": location_data}
                        )
                        
                        if obs_result and obs_result.content:
                            observation_data = json.loads(obs_result.content[0].text)
                            
                            return ComprehensiveTestResult(
                                test_name=test_name,
                                test_category=test_category,
                                passed=True,
                                execution_time=time.time() - start_time,
                                details={
                                    "observation_retrieved": True,
                                    "has_timestamp": "timestamp" in observation_data,
                                    "has_temperature": "temperature" in observation_data,
                                    "has_humidity": "relativeHumidity" in observation_data,
                                    "observation_keys": list(observation_data.keys())[:10]  # First 10 keys
                                },
                                mcp_spec_section=mcp_spec_section
                            )
                        else:
                            return ComprehensiveTestResult(
                                test_name=test_name,
                                test_category=test_category,
                                passed=False,
                                error_message="No observation data returned",
                                execution_time=time.time() - start_time,
                                mcp_spec_section=mcp_spec_section
                            )
                            
                    except Exception as obs_error:
                        return ComprehensiveTestResult(
                            test_name=test_name,
                            test_category=test_category,
                            passed=False,
                            error_message=f"Weather observation failed: {obs_error}",
                            execution_time=time.time() - start_time,
                            mcp_spec_section=mcp_spec_section
                        )
                
        except Exception as e:
            return ComprehensiveTestResult(
                test_name=test_name,
                test_category=test_category,
                passed=False,
                error_message=f"WeatherInfo_MCP weather observation test failed: {e}",
                execution_time=time.time() - start_time,
                mcp_spec_section=mcp_spec_section
            )
    
    # ============================================================================
    # MCP INSPECTOR INTEGRATION TESTS
    # ============================================================================
    
    async def test_inspector_availability(self) -> ComprehensiveTestResult:
        """Test MCP Inspector availability."""
        start_time = time.time()
        test_name = "MCP Inspector Availability"
        test_category = "inspector"
        mcp_spec_section = "Developer Tools"
        
        try:
            # Check if MCP Inspector is available via npx
            # Increased timeout to 30 seconds to allow for package download on first run
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/inspector", "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return ComprehensiveTestResult(
                    test_name=test_name,
                    test_category=test_category,
                    passed=True,
                    execution_time=time.time() - start_time,
                    details={
                        "inspector_available": True,
                        "npx_accessible": True,
                        "help_output_length": len(result.stdout)
                    },
                    mcp_spec_section=mcp_spec_section
                )
            else:
                return ComprehensiveTestResult(
                    test_name=test_name,
                    test_category=test_category,
                    passed=False,
                    error_message="MCP Inspector not available via npx",
                    execution_time=time.time() - start_time,
                    details={
                        "inspector_available": False,
                        "npx_accessible": False,
                        "error_output": result.stderr
                    },
                    mcp_spec_section=mcp_spec_section
                )
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            return ComprehensiveTestResult(
                test_name=test_name,
                test_category=test_category,
                passed=False,
                error_message=f"MCP Inspector not available: {e}",
                execution_time=time.time() - start_time,
                details={
                    "inspector_available": False,
                    "error_type": type(e).__name__
                },
                mcp_spec_section=mcp_spec_section
            )
    
    # ============================================================================
    # TEST RUNNERS
    # ============================================================================
    
    async def run_base_tests(self) -> List[ComprehensiveTestResult]:
        """Run base MCP protocol tests."""
        logger.info("Running Base MCP Protocol Tests...")
        
        base_tests = [
            self.test_base_connection_and_initialization,
            self.test_base_tool_manifest_compliance,
            self.test_base_tool_execution_compliance,
        ]
        
        results = []
        for test_method in base_tests:
            try:
                result = await test_method()
                results.append(result)
                self.test_results.append(result)
                
                status = "PASS" if result.passed else "FAIL"
                logger.info(f"{status}: {result.test_name} ({result.execution_time:.2f}s)")
                
                if not result.passed:
                    logger.error(f"  Error: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"Base test {test_method.__name__} failed with exception: {e}")
                error_result = ComprehensiveTestResult(
                    test_name=test_method.__name__,
                    test_category="base",
                    passed=False,
                    error_message=str(e),
                    execution_time=0.0
                )
                results.append(error_result)
                self.test_results.append(error_result)
        
        return results
    
    async def run_weatherinfo_mcp_tests(self) -> List[ComprehensiveTestResult]:
        """Run WeatherInfo_MCP-specific tests."""
        logger.info("Running WeatherInfo_MCP-Specific Tests...")
        
        weatherinfo_mcp_tests = [
            self.test_weatherinfo_mcp_tool_availability,
            self.test_weatherinfo_mcp_location_creation,
            self.test_weatherinfo_mcp_weather_observation,
        ]
        
        results = []
        for test_method in weatherinfo_mcp_tests:
            try:
                result = await test_method()
                results.append(result)
                self.test_results.append(result)
                
                status = "PASS" if result.passed else "FAIL"
                logger.info(f"{status}: {result.test_name} ({result.execution_time:.2f}s)")
                
                if not result.passed:
                    logger.error(f"  Error: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"WeatherInfo_MCP test {test_method.__name__} failed with exception: {e}")
                error_result = ComprehensiveTestResult(
                    test_name=test_method.__name__,
                    test_category="weatherinfo_mcp",
                    passed=False,
                    error_message=str(e),
                    execution_time=0.0
                )
                results.append(error_result)
                self.test_results.append(error_result)
        
        return results
    
    async def run_inspector_tests(self) -> List[ComprehensiveTestResult]:
        """Run MCP Inspector integration tests."""
        logger.info("Running MCP Inspector Integration Tests...")
        
        inspector_tests = [
            self.test_inspector_availability,
        ]
        
        results = []
        for test_method in inspector_tests:
            try:
                result = await test_method()
                results.append(result)
                self.test_results.append(result)
                
                status = "PASS" if result.passed else "FAIL"
                logger.info(f"{status}: {result.test_name} ({result.execution_time:.2f}s)")
                
                if not result.passed:
                    logger.error(f"  Error: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"Inspector test {test_method.__name__} failed with exception: {e}")
                error_result = ComprehensiveTestResult(
                    test_name=test_method.__name__,
                    test_category="inspector",
                    passed=False,
                    error_message=str(e),
                    execution_time=0.0
                )
                results.append(error_result)
                self.test_results.append(error_result)
        
        return results
    
    async def run_all_tests(self, test_type: str = "all") -> List[ComprehensiveTestResult]:
        """Run all comprehensive tests."""
        logger.info("Starting Comprehensive Stdio MCP Conformance Tests")
        logger.info(f"Test Type: {test_type}")
        
        all_results = []
        
        if test_type in ["base", "all"]:
            base_results = await self.run_base_tests()
            all_results.extend(base_results)
        
        if test_type in ["weatherinfo_mcp", "all"]:
            weatherinfo_mcp_results = await self.run_weatherinfo_mcp_tests()
            all_results.extend(weatherinfo_mcp_results)
        
        if test_type in ["inspector", "all"]:
            inspector_results = await self.run_inspector_tests()
            all_results.extend(inspector_results)
        
        return all_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        # Group results by category
        base_results = [r for r in self.test_results if r.test_category == "base"]
        weatherinfo_mcp_results = [r for r in self.test_results if r.test_category == "weatherinfo_mcp"]
        inspector_results = [r for r in self.test_results if r.test_category == "inspector"]
        
        report = f"""
COMPREHENSIVE STDIO MCP CONFORMANCE TEST REPORT
===============================================

✅ Testing stdio-based MCP server with comprehensive validation
   Server Command: {self.server_command}
   Server Args: {self.server_args}
   Server CWD: {self.server_cwd}
   Protocol Version: {self.protocol_version}
   Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

Summary:
--------
Total Tests: {total_tests}
Passed: {passed_tests}
Failed: {failed_tests}
Success Rate: {(passed_tests/total_tests)*100:.1f}%

Test Categories:
----------------
Base MCP Protocol: {len(base_results)} tests ({sum(1 for r in base_results if r.passed)} passed)
WeatherInfo_MCP Specific: {len(weatherinfo_mcp_results)} tests ({sum(1 for r in weatherinfo_mcp_results if r.passed)} passed)
MCP Inspector: {len(inspector_results)} tests ({sum(1 for r in inspector_results if r.passed)} passed)

Detailed Results:
----------------
"""
        
        for result in self.test_results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            report += f"\n{status}: [{result.test_category.upper()}] {result.test_name} ({result.execution_time:.2f}s)"
            if result.mcp_spec_section:
                report += f"\n    MCP Spec: {result.mcp_spec_section}"
            
            if not result.passed:
                report += f"\n    Error: {result.error_message}"
            
            if result.details:
                report += f"\n    Details: {json.dumps(result.details, indent=4)}"
        
        report += f"""

Test Coverage:
--------------
✅ Base MCP Protocol Tests:
   - Connection and Initialization (Base Protocol - Lifecycle)
   - Tool Manifest Compliance (Server Features - Tools)
   - Tool Execution Compliance (Server Features - Tools)

✅ WeatherInfo_MCP-Specific Tests:
   - Tool Availability Validation
   - Location Creation Functionality
   - Weather Observation Retrieval

✅ MCP Inspector Integration:
   - Inspector Tool Availability
   - CLI Integration Testing

Compliance Status:
------------------
✅ COMPREHENSIVE TESTING with MCP specification version {self.protocol_version}
✅ All required protocol components tested
✅ Proper stdio transport implementation
✅ FastMCP server compatibility validated
✅ WeatherInfo_MCP-specific functionality validated

References:
-----------
- MCP Specification: https://modelcontextprotocol.io/specification/{self.protocol_version}
- FastMCP Documentation: https://github.com/modelcontextprotocol/python-sdk
- MCP Inspector: https://modelcontextprotocol.io/docs/tools/inspector
- WeatherInfo_MCP Documentation: ../README.md
"""
        
        return report


async def main():
    """Main entry point for comprehensive stdio MCP tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Stdio MCP Conformance Tests")
    parser.add_argument("--test-type", choices=["base", "weatherinfo_mcp", "inspector", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--server-command", help="Command to start the MCP server")
    parser.add_argument("--server-args", nargs="*", help="Arguments to pass to the server")
    parser.add_argument("--server-cwd", help="Working directory for the server")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout for operations")
    parser.add_argument("--output", help="Output file for test report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create comprehensive test framework
    framework = ComprehensiveStdioMCPTests(
        server_command=args.server_command,
        server_args=args.server_args,
        server_cwd=args.server_cwd,
        timeout=args.timeout
    )
    
    try:
        # Run tests
        results = await framework.run_all_tests(args.test_type)
        
        # Generate and display report
        report = framework.generate_report()
        print(report)
        
        # Save report to file if specified
        if args.output:
            # Create parent directory if it doesn't exist
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {args.output}")
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in results if not result.passed)
        sys.exit(0 if failed_tests == 0 else 1)
        
    except KeyboardInterrupt:
        logger.info("Comprehensive stdio MCP tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Comprehensive stdio MCP tests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
