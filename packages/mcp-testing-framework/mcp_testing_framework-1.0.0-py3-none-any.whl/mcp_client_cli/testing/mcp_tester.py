"""
Core MCP Server Testing Framework.

This module implements the MCPServerTester class that provides comprehensive
testing capabilities for MCP servers, following the existing async patterns
from the mcp-client-cli codebase.
"""

import asyncio
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from mcp import StdioServerParameters

from ..config import AppConfig, ServerConfig
from ..tool import McpServerConfig, McpToolkit


class TestStatus(Enum):
    """Test execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result with confidence scoring."""

    test_name: str
    status: TestStatus
    confidence_score: float  # 0.0 to 1.0
    execution_time: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    error_info: Optional[str] = None


@dataclass
class TestSuite:
    """Collection of test results for a server."""

    server_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    skipped_tests: int
    overall_confidence: float
    execution_time: float
    results: List[TestResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class MCPServerTester:
    """
    Core MCP Server Testing Framework.

    This class provides comprehensive testing capabilities for MCP servers,
    extending the existing async patterns from McpToolkit and following
    methodological pragmatism principles with confidence scoring and
    systematic verification.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize the MCP Server Tester.

        Args:
            config: Application configuration containing server definitions
        """
        self.config = config
        self._active_toolkits: Dict[str, McpToolkit] = {}
        self._test_results: Dict[str, TestSuite] = {}

    async def test_server_connectivity(
        self, server_config: ServerConfig, server_name: str
    ) -> TestResult:
        """
        Test basic connectivity to an MCP server.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server

        Returns:
            TestResult: Result of connectivity test with confidence score
        """
        start_time = time.time()
        test_name = f"{server_name}_connectivity"

        try:
            # Create MCP server configuration
            mcp_config = McpServerConfig(
                server_name=server_name,
                server_param=StdioServerParameters(
                    command=server_config.command,
                    args=server_config.args or [],
                    env=server_config.env or {},
                ),
                exclude_tools=server_config.exclude_tools or [],
            )

            # Test connection using existing McpToolkit pattern
            toolkit = McpToolkit(
                name=server_name,
                server_param=mcp_config.server_param,
                exclude_tools=mcp_config.exclude_tools,
            )

            # Attempt to start session with timeout
            async with asyncio.timeout(10.0):
                await toolkit._start_session()

            # Store for later use
            self._active_toolkits[server_name] = toolkit

            execution_time = time.time() - start_time

            return TestResult(
                test_name=test_name,
                status=TestStatus.PASSED,
                confidence_score=0.95,  # High confidence for successful connection
                execution_time=execution_time,
                message=f"Successfully connected to {server_name}",
                details={
                    "command": server_config.command,
                    "args": server_config.args,
                    "connection_time": execution_time,
                },
            )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.FAILED,
                confidence_score=0.90,  # High confidence in timeout failure
                execution_time=execution_time,
                message=f"Connection timeout for {server_name}",
                error_info="Connection timed out after 10 seconds",
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.85,  # High confidence in error detection
                execution_time=execution_time,
                message=f"Connection error for {server_name}: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def test_tool_discovery(
        self, server_config: ServerConfig, server_name: str
    ) -> TestResult:
        """
        Test tool discovery capabilities of an MCP server.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server

        Returns:
            TestResult: Result of tool discovery test
        """
        start_time = time.time()
        test_name = f"{server_name}_tool_discovery"

        try:
            # Get or create toolkit
            toolkit = self._active_toolkits.get(server_name)
            if not toolkit:
                # Run connectivity test first
                conn_result = await self.test_server_connectivity(
                    server_config, server_name
                )
                if conn_result.status != TestStatus.PASSED:
                    return TestResult(
                        test_name=test_name,
                        status=TestStatus.SKIPPED,
                        confidence_score=0.95,
                        execution_time=time.time() - start_time,
                        message=f"Skipped tool discovery - connectivity failed for {server_name}",
                    )
                toolkit = self._active_toolkits[server_name]

            # Initialize toolkit to discover tools
            await toolkit.initialize(force_refresh=True)
            tools = toolkit.get_tools()

            execution_time = time.time() - start_time

            # Calculate confidence based on tool discovery success
            confidence = 0.90 if len(tools) > 0 else 0.75

            return TestResult(
                test_name=test_name,
                status=TestStatus.PASSED,
                confidence_score=confidence,
                execution_time=execution_time,
                message=f"Discovered {len(tools)} tools for {server_name}",
                details={
                    "tool_count": len(tools),
                    "tool_names": [tool.name for tool in tools],
                    "discovery_time": execution_time,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.85,
                execution_time=execution_time,
                message=f"Tool discovery error for {server_name}: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def test_tool_execution(
        self,
        server_config: ServerConfig,
        server_name: str,
        tool_name: str,
        test_args: Dict[str, Any] = None,
    ) -> TestResult:
        """
        Test execution of a specific tool on an MCP server.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server
            tool_name: Name of the tool to test
            test_args: Arguments to pass to the tool (optional)

        Returns:
            TestResult: Result of tool execution test
        """
        start_time = time.time()
        test_name = f"{server_name}_{tool_name}_execution"

        try:
            # Get toolkit
            toolkit = self._active_toolkits.get(server_name)
            if not toolkit:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.SKIPPED,
                    confidence_score=0.95,
                    execution_time=time.time() - start_time,
                    message=f"Skipped tool execution - no active toolkit for {server_name}",
                )

            # Find the tool
            tools = toolkit.get_tools()
            target_tool = next(
                (tool for tool in tools if tool.name == tool_name), None
            )

            if not target_tool:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.FAILED,
                    confidence_score=0.90,
                    execution_time=time.time() - start_time,
                    message=f"Tool '{tool_name}' not found in {server_name}",
                )

            # Execute tool with test arguments or empty args
            test_args = test_args or {}

            async with asyncio.timeout(
                30.0
            ):  # 30 second timeout for tool execution
                result = await target_tool._arun(**test_args)

            execution_time = time.time() - start_time

            return TestResult(
                test_name=test_name,
                status=TestStatus.PASSED,
                confidence_score=0.85,  # Moderate confidence for successful execution
                execution_time=execution_time,
                message=f"Successfully executed {tool_name} on {server_name}",
                details={
                    "tool_name": tool_name,
                    "test_args": test_args,
                    "result_length": len(str(result)) if result else 0,
                    "execution_time": execution_time,
                },
            )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.FAILED,
                confidence_score=0.90,
                execution_time=execution_time,
                message=f"Tool execution timeout for {tool_name} on {server_name}",
                error_info="Tool execution timed out after 30 seconds",
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.80,
                execution_time=execution_time,
                message=f"Tool execution error for {tool_name} on {server_name}: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def validate_configuration(self, config: AppConfig) -> TestResult:
        """
        Validate the overall MCP configuration.

        Args:
            config: Application configuration to validate

        Returns:
            TestResult: Result of configuration validation
        """
        start_time = time.time()
        test_name = "configuration_validation"

        try:
            issues = []

            # Check LLM configuration
            if not config.llm.model:
                issues.append("LLM model not specified")
            if not config.llm.provider:
                issues.append("LLM provider not specified")

            # Check system prompt
            if (
                not config.system_prompt
                or len(config.system_prompt.strip()) == 0
            ):
                issues.append("System prompt is empty")

            # Check MCP servers
            if not config.mcp_servers:
                issues.append("No MCP servers configured")
            else:
                for server_name, server_config in config.mcp_servers.items():
                    if not server_config.command:
                        issues.append(
                            f"Server '{server_name}' has no command specified"
                        )

            execution_time = time.time() - start_time

            if issues:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.FAILED,
                    confidence_score=0.95,  # High confidence in validation issues
                    execution_time=execution_time,
                    message=f"Configuration validation failed: {len(issues)} issues found",
                    details={"issues": issues},
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.PASSED,
                    confidence_score=0.90,
                    execution_time=execution_time,
                    message="Configuration validation passed",
                    details={
                        "llm_provider": config.llm.provider,
                        "llm_model": config.llm.model,
                        "server_count": len(config.mcp_servers),
                        "enabled_servers": len(config.get_enabled_servers()),
                    },
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.85,
                execution_time=execution_time,
                message=f"Configuration validation error: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def run_comprehensive_test_suite(
        self, server_name: Optional[str] = None
    ) -> Dict[str, TestSuite]:
        """
        Run comprehensive test suite for all or specific servers.

        Args:
            server_name: Optional specific server to test (tests all if None)

        Returns:
            Dict[str, TestSuite]: Test results for each server
        """
        time.time()
        results = {}

        # First validate configuration
        config_result = await self.validate_configuration(self.config)

        # Determine which servers to test
        servers_to_test = {}
        if server_name:
            if server_name in self.config.mcp_servers:
                servers_to_test[server_name] = self.config.mcp_servers[
                    server_name
                ]
        else:
            servers_to_test = self.config.get_enabled_servers()

        # Test each server
        for name, server_config in servers_to_test.items():
            suite_start_time = time.time()
            test_results = []

            # Add configuration result to each suite
            test_results.append(config_result)

            # Test connectivity
            conn_result = await self.test_server_connectivity(
                server_config, name
            )
            test_results.append(conn_result)

            # Test tool discovery if connectivity passed
            if conn_result.status == TestStatus.PASSED:
                discovery_result = await self.test_tool_discovery(
                    server_config, name
                )
                test_results.append(discovery_result)

                # Test tool execution for discovered tools (sample testing)
                if (
                    discovery_result.status == TestStatus.PASSED
                    and discovery_result.details.get("tool_count", 0) > 0
                ):
                    tool_names = discovery_result.details.get("tool_names", [])
                    # Test first tool as sample (can be extended for comprehensive testing)
                    if tool_names:
                        execution_result = await self.test_tool_execution(
                            server_config, name, tool_names[0]
                        )
                        test_results.append(execution_result)

            # Calculate suite statistics
            passed = sum(
                1 for r in test_results if r.status == TestStatus.PASSED
            )
            failed = sum(
                1 for r in test_results if r.status == TestStatus.FAILED
            )
            errors = sum(
                1 for r in test_results if r.status == TestStatus.ERROR
            )
            skipped = sum(
                1 for r in test_results if r.status == TestStatus.SKIPPED
            )

            # Calculate overall confidence (weighted average)
            if test_results:
                overall_confidence = sum(
                    r.confidence_score for r in test_results
                ) / len(test_results)
            else:
                overall_confidence = 0.0

            suite_execution_time = time.time() - suite_start_time

            suite = TestSuite(
                server_name=name,
                total_tests=len(test_results),
                passed_tests=passed,
                failed_tests=failed,
                error_tests=errors,
                skipped_tests=skipped,
                overall_confidence=overall_confidence,
                execution_time=suite_execution_time,
                results=test_results,
            )

            results[name] = suite
            self._test_results[name] = suite

        return results

    async def cleanup(self):
        """Clean up active connections and resources."""
        for toolkit in self._active_toolkits.values():
            try:
                await toolkit.close()
            except Exception:
                pass  # Ignore cleanup errors
        self._active_toolkits.clear()

    def get_test_results(self) -> Dict[str, TestSuite]:
        """Get all stored test results."""
        return self._test_results.copy()
