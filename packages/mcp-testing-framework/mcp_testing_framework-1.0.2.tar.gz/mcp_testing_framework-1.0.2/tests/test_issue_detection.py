"""
Tests for Issue Detection and Remediation System.

This module provides comprehensive tests for the automated issue detection,
remediation, and storage components of the MCP testing framework.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.mcp_client_cli.config import ServerConfig
from src.mcp_client_cli.testing.issue_detector import (
    HealthMetrics,
    Issue,
    IssuePattern,
    IssueSeverity,
    IssueType,
    MCPIssueDetector,
)
from src.mcp_client_cli.testing.issue_storage import IssueTrackingManager
from src.mcp_client_cli.testing.mcp_tester import TestResult, TestStatus
from src.mcp_client_cli.testing.remediation import (
    MCPRemediationEngine,
    RemediationResult,
    RemediationStatus,
    RemediationStrategy,
    RetryConfig,
)


class TestMCPIssueDetector:
    """Test suite for MCPIssueDetector."""

    @pytest.fixture
    def issue_detector(self):
        """Create an issue detector instance."""
        return MCPIssueDetector()

    @pytest.fixture
    def server_config(self):
        """Create a test server configuration."""
        return ServerConfig(
            command="python",
            args=["-m", "test_server"],
            env={"TEST_ENV": "true"},
        )

    @pytest.fixture
    def test_result_connection_failure(self):
        """Create a test result with connection failure."""
        return TestResult(
            test_name="test_server_connectivity",
            status=TestStatus.ERROR,
            confidence_score=0.9,
            execution_time=5.0,
            message="Connection refused",
            error_info="ConnectionRefusedError: [Errno 61] Connection refused",
        )

    @pytest.fixture
    def test_result_timeout(self):
        """Create a test result with timeout."""
        return TestResult(
            test_name="test_server_timeout",
            status=TestStatus.FAILED,
            confidence_score=0.8,
            execution_time=15.0,
            message="Operation timed out",
            error_info="asyncio.TimeoutError: timeout after 10 seconds",
        )

    def test_initialization(self, issue_detector):
        """Test issue detector initialization."""
        assert len(issue_detector._issue_patterns) > 0
        assert isinstance(issue_detector._health_metrics, dict)
        assert isinstance(issue_detector._issue_history, list)

    def test_pattern_initialization(self, issue_detector):
        """Test that issue patterns are properly initialized."""
        patterns = issue_detector._issue_patterns

        # Check that we have patterns for major issue types
        pattern_types = {pattern.issue_type for pattern in patterns}
        expected_types = {
            IssueType.CONNECTION_FAILURE,
            IssueType.TIMEOUT,
            IssueType.AUTHENTICATION_ERROR,
            IssueType.DEPENDENCY_MISSING,
        }

        assert expected_types.issubset(pattern_types)

        # Check pattern structure
        for pattern in patterns:
            assert isinstance(pattern, IssuePattern)
            assert pattern.pattern_id
            assert pattern.error_patterns
            assert 0.0 <= pattern.confidence_base <= 1.0
            assert pattern.remediation_suggestions

    @pytest.mark.asyncio
    async def test_monitor_server_health_success(
        self, issue_detector, server_config
    ):
        """Test successful server health monitoring."""
        # Mock the toolkit creation and session to simulate success
        with patch(
            "src.mcp_client_cli.testing.issue_detector.McpToolkit"
        ) as mock_toolkit:
            mock_instance = AsyncMock()
            mock_instance._start_session = AsyncMock()
            mock_instance.initialize = AsyncMock()
            mock_instance.get_tools = Mock(return_value=["tool1", "tool2"])
            mock_instance.close = AsyncMock()
            mock_toolkit.return_value = mock_instance

            metrics = await issue_detector.monitor_server_health(
                server_config, "test_server"
            )

            assert isinstance(metrics, HealthMetrics)
            assert metrics.server_name == "test_server"
            assert metrics.connection_success_rate > 0.0
            assert metrics.error_count == 0
            assert metrics.last_successful_connection is not None

    @pytest.mark.asyncio
    async def test_monitor_server_health_failure(
        self, issue_detector, server_config
    ):
        """Test server health monitoring with failure."""
        # Mock the toolkit creation to simulate failure
        with patch(
            "src.mcp_client_cli.testing.issue_detector.McpToolkit"
        ) as mock_toolkit:
            mock_instance = AsyncMock()
            mock_instance._start_session = AsyncMock(
                side_effect=Exception("Connection failed")
            )
            mock_instance.close = AsyncMock()
            mock_toolkit.return_value = mock_instance

            metrics = await issue_detector.monitor_server_health(
                server_config, "test_server"
            )

            assert isinstance(metrics, HealthMetrics)
            assert metrics.server_name == "test_server"
            assert metrics.connection_success_rate == 0.0
            assert metrics.error_count > 0
            assert metrics.consecutive_failures > 0

    @pytest.mark.asyncio
    async def test_analyze_test_failures_connection_error(
        self, issue_detector, test_result_connection_failure
    ):
        """Test analysis of connection failure."""
        issues = await issue_detector.analyze_test_failures(
            test_result_connection_failure
        )

        assert len(issues) > 0
        issue = issues[0]
        assert issue.issue_type == IssueType.CONNECTION_FAILURE
        assert issue.confidence_score > 0.5
        assert "Connection refused" in issue.error_message
        assert len(issue.suggested_remediation) > 0

    @pytest.mark.asyncio
    async def test_analyze_test_failures_timeout(
        self, issue_detector, test_result_timeout
    ):
        """Test analysis of timeout failure."""
        issues = await issue_detector.analyze_test_failures(
            test_result_timeout
        )

        assert len(issues) > 0
        issue = issues[0]
        assert issue.issue_type == IssueType.TIMEOUT
        assert issue.confidence_score > 0.5
        assert (
            "timed out" in issue.error_message.lower()
            or "timeout" in issue.error_message.lower()
        )

    @pytest.mark.asyncio
    async def test_analyze_test_failures_unknown_error(self, issue_detector):
        """Test analysis of unknown error."""
        unknown_result = TestResult(
            test_name="test_unknown",
            status=TestStatus.ERROR,
            confidence_score=0.7,
            execution_time=3.0,
            message="Some unknown error occurred",
            error_info="UnknownError: mysterious failure",
        )

        issues = await issue_detector.analyze_test_failures(unknown_result)

        assert len(issues) > 0
        issue = issues[0]
        assert issue.issue_type == IssueType.UNKNOWN_ERROR
        assert issue.confidence_score == 0.6  # Default for unknown errors

    @pytest.mark.asyncio
    async def test_categorize_issues(self, issue_detector):
        """Test issue categorization."""
        # Create test issues
        issues = [
            Issue(
                issue_id="issue1",
                issue_type=IssueType.CONNECTION_FAILURE,
                severity=IssueSeverity.HIGH,
                confidence_score=0.9,
                title="Connection Issue",
                description="Test description",
                server_name="server1",
                test_name="test1",
            ),
            Issue(
                issue_id="issue2",
                issue_type=IssueType.TIMEOUT,
                severity=IssueSeverity.MEDIUM,
                confidence_score=0.8,
                title="Timeout Issue",
                description="Test description",
                server_name="server1",
                test_name="test2",
            ),
        ]

        categories = await issue_detector.categorize_issues(issues)

        assert "by_type" in categories
        assert "by_severity" in categories
        assert "by_server" in categories
        assert "by_confidence" in categories

        assert len(categories["by_type"]["connection_failure"]) == 1
        assert len(categories["by_type"]["timeout"]) == 1
        assert len(categories["by_server"]["server1"]) == 2

    @pytest.mark.asyncio
    async def test_suggest_remediation(self, issue_detector):
        """Test remediation suggestion generation."""
        issue = Issue(
            issue_id="test_issue",
            issue_type=IssueType.CONNECTION_FAILURE,
            severity=IssueSeverity.HIGH,
            confidence_score=0.9,
            title="Connection Issue",
            description="Test description",
            server_name="test_server",
            test_name="test_connectivity",
            error_message="command not found",
            context={"command": "/usr/bin/test_server"},
        )

        suggestions = await issue_detector.suggest_remediation(issue)

        assert len(suggestions) > 0
        assert any(
            "Install the required server executable" in s for s in suggestions
        )

    def test_get_health_metrics(self, issue_detector):
        """Test health metrics retrieval."""
        # Add test metrics
        test_metrics = HealthMetrics(
            server_name="test_server",
            timestamp=datetime.now(),
            connection_success_rate=0.95,
            tool_execution_success_rate=0.90,
            average_response_time=2.5,
            error_count=1,
            warning_count=2,
            uptime_percentage=98.5,
            consecutive_failures=0,
        )
        issue_detector._health_metrics["test_server"] = test_metrics

        # Test single server retrieval
        metrics = issue_detector.get_health_metrics("test_server")
        assert metrics == test_metrics

        # Test all servers retrieval
        all_metrics = issue_detector.get_health_metrics()
        assert "test_server" in all_metrics
        assert all_metrics["test_server"] == test_metrics

    def test_get_issue_history(self, issue_detector):
        """Test issue history retrieval."""
        # Add test issues to history
        issue1 = Issue(
            issue_id="issue1",
            issue_type=IssueType.CONNECTION_FAILURE,
            severity=IssueSeverity.HIGH,
            confidence_score=0.9,
            title="Connection Issue",
            description="Test description",
            server_name="server1",
            test_name="test1",
        )
        issue2 = Issue(
            issue_id="issue2",
            issue_type=IssueType.TIMEOUT,
            severity=IssueSeverity.MEDIUM,
            confidence_score=0.8,
            title="Timeout Issue",
            description="Test description",
            server_name="server2",
            test_name="test2",
        )

        issue_detector._issue_history = [issue1, issue2]

        # Test unfiltered retrieval
        all_issues = issue_detector.get_issue_history()
        assert len(all_issues) == 2

        # Test server name filter
        server1_issues = issue_detector.get_issue_history(
            server_name="server1"
        )
        assert len(server1_issues) == 1
        assert server1_issues[0].server_name == "server1"

        # Test issue type filter
        timeout_issues = issue_detector.get_issue_history(
            issue_type=IssueType.TIMEOUT
        )
        assert len(timeout_issues) == 1
        assert timeout_issues[0].issue_type == IssueType.TIMEOUT


class TestMCPRemediationEngine:
    """Test suite for MCPRemediationEngine."""

    @pytest.fixture
    def issue_detector(self):
        """Create an issue detector instance."""
        return MCPIssueDetector()

    @pytest.fixture
    def remediation_engine(self, issue_detector):
        """Create a remediation engine instance."""
        return MCPRemediationEngine(issue_detector)

    @pytest.fixture
    def server_config(self):
        """Create a test server configuration."""
        return ServerConfig(
            command="python",
            args=["-m", "test_server"],
            env={"TEST_ENV": "true"},
        )

    @pytest.fixture
    def connection_issue(self):
        """Create a connection failure issue."""
        return Issue(
            issue_id="conn_issue_1",
            issue_type=IssueType.CONNECTION_FAILURE,
            severity=IssueSeverity.HIGH,
            confidence_score=0.9,
            title="Connection Failure",
            description="Server connection failed",
            server_name="test_server",
            test_name="connectivity_test",
            error_message="Connection refused",
        )

    def test_initialization(self, remediation_engine):
        """Test remediation engine initialization."""
        assert remediation_engine.issue_detector is not None
        assert len(remediation_engine._remediation_strategies) > 0
        assert isinstance(remediation_engine._remediation_history, list)

    def test_remediation_strategies_initialization(self, remediation_engine):
        """Test that remediation strategies are properly initialized."""
        strategies = remediation_engine._remediation_strategies

        # Check that we have strategies for major issue types
        assert IssueType.CONNECTION_FAILURE in strategies
        assert IssueType.TIMEOUT in strategies
        assert IssueType.AUTHENTICATION_ERROR in strategies

        # Check strategy structure
        for issue_type, actions in strategies.items():
            assert len(actions) > 0
            for action in actions:
                assert action.action_id
                assert action.strategy
                assert action.description
                assert 0.0 <= action.confidence_score <= 1.0
                assert action.estimated_time > 0
                assert action.risk_level in ["low", "medium", "high"]

    @pytest.mark.asyncio
    async def test_remediate_issue_success(
        self, remediation_engine, connection_issue, server_config
    ):
        """Test successful issue remediation."""
        with patch.object(
            remediation_engine, "_test_server_connectivity", return_value=True
        ):
            result = await remediation_engine.remediate_issue(
                connection_issue, server_config
            )

            assert isinstance(result, RemediationResult)
            assert result.issue_id == connection_issue.issue_id
            assert result.status in [
                RemediationStatus.SUCCESS,
                RemediationStatus.PARTIAL_SUCCESS,
            ]

    @pytest.mark.asyncio
    async def test_remediate_issue_no_actions(
        self, remediation_engine, server_config
    ):
        """Test remediation when no actions are available."""
        unknown_issue = Issue(
            issue_id="unknown_issue",
            issue_type=IssueType.UNKNOWN_ERROR,
            severity=IssueSeverity.MEDIUM,
            confidence_score=0.6,
            title="Unknown Issue",
            description="Unknown error",
            server_name="test_server",
            test_name="unknown_test",
        )

        # Clear strategies for unknown error type
        remediation_engine._remediation_strategies[IssueType.UNKNOWN_ERROR] = (
            []
        )

        result = await remediation_engine.remediate_issue(
            unknown_issue, server_config
        )

        assert result.status == RemediationStatus.SKIPPED
        assert "No remediation actions available" in result.message

    @pytest.mark.asyncio
    async def test_retry_strategy(
        self, remediation_engine, connection_issue, server_config
    ):
        """Test retry remediation strategy."""
        # Set up retry config
        retry_config = RetryConfig(max_attempts=2, base_delay=0.1)
        remediation_engine.set_retry_config("test_server", retry_config)

        # Mock connectivity test to succeed on second attempt
        connectivity_results = [False, True]
        with patch.object(
            remediation_engine,
            "_test_server_connectivity",
            side_effect=connectivity_results,
        ):
            # Get retry action
            actions = remediation_engine._get_remediation_actions(
                connection_issue
            )
            retry_action = next(
                (
                    a
                    for a in actions
                    if a.strategy == RemediationStrategy.RETRY
                ),
                None,
            )
            assert retry_action is not None

            result = await remediation_engine._execute_retry_strategy(
                retry_action, connection_issue, server_config
            )

            assert result.status == RemediationStatus.SUCCESS
            assert result.details["attempts"] == 2

    @pytest.mark.asyncio
    async def test_dependency_install_strategy(
        self, remediation_engine, server_config
    ):
        """Test dependency installation strategy."""
        dependency_issue = Issue(
            issue_id="dep_issue",
            issue_type=IssueType.DEPENDENCY_MISSING,
            severity=IssueSeverity.HIGH,
            confidence_score=0.9,
            title="Missing Dependency",
            description="Module not found",
            server_name="test_server",
            test_name="dependency_test",
            error_message="ModuleNotFoundError: No module named 'test_module'",
        )

        with patch.object(
            remediation_engine, "_test_server_connectivity", return_value=True
        ):
            result = await remediation_engine.remediate_issue(
                dependency_issue, server_config
            )

            assert result.status in [
                RemediationStatus.SUCCESS,
                RemediationStatus.PARTIAL_SUCCESS,
            ]
            if result.status == RemediationStatus.SUCCESS:
                assert "test_module" in result.message

    def test_set_retry_config(self, remediation_engine):
        """Test setting retry configuration."""
        config = RetryConfig(max_attempts=5, base_delay=2.0)
        remediation_engine.set_retry_config("test_server", config)

        assert "test_server" in remediation_engine._retry_configs
        assert remediation_engine._retry_configs["test_server"] == config

    def test_get_remediation_history(self, remediation_engine):
        """Test remediation history retrieval."""
        # Add test results to history
        result1 = RemediationResult(
            action_id="action1",
            issue_id="issue1",
            status=RemediationStatus.SUCCESS,
            confidence_score=0.9,
            execution_time=5.0,
            message="Success",
        )
        result2 = RemediationResult(
            action_id="action2",
            issue_id="issue2",
            status=RemediationStatus.FAILED,
            confidence_score=0.7,
            execution_time=3.0,
            message="Failed",
        )

        remediation_engine._remediation_history = [result1, result2]

        # Test unfiltered retrieval
        all_results = remediation_engine.get_remediation_history()
        assert len(all_results) == 2

        # Test filtered by issue ID
        issue1_results = remediation_engine.get_remediation_history(
            issue_id="issue1"
        )
        assert len(issue1_results) == 1
        assert issue1_results[0].issue_id == "issue1"

    def test_get_success_rate(self, remediation_engine):
        """Test success rate calculation."""
        # Add test results to history
        results = [
            RemediationResult(
                "a1", "i1", RemediationStatus.SUCCESS, 0.9, 1.0, "Success"
            ),
            RemediationResult(
                "a2", "i2", RemediationStatus.SUCCESS, 0.8, 2.0, "Success"
            ),
            RemediationResult(
                "a3", "i3", RemediationStatus.FAILED, 0.7, 3.0, "Failed"
            ),
        ]

        remediation_engine._remediation_history = results

        success_rate = remediation_engine.get_success_rate()
        assert success_rate == 2 / 3  # 2 successes out of 3 total


class TestIssueTrackingManager:
    """Test suite for IssueTrackingManager."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        yield db_path
        # Cleanup
        if db_path.exists():
            db_path.unlink()

    @pytest.fixture
    def issue_manager(self, temp_db_path):
        """Create an issue tracking manager with temporary database."""
        return IssueTrackingManager(temp_db_path)

    @pytest.fixture
    def test_issue(self):
        """Create a test issue."""
        return Issue(
            issue_id="test_issue_1",
            issue_type=IssueType.CONNECTION_FAILURE,
            severity=IssueSeverity.HIGH,
            confidence_score=0.9,
            title="Test Connection Issue",
            description="Test description for connection failure",
            server_name="test_server",
            test_name="connectivity_test",
            error_message="Connection refused",
            context={"test_context": "value"},
            suggested_remediation=["Fix connection", "Check server"],
        )

    @pytest.fixture
    def test_remediation_result(self):
        """Create a test remediation result."""
        return RemediationResult(
            action_id="test_action",
            issue_id="test_issue_1",
            status=RemediationStatus.SUCCESS,
            confidence_score=0.8,
            execution_time=5.0,
            message="Remediation successful",
            details={"attempts": 2},
            follow_up_actions=["Monitor server"],
        )

    @pytest.fixture
    def test_health_metrics(self):
        """Create test health metrics."""
        return HealthMetrics(
            server_name="test_server",
            timestamp=datetime.now(),
            connection_success_rate=0.95,
            tool_execution_success_rate=0.90,
            average_response_time=2.5,
            error_count=1,
            warning_count=2,
            uptime_percentage=98.5,
            last_successful_connection=datetime.now(),
            consecutive_failures=0,
        )

    @pytest.mark.asyncio
    async def test_save_and_get_issue(self, issue_manager, test_issue):
        """Test saving and retrieving issues."""
        # Save issue
        await issue_manager.save_issue(test_issue)

        # Retrieve issues
        issues = await issue_manager.get_issues()

        assert len(issues) == 1
        retrieved_issue = issues[0]
        assert retrieved_issue.issue_id == test_issue.issue_id
        assert retrieved_issue.issue_type == test_issue.issue_type
        assert retrieved_issue.server_name == test_issue.server_name
        assert retrieved_issue.context == test_issue.context

    @pytest.mark.asyncio
    async def test_save_and_get_remediation_result(
        self, issue_manager, test_issue, test_remediation_result
    ):
        """Test saving and retrieving remediation results."""
        # Save issue first
        await issue_manager.save_issue(test_issue)

        # Save remediation result
        await issue_manager.save_remediation_result(test_remediation_result)

        # Retrieve results
        results = await issue_manager.get_remediation_results()

        assert len(results) == 1
        retrieved_result = results[0]
        assert retrieved_result.action_id == test_remediation_result.action_id
        assert retrieved_result.issue_id == test_remediation_result.issue_id
        assert retrieved_result.status == test_remediation_result.status
        assert retrieved_result.details == test_remediation_result.details

    @pytest.mark.asyncio
    async def test_save_and_get_health_metrics(
        self, issue_manager, test_health_metrics
    ):
        """Test saving and retrieving health metrics."""
        # Save metrics
        await issue_manager.save_health_metrics(test_health_metrics)

        # Retrieve metrics
        metrics_list = await issue_manager.get_health_metrics()

        assert len(metrics_list) == 1
        retrieved_metrics = metrics_list[0]
        assert retrieved_metrics.server_name == test_health_metrics.server_name
        assert (
            retrieved_metrics.connection_success_rate
            == test_health_metrics.connection_success_rate
        )
        assert retrieved_metrics.error_count == test_health_metrics.error_count

    @pytest.mark.asyncio
    async def test_resolve_issue(self, issue_manager, test_issue):
        """Test resolving an issue."""
        # Save issue
        await issue_manager.save_issue(test_issue)

        # Resolve issue
        success = await issue_manager.resolve_issue(
            test_issue.issue_id, "Fixed by manual intervention"
        )
        assert success

        # Check that issue is marked as resolved
        resolved_issues = await issue_manager.get_issues(status="resolved")
        assert len(resolved_issues) == 1

        # Check that open issues list is empty
        open_issues = await issue_manager.get_issues(status="open")
        assert len(open_issues) == 0

    @pytest.mark.asyncio
    async def test_get_issue_statistics(
        self, issue_manager, test_issue, test_remediation_result
    ):
        """Test getting issue statistics."""
        # Save test data
        await issue_manager.save_issue(test_issue)
        await issue_manager.save_remediation_result(test_remediation_result)

        # Get statistics
        stats = await issue_manager.get_issue_statistics()

        assert stats["total_issues"] == 1
        assert "connection_failure" in stats["issues_by_type"]
        assert "high" in stats["issues_by_severity"]
        assert stats["average_confidence_score"] == test_issue.confidence_score
        assert stats["remediation_success_rate"] == 1.0  # 100% success

    @pytest.mark.asyncio
    async def test_learn_from_pattern(self, issue_manager, test_issue):
        """Test learning from issue patterns."""
        # Learn from successful remediation
        await issue_manager.learn_from_pattern(
            test_issue, remediation_success=True
        )

        # Learn from failed remediation (same pattern)
        await issue_manager.learn_from_pattern(
            test_issue, remediation_success=False
        )

        # Get pattern insights
        insights = await issue_manager.get_pattern_insights()

        assert len(insights["most_common_patterns"]) > 0
        # Should have at least one pattern with 2 occurrences
        assert any(
            pattern["occurrences"] >= 2
            for pattern in insights["most_common_patterns"]
        )

    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, issue_manager, test_issue):
        """Test cleaning up old data."""
        # Save issue and mark as resolved with old timestamp
        await issue_manager.save_issue(test_issue)

        # Manually update resolved timestamp to be old
        import aiosqlite

        async with aiosqlite.connect(issue_manager.db_path) as db:
            await issue_manager._init_db(db)
            old_timestamp = (datetime.now() - timedelta(days=100)).isoformat()
            await db.execute(
                """
                UPDATE issues 
                SET status = 'resolved', resolved_at = ?
                WHERE id = ?
            """,
                (old_timestamp, test_issue.issue_id),
            )
            await db.commit()

        # Cleanup data older than 90 days
        cleanup_result = await issue_manager.cleanup_old_data(
            retention_days=90
        )

        assert cleanup_result["cleaned_issues"] == 1

    @pytest.mark.asyncio
    async def test_filtering_and_pagination(self, issue_manager):
        """Test filtering and pagination of issues."""
        # Create multiple test issues
        issues = []
        for i in range(5):
            issue = Issue(
                issue_id=f"issue_{i}",
                issue_type=(
                    IssueType.CONNECTION_FAILURE
                    if i % 2 == 0
                    else IssueType.TIMEOUT
                ),
                severity=IssueSeverity.HIGH if i < 3 else IssueSeverity.MEDIUM,
                confidence_score=0.8 + i * 0.02,
                title=f"Test Issue {i}",
                description=f"Description {i}",
                server_name=f"server_{i % 2}",  # server_0 or server_1
                test_name=f"test_{i}",
            )
            issues.append(issue)
            await issue_manager.save_issue(issue)

        # Test server name filtering
        server_0_issues = await issue_manager.get_issues(
            server_name="server_0"
        )
        assert len(server_0_issues) == 3  # Issues 0, 2, 4

        # Test issue type filtering
        connection_issues = await issue_manager.get_issues(
            issue_type=IssueType.CONNECTION_FAILURE
        )
        assert len(connection_issues) == 3  # Issues 0, 2, 4

        # Test severity filtering
        high_severity_issues = await issue_manager.get_issues(
            severity=IssueSeverity.HIGH
        )
        assert len(high_severity_issues) == 3  # Issues 0, 1, 2

        # Test pagination
        limited_issues = await issue_manager.get_issues(limit=2)
        assert len(limited_issues) == 2
