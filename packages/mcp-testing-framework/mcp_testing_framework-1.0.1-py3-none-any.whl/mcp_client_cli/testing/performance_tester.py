"""
Performance Testing Module for MCP Servers.

This module implements comprehensive performance testing capabilities for MCP servers,
including benchmarking, load testing, concurrent connection testing, and resource
monitoring following methodological pragmatism principles.
"""

import asyncio
import statistics
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import psutil
from mcp import StdioServerParameters

from ..config import ServerConfig
from ..tool import McpServerConfig, McpToolkit
from .mcp_tester import TestResult, TestStatus


@dataclass
class PerformanceTestConfig:
    """Configuration for performance testing scenarios."""

    test_response_times: bool = True
    test_concurrent_connections: bool = True
    test_resource_usage: bool = True
    test_load_capacity: bool = True
    test_memory_leaks: bool = True

    # Test parameters
    max_concurrent_connections: int = 50
    test_duration_seconds: int = 60
    warmup_duration_seconds: int = 10
    cooldown_duration_seconds: int = 5

    # Performance thresholds
    max_response_time_ms: float = 2000.0
    max_memory_usage_mb: float = 512.0
    max_cpu_usage_percent: float = 80.0
    min_success_rate: float = 0.95


@dataclass
class PerformanceMetrics:
    """Performance metrics collected during testing."""

    response_times: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    cpu_usage: List[float] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    error_count: int = 0

    # Derived metrics
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0

    avg_memory_usage: float = 0.0
    peak_memory_usage: float = 0.0
    avg_cpu_usage: float = 0.0
    peak_cpu_usage: float = 0.0

    success_rate: float = 0.0
    throughput_rps: float = 0.0

    def calculate_derived_metrics(self, test_duration: float):
        """Calculate derived metrics from collected data."""
        if self.response_times:
            self.avg_response_time = statistics.mean(self.response_times)
            self.min_response_time = min(self.response_times)
            self.max_response_time = max(self.response_times)

            sorted_times = sorted(self.response_times)
            n = len(sorted_times)
            self.p95_response_time = (
                sorted_times[int(0.95 * n)] if n > 0 else 0.0
            )
            self.p99_response_time = (
                sorted_times[int(0.99 * n)] if n > 0 else 0.0
            )

        if self.memory_usage:
            self.avg_memory_usage = statistics.mean(self.memory_usage)
            self.peak_memory_usage = max(self.memory_usage)

        if self.cpu_usage:
            self.avg_cpu_usage = statistics.mean(self.cpu_usage)
            self.peak_cpu_usage = max(self.cpu_usage)

        total_requests = (
            self.success_count + self.failure_count + self.error_count
        )
        self.success_rate = (
            self.success_count / total_requests if total_requests > 0 else 0.0
        )
        self.throughput_rps = (
            total_requests / test_duration if test_duration > 0 else 0.0
        )


@dataclass
class LoadTestResult:
    """Result of a load testing scenario."""

    scenario_name: str
    concurrent_users: int
    test_duration: float
    metrics: PerformanceMetrics
    baseline_comparison: Optional[Dict[str, float]] = None
    performance_grade: str = "unknown"  # A, B, C, D, F
    bottlenecks_detected: List[str] = field(default_factory=list)


class MCPPerformanceTester:
    """
    Comprehensive performance testing framework for MCP servers.

    This class provides specialized performance testing capabilities including
    response time measurement, load testing, resource monitoring, and
    performance regression detection following existing async patterns.
    """

    def __init__(self, config: PerformanceTestConfig = None):
        """
        Initialize the performance tester.

        Args:
            config: Performance testing configuration
        """
        self.config = config or PerformanceTestConfig()
        self._baseline_metrics: Optional[PerformanceMetrics] = None
        self._test_results: List[LoadTestResult] = []

    async def benchmark_tool_execution(
        self, server_config: ServerConfig, server_name: str
    ) -> TestResult:
        """
        Benchmark tool execution performance for an MCP server.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server

        Returns:
            TestResult: Benchmark test result with performance metrics
        """
        start_time = time.time()
        test_name = f"{server_name}_tool_benchmark"

        try:
            # Create toolkit for testing
            mcp_config = McpServerConfig(
                server_name=server_name,
                server_param=StdioServerParameters(
                    command=server_config.command,
                    args=server_config.args or [],
                    env=server_config.env or {},
                ),
                exclude_tools=server_config.exclude_tools or [],
            )

            toolkit = McpToolkit(
                name=server_name,
                server_param=mcp_config.server_param,
                exclude_tools=mcp_config.exclude_tools,
            )

            await toolkit.initialize()
            tools = toolkit.get_tools()

            if not tools:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.SKIPPED,
                    confidence_score=0.95,
                    execution_time=time.time() - start_time,
                    message=f"No tools available for benchmarking in {server_name}",
                )

            # Benchmark each tool
            tool_benchmarks = {}
            overall_metrics = PerformanceMetrics()

            for tool_name in tools[
                :5
            ]:  # Limit to first 5 tools for reasonable test time
                tool_metrics = await self._benchmark_single_tool(
                    toolkit, tool_name
                )
                tool_benchmarks[tool_name] = tool_metrics

                # Aggregate metrics
                overall_metrics.response_times.extend(
                    tool_metrics.response_times
                )
                overall_metrics.success_count += tool_metrics.success_count
                overall_metrics.failure_count += tool_metrics.failure_count
                overall_metrics.error_count += tool_metrics.error_count

            # Calculate derived metrics
            test_duration = time.time() - start_time
            overall_metrics.calculate_derived_metrics(test_duration)

            # Determine performance grade
            performance_grade = self._calculate_performance_grade(
                overall_metrics
            )

            # Check against thresholds
            issues = []
            if (
                overall_metrics.avg_response_time
                > self.config.max_response_time_ms
            ):
                issues.append(
                    f"Average response time ({overall_metrics.avg_response_time:.1f}ms) exceeds threshold"
                )

            if overall_metrics.success_rate < self.config.min_success_rate:
                issues.append(
                    f"Success rate ({overall_metrics.success_rate:.2%}) below threshold"
                )

            status = TestStatus.PASSED if not issues else TestStatus.FAILED
            confidence = 0.90 if len(tools) >= 3 else 0.75

            return TestResult(
                test_name=test_name,
                status=status,
                confidence_score=confidence,
                execution_time=test_duration,
                message=f"Tool benchmark completed: Grade {performance_grade}",
                details={
                    "performance_grade": performance_grade,
                    "tools_tested": len(tool_benchmarks),
                    "avg_response_time_ms": overall_metrics.avg_response_time,
                    "p95_response_time_ms": overall_metrics.p95_response_time,
                    "success_rate": overall_metrics.success_rate,
                    "throughput_rps": overall_metrics.throughput_rps,
                    "tool_benchmarks": {
                        tool: {
                            "avg_response_time": metrics.avg_response_time,
                            "success_rate": metrics.success_rate,
                        }
                        for tool, metrics in tool_benchmarks.items()
                    },
                    "issues": issues,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.85,
                execution_time=execution_time,
                message=f"Tool benchmark error: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def test_concurrent_connections(
        self, server_config: ServerConfig, server_name: str
    ) -> TestResult:
        """
        Test concurrent connection handling capabilities.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server

        Returns:
            TestResult: Concurrent connection test result
        """
        start_time = time.time()
        test_name = f"{server_name}_concurrent_connections"

        try:
            # Test with increasing concurrent connections
            connection_levels = [1, 5, 10, 20, 30]
            if self.config.max_concurrent_connections > 30:
                connection_levels.append(
                    self.config.max_concurrent_connections
                )

            load_test_results = []

            for concurrent_users in connection_levels:
                print(f"Testing {concurrent_users} concurrent connections...")

                load_result = await self._run_load_test(
                    server_config,
                    server_name,
                    concurrent_users,
                    duration_seconds=min(
                        30, self.config.test_duration_seconds
                    ),
                )

                load_test_results.append(load_result)

                # Stop if performance degrades significantly
                if load_result.metrics.success_rate < 0.5:
                    break

                # Brief cooldown between tests
                await asyncio.sleep(2)

            # Analyze results
            max_stable_connections = 0
            performance_breakdown_point = None

            for result in load_test_results:
                if result.metrics.success_rate >= self.config.min_success_rate:
                    max_stable_connections = result.concurrent_users
                else:
                    performance_breakdown_point = result.concurrent_users
                    break

            # Determine overall status
            if max_stable_connections >= 10:
                status = TestStatus.PASSED
                confidence = 0.90
            elif max_stable_connections >= 5:
                status = TestStatus.PASSED
                confidence = 0.80
            else:
                status = TestStatus.FAILED
                confidence = 0.85

            execution_time = time.time() - start_time

            return TestResult(
                test_name=test_name,
                status=status,
                confidence_score=confidence,
                execution_time=execution_time,
                message=f"Concurrent connection test completed: Max stable connections = {max_stable_connections}",
                details={
                    "max_stable_connections": max_stable_connections,
                    "performance_breakdown_point": performance_breakdown_point,
                    "load_test_results": [
                        {
                            "concurrent_users": r.concurrent_users,
                            "success_rate": r.metrics.success_rate,
                            "avg_response_time": r.metrics.avg_response_time,
                            "throughput_rps": r.metrics.throughput_rps,
                            "performance_grade": r.performance_grade,
                        }
                        for r in load_test_results
                    ],
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.80,
                execution_time=execution_time,
                message=f"Concurrent connection test error: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def measure_response_times(
        self, server_config: ServerConfig, server_name: str
    ) -> TestResult:
        """
        Measure detailed response time characteristics.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server

        Returns:
            TestResult: Response time measurement result
        """
        start_time = time.time()
        test_name = f"{server_name}_response_times"

        try:
            # Create toolkit for testing
            mcp_config = McpServerConfig(
                server_name=server_name,
                server_param=StdioServerParameters(
                    command=server_config.command,
                    args=server_config.args or [],
                    env=server_config.env or {},
                ),
                exclude_tools=server_config.exclude_tools or [],
            )

            toolkit = McpToolkit(
                name=server_name,
                server_param=mcp_config.server_param,
                exclude_tools=mcp_config.exclude_tools,
            )

            await toolkit.initialize()
            tools = toolkit.get_tools()

            if not tools:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.SKIPPED,
                    confidence_score=0.95,
                    execution_time=time.time() - start_time,
                    message=f"No tools available for response time testing in {server_name}",
                )

            # Measure response times with different scenarios
            scenarios = [
                ("cold_start", 1),  # Single cold start
                ("warm_sequential", 10),  # Sequential warm calls
                ("burst", 5),  # Burst of concurrent calls
            ]

            scenario_results = {}

            for scenario_name, call_count in scenarios:
                scenario_metrics = await self._measure_scenario_response_times(
                    toolkit, tools[0], scenario_name, call_count
                )
                scenario_results[scenario_name] = scenario_metrics

            # Analyze response time patterns
            all_response_times = []
            for metrics in scenario_results.values():
                all_response_times.extend(metrics.response_times)

            if all_response_times:
                overall_metrics = PerformanceMetrics()
                overall_metrics.response_times = all_response_times
                overall_metrics.calculate_derived_metrics(
                    time.time() - start_time
                )

                # Check for performance issues
                issues = []
                if (
                    overall_metrics.p95_response_time
                    > self.config.max_response_time_ms
                ):
                    issues.append(
                        f"P95 response time ({overall_metrics.p95_response_time:.1f}ms) exceeds threshold"
                    )

                if (
                    overall_metrics.max_response_time
                    > self.config.max_response_time_ms * 2
                ):
                    issues.append(
                        f"Maximum response time ({overall_metrics.max_response_time:.1f}ms) is excessive"
                    )

                # Check for response time variability
                if len(all_response_times) > 1:
                    response_time_std = statistics.stdev(all_response_times)
                    if (
                        response_time_std
                        > overall_metrics.avg_response_time * 0.5
                    ):
                        issues.append(
                            "High response time variability detected"
                        )

                status = TestStatus.PASSED if not issues else TestStatus.FAILED
                confidence = 0.88

                execution_time = time.time() - start_time

                return TestResult(
                    test_name=test_name,
                    status=status,
                    confidence_score=confidence,
                    execution_time=execution_time,
                    message=f"Response time measurement completed: Avg {overall_metrics.avg_response_time:.1f}ms",
                    details={
                        "avg_response_time_ms": overall_metrics.avg_response_time,
                        "min_response_time_ms": overall_metrics.min_response_time,
                        "max_response_time_ms": overall_metrics.max_response_time,
                        "p95_response_time_ms": overall_metrics.p95_response_time,
                        "p99_response_time_ms": overall_metrics.p99_response_time,
                        "response_time_std": (
                            statistics.stdev(all_response_times)
                            if len(all_response_times) > 1
                            else 0
                        ),
                        "scenario_results": {
                            scenario: {
                                "avg_response_time": metrics.avg_response_time,
                                "min_response_time": metrics.min_response_time,
                                "max_response_time": metrics.max_response_time,
                            }
                            for scenario, metrics in scenario_results.items()
                        },
                        "issues": issues,
                    },
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.FAILED,
                    confidence_score=0.85,
                    execution_time=time.time() - start_time,
                    message="No response times could be measured",
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.80,
                execution_time=execution_time,
                message=f"Response time measurement error: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def test_resource_usage(
        self, server_config: ServerConfig, server_name: str
    ) -> TestResult:
        """
        Test resource usage patterns and detect memory leaks.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server

        Returns:
            TestResult: Resource usage test result
        """
        start_time = time.time()
        test_name = f"{server_name}_resource_usage"

        try:
            # Start resource monitoring
            resource_monitor = ResourceMonitor()
            await resource_monitor.start()

            # Create toolkit for testing
            mcp_config = McpServerConfig(
                server_name=server_name,
                server_param=StdioServerParameters(
                    command=server_config.command,
                    args=server_config.args or [],
                    env=server_config.env or {},
                ),
                exclude_tools=server_config.exclude_tools or [],
            )

            toolkit = McpToolkit(
                name=server_name,
                server_param=mcp_config.server_param,
                exclude_tools=mcp_config.exclude_tools,
            )

            await toolkit.initialize()
            tools = toolkit.get_tools()

            if not tools:
                await resource_monitor.stop()
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.SKIPPED,
                    confidence_score=0.95,
                    execution_time=time.time() - start_time,
                    message=f"No tools available for resource usage testing in {server_name}",
                )

            # Run sustained load to monitor resource usage
            test_duration = min(60, self.config.test_duration_seconds)
            end_time = time.time() + test_duration

            operation_count = 0
            while time.time() < end_time:
                try:
                    # Perform operations to stress the server
                    for tool_name in tools[:3]:  # Use first 3 tools
                        await toolkit.call_tool(tool_name, {})
                        operation_count += 1

                        # Brief pause to allow monitoring
                        await asyncio.sleep(0.1)

                except Exception:
                    # Continue testing even if some operations fail
                    pass

            # Stop monitoring and analyze results
            resource_data = await resource_monitor.stop()

            # Analyze resource usage patterns
            issues = []

            if (
                resource_data["peak_memory_mb"]
                > self.config.max_memory_usage_mb
            ):
                issues.append(
                    f"Peak memory usage ({resource_data['peak_memory_mb']:.1f}MB) exceeds threshold"
                )

            if (
                resource_data["avg_cpu_percent"]
                > self.config.max_cpu_usage_percent
            ):
                issues.append(
                    f"Average CPU usage ({resource_data['avg_cpu_percent']:.1f}%) exceeds threshold"
                )

            # Check for memory leaks
            memory_trend = self._analyze_memory_trend(
                resource_data["memory_samples"]
            )
            if memory_trend > 0.1:  # More than 10% increase over time
                issues.append(
                    f"Potential memory leak detected (trend: +{memory_trend:.1%})"
                )

            status = TestStatus.PASSED if not issues else TestStatus.FAILED
            confidence = 0.85

            execution_time = time.time() - start_time

            return TestResult(
                test_name=test_name,
                status=status,
                confidence_score=confidence,
                execution_time=execution_time,
                message=f"Resource usage test completed: {len(issues)} issues found",
                details={
                    "test_duration_seconds": test_duration,
                    "operations_performed": operation_count,
                    "peak_memory_mb": resource_data["peak_memory_mb"],
                    "avg_memory_mb": resource_data["avg_memory_mb"],
                    "peak_cpu_percent": resource_data["peak_cpu_percent"],
                    "avg_cpu_percent": resource_data["avg_cpu_percent"],
                    "memory_trend": memory_trend,
                    "issues": issues,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                confidence_score=0.75,
                execution_time=execution_time,
                message=f"Resource usage test error: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def run_comprehensive_performance_suite(
        self, server_config: ServerConfig, server_name: str
    ) -> Dict[str, TestResult]:
        """
        Run a comprehensive performance test suite.

        Args:
            server_config: Server configuration to test
            server_name: Name identifier for the server

        Returns:
            Dict[str, TestResult]: Dictionary of all performance test results
        """
        results = {}

        if self.config.test_response_times:
            results["response_times"] = await self.measure_response_times(
                server_config, server_name
            )

        if self.config.test_concurrent_connections:
            results["concurrent_connections"] = (
                await self.test_concurrent_connections(
                    server_config, server_name
                )
            )

        if self.config.test_resource_usage:
            results["resource_usage"] = await self.test_resource_usage(
                server_config, server_name
            )

        # Tool benchmarking
        results["tool_benchmark"] = await self.benchmark_tool_execution(
            server_config, server_name
        )

        return results

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        if not self._test_results:
            return {"message": "No performance test results available"}

        # Aggregate results
        total_tests = len(self._test_results)
        grades = [result.performance_grade for result in self._test_results]
        grade_distribution = {
            grade: grades.count(grade) for grade in set(grades)
        }

        # Calculate overall performance score
        grade_scores = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
        avg_score = (
            sum(grade_scores.get(grade, 0) for grade in grades) / len(grades)
            if grades
            else 0
        )

        return {
            "total_tests": total_tests,
            "grade_distribution": grade_distribution,
            "average_performance_score": avg_score,
            "test_results": [
                {
                    "scenario": result.scenario_name,
                    "concurrent_users": result.concurrent_users,
                    "duration": result.test_duration,
                    "success_rate": result.metrics.success_rate,
                    "avg_response_time": result.metrics.avg_response_time,
                    "throughput_rps": result.metrics.throughput_rps,
                    "grade": result.performance_grade,
                    "bottlenecks": result.bottlenecks_detected,
                }
                for result in self._test_results
            ],
        }

    # Private helper methods

    async def _benchmark_single_tool(
        self, toolkit: McpToolkit, tool_name: str, iterations: int = 10
    ) -> PerformanceMetrics:
        """Benchmark a single tool's performance."""
        metrics = PerformanceMetrics()

        for _ in range(iterations):
            start_time = time.time()
            try:
                await toolkit.call_tool(tool_name, {})
                response_time = (
                    time.time() - start_time
                ) * 1000  # Convert to milliseconds
                metrics.response_times.append(response_time)
                metrics.success_count += 1
            except Exception:
                metrics.failure_count += 1

        metrics.calculate_derived_metrics(iterations * 0.1)  # Rough estimate
        return metrics

    async def _run_load_test(
        self,
        server_config: ServerConfig,
        server_name: str,
        concurrent_users: int,
        duration_seconds: int,
    ) -> LoadTestResult:
        """Run a load test with specified parameters."""
        start_time = time.time()

        # Create multiple toolkit instances for concurrent testing
        toolkits = []
        for i in range(concurrent_users):
            mcp_config = McpServerConfig(
                server_name=f"{server_name}_{i}",
                server_param=StdioServerParameters(
                    command=server_config.command,
                    args=server_config.args or [],
                    env=server_config.env or {},
                ),
                exclude_tools=server_config.exclude_tools or [],
            )

            toolkit = McpToolkit(
                name=f"{server_name}_{i}",
                server_param=mcp_config.server_param,
                exclude_tools=mcp_config.exclude_tools,
            )
            toolkits.append(toolkit)

        # Initialize all toolkits
        await asyncio.gather(
            *[toolkit.initialize() for toolkit in toolkits],
            return_exceptions=True,
        )

        # Run concurrent load test
        metrics = PerformanceMetrics()
        end_time = time.time() + duration_seconds

        async def worker(toolkit: McpToolkit, worker_id: int):
            """Worker function for load testing."""
            tools = toolkit.get_tools()
            if not tools:
                return

            tool_name = tools[0]  # Use first available tool

            while time.time() < end_time:
                worker_start = time.time()
                try:
                    await toolkit.call_tool(tool_name, {})
                    response_time = (time.time() - worker_start) * 1000
                    metrics.response_times.append(response_time)
                    metrics.success_count += 1
                except Exception:
                    metrics.failure_count += 1

                # Brief pause to prevent overwhelming
                await asyncio.sleep(0.01)

        # Run workers concurrently
        await asyncio.gather(
            *[worker(toolkit, i) for i, toolkit in enumerate(toolkits)],
            return_exceptions=True,
        )

        # Calculate metrics
        actual_duration = time.time() - start_time
        metrics.calculate_derived_metrics(actual_duration)

        # Determine performance grade
        performance_grade = self._calculate_performance_grade(metrics)

        # Detect bottlenecks
        bottlenecks = self._detect_bottlenecks(metrics)

        return LoadTestResult(
            scenario_name=f"load_test_{concurrent_users}_users",
            concurrent_users=concurrent_users,
            test_duration=actual_duration,
            metrics=metrics,
            performance_grade=performance_grade,
            bottlenecks_detected=bottlenecks,
        )

    async def _measure_scenario_response_times(
        self,
        toolkit: McpToolkit,
        tool_name: str,
        scenario_name: str,
        call_count: int,
    ) -> PerformanceMetrics:
        """Measure response times for a specific scenario."""
        metrics = PerformanceMetrics()

        if scenario_name == "cold_start":
            # Single cold start measurement
            start_time = time.time()
            try:
                await toolkit.call_tool(tool_name, {})
                response_time = (time.time() - start_time) * 1000
                metrics.response_times.append(response_time)
                metrics.success_count += 1
            except Exception:
                metrics.failure_count += 1

        elif scenario_name == "warm_sequential":
            # Sequential warm calls
            for _ in range(call_count):
                start_time = time.time()
                try:
                    await toolkit.call_tool(tool_name, {})
                    response_time = (time.time() - start_time) * 1000
                    metrics.response_times.append(response_time)
                    metrics.success_count += 1
                except Exception:
                    metrics.failure_count += 1

                await asyncio.sleep(0.1)  # Brief pause between calls

        elif scenario_name == "burst":
            # Burst of concurrent calls
            async def single_call():
                start_time = time.time()
                try:
                    await toolkit.call_tool(tool_name, {})
                    response_time = (time.time() - start_time) * 1000
                    metrics.response_times.append(response_time)
                    metrics.success_count += 1
                except Exception:
                    metrics.failure_count += 1

            await asyncio.gather(
                *[single_call() for _ in range(call_count)],
                return_exceptions=True,
            )

        metrics.calculate_derived_metrics(call_count * 0.1)  # Rough estimate
        return metrics

    def _calculate_performance_grade(self, metrics: PerformanceMetrics) -> str:
        """Calculate performance grade based on metrics."""
        score = 100

        # Response time scoring
        if metrics.avg_response_time > self.config.max_response_time_ms:
            score -= 20
        elif (
            metrics.avg_response_time > self.config.max_response_time_ms * 0.8
        ):
            score -= 10

        # Success rate scoring
        if metrics.success_rate < self.config.min_success_rate:
            score -= 30
        elif metrics.success_rate < 0.98:
            score -= 15

        # P95 response time scoring
        if metrics.p95_response_time > self.config.max_response_time_ms * 1.5:
            score -= 15

        # Convert score to grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _detect_bottlenecks(self, metrics: PerformanceMetrics) -> List[str]:
        """Detect performance bottlenecks from metrics."""
        bottlenecks = []

        if metrics.avg_response_time > self.config.max_response_time_ms:
            bottlenecks.append("High average response time")

        if metrics.success_rate < self.config.min_success_rate:
            bottlenecks.append("Low success rate")

        if metrics.p95_response_time > metrics.avg_response_time * 3:
            bottlenecks.append("High response time variability")

        if metrics.throughput_rps < 1.0:
            bottlenecks.append("Low throughput")

        return bottlenecks

    def _analyze_memory_trend(self, memory_samples: List[float]) -> float:
        """Analyze memory usage trend to detect leaks."""
        if len(memory_samples) < 10:
            return 0.0

        # Simple linear trend analysis
        n = len(memory_samples)
        x_values = list(range(n))

        # Calculate slope using least squares
        x_mean = sum(x_values) / n
        y_mean = sum(memory_samples) / n

        numerator = sum(
            (x - x_mean) * (y - y_mean)
            for x, y in zip(x_values, memory_samples)
        )
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Convert slope to percentage change over the test period
        if y_mean > 0:
            return (slope * n) / y_mean
        else:
            return 0.0


class ResourceMonitor:
    """Monitor system resource usage during testing."""

    def __init__(self):
        self.monitoring = False
        self.memory_samples = []
        self.cpu_samples = []
        self.monitor_task = None

    async def start(self):
        """Start resource monitoring."""
        self.monitoring = True
        self.memory_samples = []
        self.cpu_samples = []
        self.monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> Dict[str, Any]:
        """Stop monitoring and return collected data."""
        self.monitoring = False
        if self.monitor_task:
            await self.monitor_task

        if not self.memory_samples:
            return {
                "peak_memory_mb": 0,
                "avg_memory_mb": 0,
                "peak_cpu_percent": 0,
                "avg_cpu_percent": 0,
                "memory_samples": [],
                "cpu_samples": [],
            }

        return {
            "peak_memory_mb": max(self.memory_samples),
            "avg_memory_mb": sum(self.memory_samples)
            / len(self.memory_samples),
            "peak_cpu_percent": max(self.cpu_samples),
            "avg_cpu_percent": sum(self.cpu_samples) / len(self.cpu_samples),
            "memory_samples": self.memory_samples.copy(),
            "cpu_samples": self.cpu_samples.copy(),
        }

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Get current process info
                process = psutil.Process()

                # Memory usage in MB
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.memory_samples.append(memory_mb)

                # CPU usage percentage
                cpu_percent = process.cpu_percent()
                self.cpu_samples.append(cpu_percent)

            except Exception:
                # Continue monitoring even if we can't get some metrics
                pass

            await asyncio.sleep(1.0)  # Sample every second
