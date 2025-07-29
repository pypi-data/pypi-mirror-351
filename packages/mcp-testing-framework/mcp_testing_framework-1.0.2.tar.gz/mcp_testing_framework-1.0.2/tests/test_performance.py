"""
Test suite for MCP Performance Testing Module.

This module tests the performance testing capabilities including benchmarking,
load testing, resource monitoring, and performance analysis.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_client_cli.config import ServerConfig
from mcp_client_cli.testing.mcp_tester import TestStatus
from mcp_client_cli.testing.performance_tester import (
    LoadTestResult,
    MCPPerformanceTester,
    PerformanceMetrics,
    PerformanceTestConfig,
    ResourceMonitor,
)


@pytest.fixture
def performance_config():
    """Create a test performance configuration."""
    return PerformanceTestConfig(
        test_response_times=True,
        test_concurrent_connections=True,
        test_resource_usage=True,
        max_concurrent_connections=10,
        test_duration_seconds=5,
        max_response_time_ms=1000.0,
        min_success_rate=0.90,
    )


@pytest.fixture
def server_config():
    """Create a test server configuration."""
    return ServerConfig(
        command="python",
        args=["test_server.py"],
        env={"TEST_MODE": "true"},
        enabled=True,
        exclude_tools=[],
        requires_confirmation=[],
    )


@pytest.fixture
def performance_tester(performance_config):
    """Create a performance tester instance."""
    return MCPPerformanceTester(performance_config)


class TestPerformanceTestConfig:
    """Test PerformanceTestConfig functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PerformanceTestConfig()

        assert config.test_response_times is True
        assert config.test_concurrent_connections is True
        assert config.test_resource_usage is True
        assert config.max_concurrent_connections == 50
        assert config.test_duration_seconds == 60
        assert config.max_response_time_ms == 2000.0
        assert config.min_success_rate == 0.95

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PerformanceTestConfig(
            test_response_times=False,
            max_concurrent_connections=20,
            test_duration_seconds=30,
            max_response_time_ms=500.0,
        )

        assert config.test_response_times is False
        assert config.max_concurrent_connections == 20
        assert config.test_duration_seconds == 30
        assert config.max_response_time_ms == 500.0


class TestPerformanceMetrics:
    """Test PerformanceMetrics functionality."""

    def test_metrics_initialization(self):
        """Test metrics initialization."""
        metrics = PerformanceMetrics()

        assert len(metrics.response_times) == 0
        assert metrics.success_count == 0
        assert metrics.failure_count == 0
        assert metrics.avg_response_time == 0.0
        assert metrics.success_rate == 0.0

    def test_calculate_derived_metrics(self):
        """Test derived metrics calculation."""
        metrics = PerformanceMetrics()
        metrics.response_times = [100.0, 200.0, 150.0, 300.0, 250.0]
        metrics.success_count = 4
        metrics.failure_count = 1

        metrics.calculate_derived_metrics(test_duration=5.0)

        assert metrics.avg_response_time == 200.0
        assert metrics.min_response_time == 100.0
        assert metrics.max_response_time == 300.0
        assert metrics.p95_response_time == 300.0  # 95th percentile
        assert metrics.success_rate == 0.8  # 4/5
        assert metrics.throughput_rps == 1.0  # 5 requests / 5 seconds

    def test_calculate_derived_metrics_empty(self):
        """Test derived metrics calculation with empty data."""
        metrics = PerformanceMetrics()

        metrics.calculate_derived_metrics(test_duration=5.0)

        assert metrics.avg_response_time == 0.0
        assert metrics.success_rate == 0.0
        assert metrics.throughput_rps == 0.0


class TestLoadTestResult:
    """Test LoadTestResult functionality."""

    def test_load_test_result_creation(self):
        """Test creating a load test result."""
        metrics = PerformanceMetrics()
        metrics.avg_response_time = 150.0
        metrics.success_rate = 0.95

        result = LoadTestResult(
            scenario_name="test_scenario",
            concurrent_users=10,
            test_duration=30.0,
            metrics=metrics,
            performance_grade="A",
            bottlenecks_detected=["high_latency"],
        )

        assert result.scenario_name == "test_scenario"
        assert result.concurrent_users == 10
        assert result.test_duration == 30.0
        assert result.metrics == metrics
        assert result.performance_grade == "A"
        assert result.bottlenecks_detected == ["high_latency"]


class TestMCPPerformanceTester:
    """Test MCPPerformanceTester functionality."""

    def test_initialization(self, performance_config):
        """Test performance tester initialization."""
        tester = MCPPerformanceTester(performance_config)

        assert tester.config == performance_config
        assert tester._baseline_metrics is None
        assert len(tester._test_results) == 0

    def test_default_initialization(self):
        """Test performance tester with default config."""
        tester = MCPPerformanceTester()

        assert isinstance(tester.config, PerformanceTestConfig)
        assert tester.config.test_response_times is True

    @pytest.mark.asyncio
    async def test_benchmark_tool_execution_success(
        self, performance_tester, server_config
    ):
        """Test successful tool benchmarking."""
        mock_toolkit = Mock()
        mock_toolkit.initialize = AsyncMock()
        mock_toolkit.get_tools.return_value = ["test_tool1", "test_tool2"]

        # Mock benchmark results
        mock_metrics = PerformanceMetrics()
        mock_metrics.response_times = [100.0, 150.0, 120.0]
        mock_metrics.success_count = 3
        mock_metrics.avg_response_time = 123.3
        mock_metrics.success_rate = 1.0

        with (
            patch(
                "mcp_client_cli.testing.performance_tester.McpToolkit",
                return_value=mock_toolkit,
            ),
            patch.object(
                performance_tester,
                "_benchmark_single_tool",
                return_value=mock_metrics,
            ),
        ):

            result = await performance_tester.benchmark_tool_execution(
                server_config, "test_server"
            )

            assert result.status == TestStatus.PASSED
            assert result.confidence_score >= 0.75
            assert "Grade" in result.message
            assert "tools_tested" in result.details
            assert result.details["tools_tested"] == 2

    @pytest.mark.asyncio
    async def test_benchmark_tool_execution_no_tools(
        self, performance_tester, server_config
    ):
        """Test tool benchmarking with no tools available."""
        mock_toolkit = Mock()
        mock_toolkit.initialize = AsyncMock()
        mock_toolkit.get_tools.return_value = []

        with patch(
            "mcp_client_cli.testing.performance_tester.McpToolkit",
            return_value=mock_toolkit,
        ):

            result = await performance_tester.benchmark_tool_execution(
                server_config, "test_server"
            )

            assert result.status == TestStatus.SKIPPED
            assert result.confidence_score == 0.95
            assert "No tools available" in result.message

    @pytest.mark.asyncio
    async def test_benchmark_tool_execution_error(
        self, performance_tester, server_config
    ):
        """Test tool benchmarking with error."""
        with patch(
            "mcp_client_cli.testing.performance_tester.McpToolkit",
            side_effect=Exception("Test error"),
        ):

            result = await performance_tester.benchmark_tool_execution(
                server_config, "test_server"
            )

            assert result.status == TestStatus.ERROR
            assert result.confidence_score == 0.85
            assert "Tool benchmark error" in result.message
            assert result.error_info is not None

    @pytest.mark.asyncio
    async def test_test_concurrent_connections(
        self, performance_tester, server_config
    ):
        """Test concurrent connection testing."""

        # Mock the _run_load_test method to return consistent results
        async def mock_load_test(
            server_config, server_name, concurrent_users, duration_seconds
        ):
            metrics = PerformanceMetrics()
            metrics.success_count = concurrent_users * 9
            metrics.failure_count = concurrent_users
            metrics.error_count = 0
            metrics.response_times = [0.1] * metrics.success_count
            metrics.calculate_derived_metrics(duration_seconds)

            return LoadTestResult(
                scenario_name=f"load_test_{concurrent_users}_users",
                concurrent_users=concurrent_users,
                test_duration=duration_seconds,
                metrics=metrics,
                performance_grade="A" if concurrent_users <= 5 else "B",
            )

        # Apply the mock
        performance_tester._run_load_test = mock_load_test

        result = await performance_tester.test_concurrent_connections(
            server_config, "test_server"
        )

        assert result.status == TestStatus.PASSED
        assert "concurrent_connections" in result.test_name
        assert result.confidence_score >= 0.8
        assert "load_test_results" in result.details

    @pytest.mark.asyncio
    async def test_measure_response_times(
        self, performance_tester, server_config
    ):
        """Test response time measurement."""
        mock_toolkit = Mock()
        mock_toolkit.initialize = AsyncMock()
        mock_toolkit.get_tools.return_value = ["test_tool"]

        # Mock scenario results
        mock_metrics = PerformanceMetrics()
        mock_metrics.response_times = [100.0, 150.0, 120.0]
        mock_metrics.avg_response_time = 123.3
        mock_metrics.p95_response_time = 150.0

        with (
            patch(
                "mcp_client_cli.testing.performance_tester.McpToolkit",
                return_value=mock_toolkit,
            ),
            patch.object(
                performance_tester,
                "_measure_scenario_response_times",
                return_value=mock_metrics,
            ),
        ):

            result = await performance_tester.measure_response_times(
                server_config, "test_server"
            )

            assert result.status == TestStatus.PASSED
            assert result.confidence_score == 0.88
            assert "Avg" in result.message
            assert "scenario_results" in result.details

    @pytest.mark.asyncio
    async def test_measure_response_times_no_tools(
        self, performance_tester, server_config
    ):
        """Test response time measurement with no tools."""
        mock_toolkit = Mock()
        mock_toolkit.initialize = AsyncMock()
        mock_toolkit.get_tools.return_value = []

        with patch(
            "mcp_client_cli.testing.performance_tester.McpToolkit",
            return_value=mock_toolkit,
        ):

            result = await performance_tester.measure_response_times(
                server_config, "test_server"
            )

            assert result.status == TestStatus.SKIPPED
            assert "No tools available" in result.message

    @pytest.mark.asyncio
    async def test_test_resource_usage(
        self, performance_tester, server_config
    ):
        """Test resource usage testing."""
        mock_toolkit = Mock()
        mock_toolkit.initialize = AsyncMock()
        mock_toolkit.get_tools.return_value = ["test_tool"]
        mock_toolkit.call_tool = AsyncMock()

        # Mock resource monitor
        mock_resource_data = {
            "peak_memory_mb": 100.0,
            "avg_memory_mb": 80.0,
            "peak_cpu_percent": 50.0,
            "avg_cpu_percent": 30.0,
            "memory_samples": [80.0, 85.0, 90.0, 95.0, 100.0],
            "cpu_samples": [30.0, 35.0, 40.0, 45.0, 50.0],
        }

        with (
            patch(
                "mcp_client_cli.testing.performance_tester.McpToolkit",
                return_value=mock_toolkit,
            ),
            patch(
                "mcp_client_cli.testing.performance_tester.ResourceMonitor"
            ) as mock_monitor_class,
        ):

            mock_monitor = Mock()
            mock_monitor.start = AsyncMock()
            mock_monitor.stop = AsyncMock(return_value=mock_resource_data)
            mock_monitor_class.return_value = mock_monitor

            result = await performance_tester.test_resource_usage(
                server_config, "test_server"
            )

            assert result.status == TestStatus.PASSED
            assert result.confidence_score == 0.85
            assert "issues found" in result.message
            assert "peak_memory_mb" in result.details

    @pytest.mark.asyncio
    async def test_run_comprehensive_performance_suite(
        self, performance_tester, server_config
    ):
        """Test comprehensive performance suite."""
        # Mock all individual test methods
        with (
            patch.object(
                performance_tester, "measure_response_times"
            ) as mock_response,
            patch.object(
                performance_tester, "test_concurrent_connections"
            ) as mock_concurrent,
            patch.object(
                performance_tester, "test_resource_usage"
            ) as mock_resource,
            patch.object(
                performance_tester, "benchmark_tool_execution"
            ) as mock_benchmark,
        ):

            # Configure mock return values
            mock_response.return_value = Mock(status=TestStatus.PASSED)
            mock_concurrent.return_value = Mock(status=TestStatus.PASSED)
            mock_resource.return_value = Mock(status=TestStatus.PASSED)
            mock_benchmark.return_value = Mock(status=TestStatus.PASSED)

            results = (
                await performance_tester.run_comprehensive_performance_suite(
                    server_config, "test_server"
                )
            )

            assert len(results) == 4
            assert "response_times" in results
            assert "concurrent_connections" in results
            assert "resource_usage" in results
            assert "tool_benchmark" in results

            # Verify all tests were called
            mock_response.assert_called_once_with(server_config, "test_server")
            mock_concurrent.assert_called_once_with(
                server_config, "test_server"
            )
            mock_resource.assert_called_once_with(server_config, "test_server")
            mock_benchmark.assert_called_once_with(
                server_config, "test_server"
            )

    def test_get_performance_report_empty(self, performance_tester):
        """Test performance report with no results."""
        report = performance_tester.get_performance_report()

        assert "No performance test results available" in report["message"]

    def test_get_performance_report_with_results(self, performance_tester):
        """Test performance report with results."""
        # Add test results
        metrics1 = PerformanceMetrics()
        metrics1.success_rate = 0.95
        metrics1.avg_response_time = 150.0
        metrics1.throughput_rps = 10.0

        metrics2 = PerformanceMetrics()
        metrics2.success_rate = 0.90
        metrics2.avg_response_time = 200.0
        metrics2.throughput_rps = 8.0

        result1 = LoadTestResult(
            "test1", 5, 30.0, metrics1, performance_grade="A"
        )
        result2 = LoadTestResult(
            "test2", 10, 30.0, metrics2, performance_grade="B"
        )

        performance_tester._test_results = [result1, result2]

        report = performance_tester.get_performance_report()

        assert report["total_tests"] == 2
        assert "A" in report["grade_distribution"]
        assert "B" in report["grade_distribution"]
        assert report["average_performance_score"] > 0
        assert len(report["test_results"]) == 2

    @pytest.mark.asyncio
    async def test_benchmark_single_tool(self, performance_tester):
        """Test single tool benchmarking."""
        mock_toolkit = Mock()
        mock_toolkit.call_tool = AsyncMock()

        metrics = await performance_tester._benchmark_single_tool(
            mock_toolkit, "test_tool", iterations=3
        )

        assert metrics.success_count == 3
        assert len(metrics.response_times) == 3
        assert mock_toolkit.call_tool.call_count == 3

    @pytest.mark.asyncio
    async def test_benchmark_single_tool_with_failures(
        self, performance_tester
    ):
        """Test single tool benchmarking with failures."""
        mock_toolkit = Mock()
        mock_toolkit.call_tool = AsyncMock(
            side_effect=[None, Exception("Error"), None]
        )

        metrics = await performance_tester._benchmark_single_tool(
            mock_toolkit, "test_tool", iterations=3
        )

        assert metrics.success_count == 2
        assert metrics.failure_count == 1
        assert len(metrics.response_times) == 2

    def test_calculate_performance_grade(self, performance_tester):
        """Test performance grade calculation."""
        # Test A grade
        metrics = PerformanceMetrics()
        metrics.avg_response_time = 100.0  # Well below threshold
        metrics.success_rate = 0.99
        metrics.p95_response_time = 150.0

        grade = performance_tester._calculate_performance_grade(metrics)
        assert grade == "A"

        # Test F grade
        metrics.avg_response_time = 5000.0  # Way above threshold
        metrics.success_rate = 0.50  # Below threshold
        metrics.p95_response_time = 8000.0

        grade = performance_tester._calculate_performance_grade(metrics)
        assert grade == "F"

    def test_detect_bottlenecks(self, performance_tester):
        """Test bottleneck detection."""
        metrics = PerformanceMetrics()
        metrics.avg_response_time = 3000.0  # Above threshold (2000ms default)
        metrics.success_rate = 0.80  # Below threshold (0.95 default)
        metrics.p95_response_time = (
            10000.0  # High variability (>3x avg response time: 10000 > 9000)
        )
        metrics.throughput_rps = 0.5  # Low throughput

        bottlenecks = performance_tester._detect_bottlenecks(metrics)

        assert "High average response time" in bottlenecks
        assert "Low success rate" in bottlenecks
        assert "High response time variability" in bottlenecks
        assert "Low throughput" in bottlenecks

    def test_analyze_memory_trend(self, performance_tester):
        """Test memory trend analysis."""
        # Test increasing trend (potential leak)
        increasing_samples = [
            100.0,
            110.0,
            120.0,
            130.0,
            140.0,
            150.0,
            160.0,
            170.0,
            180.0,
            190.0,
        ]
        trend = performance_tester._analyze_memory_trend(increasing_samples)
        assert trend > 0.1  # Should detect significant increase

        # Test stable trend
        stable_samples = [
            100.0,
            102.0,
            98.0,
            101.0,
            99.0,
            100.0,
            103.0,
            97.0,
            101.0,
            100.0,
        ]
        trend = performance_tester._analyze_memory_trend(stable_samples)
        assert abs(trend) < 0.05  # Should be close to zero

        # Test insufficient data
        short_samples = [100.0, 110.0]
        trend = performance_tester._analyze_memory_trend(short_samples)
        assert trend == 0.0


class TestResourceMonitor:
    """Test ResourceMonitor functionality."""

    @pytest.mark.asyncio
    async def test_resource_monitor_lifecycle(self):
        """Test resource monitor start/stop lifecycle."""
        monitor = ResourceMonitor()

        assert monitor.monitoring is False
        assert len(monitor.memory_samples) == 0
        assert len(monitor.cpu_samples) == 0

        # Mock psutil.Process to avoid actual system monitoring
        with patch(
            "mcp_client_cli.testing.performance_tester.psutil.Process"
        ) as mock_process_class:
            mock_process = Mock()
            mock_process.memory_info.return_value.rss = (
                100 * 1024 * 1024
            )  # 100MB
            mock_process.cpu_percent.return_value = 50.0
            mock_process_class.return_value = mock_process

            await monitor.start()
            assert monitor.monitoring is True

            # Let it run briefly
            await asyncio.sleep(0.1)

            data = await monitor.stop()
            assert monitor.monitoring is False

            # Check returned data structure
            assert "peak_memory_mb" in data
            assert "avg_memory_mb" in data
            assert "peak_cpu_percent" in data
            assert "avg_cpu_percent" in data
            assert "memory_samples" in data
            assert "cpu_samples" in data

    @pytest.mark.asyncio
    async def test_resource_monitor_no_data(self):
        """Test resource monitor with no data collected."""
        monitor = ResourceMonitor()

        data = await monitor.stop()

        assert data["peak_memory_mb"] == 0
        assert data["avg_memory_mb"] == 0
        assert data["peak_cpu_percent"] == 0
        assert data["avg_cpu_percent"] == 0
        assert len(data["memory_samples"]) == 0
        assert len(data["cpu_samples"]) == 0


if __name__ == "__main__":
    pytest.main([__file__])
