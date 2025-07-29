"""
Automated Issue Detection and Analysis System for MCP Servers.

This module implements comprehensive issue detection capabilities for MCP servers,
including real-time monitoring, failure analysis, and pattern recognition following
methodological pragmatism principles with confidence scoring and error architecture awareness.
"""

import asyncio
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from mcp import StdioServerParameters

from ..config import ServerConfig
from ..tool import McpServerConfig, McpToolkit
from .mcp_tester import TestResult, TestStatus, TestSuite


class IssueType(Enum):
    """Types of issues that can be detected."""

    CONNECTION_FAILURE = "connection_failure"
    TIMEOUT = "timeout"
    AUTHENTICATION_ERROR = "authentication_error"
    TOOL_EXECUTION_ERROR = "tool_execution_error"
    CONFIGURATION_ERROR = "configuration_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PROTOCOL_ERROR = "protocol_error"
    DEPENDENCY_MISSING = "dependency_missing"
    PERMISSION_DENIED = "permission_denied"
    UNKNOWN_ERROR = "unknown_error"


class IssueSeverity(Enum):
    """Severity levels for detected issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Issue:
    """Represents a detected issue with confidence scoring."""

    issue_id: str
    issue_type: IssueType
    severity: IssueSeverity
    confidence_score: float  # 0.0 to 1.0
    title: str
    description: str
    server_name: str
    test_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_remediation: List[str] = field(default_factory=list)
    related_issues: List[str] = field(default_factory=list)


@dataclass
class IssuePattern:
    """Pattern for recognizing common issues."""

    pattern_id: str
    issue_type: IssueType
    severity: IssueSeverity
    error_patterns: List[str]  # Regex patterns
    context_patterns: Dict[str, str] = field(default_factory=dict)
    confidence_base: float = 0.8
    remediation_suggestions: List[str] = field(default_factory=list)


@dataclass
class HealthMetrics:
    """Health metrics for server monitoring."""

    server_name: str
    timestamp: datetime
    connection_success_rate: float
    tool_execution_success_rate: float
    average_response_time: float
    error_count: int
    warning_count: int
    uptime_percentage: float
    last_successful_connection: Optional[datetime] = None
    consecutive_failures: int = 0


class MCPIssueDetector:
    """
    Automated Issue Detection and Analysis System.

    This class provides comprehensive issue detection capabilities for MCP servers,
    including pattern recognition, failure analysis, and health monitoring following
    methodological pragmatism principles.
    """

    def __init__(self):
        """Initialize the issue detector with predefined patterns."""
        self._issue_patterns = self._initialize_patterns()
        self._health_metrics: Dict[str, HealthMetrics] = {}
        self._issue_history: List[Issue] = []
        self._pattern_cache: Dict[str, List[Issue]] = defaultdict(list)

    def _initialize_patterns(self) -> List[IssuePattern]:
        """Initialize predefined issue patterns for common MCP server problems."""
        return [
            # Connection Issues
            IssuePattern(
                pattern_id="connection_refused",
                issue_type=IssueType.CONNECTION_FAILURE,
                severity=IssueSeverity.HIGH,
                error_patterns=[
                    r"[Cc]onnection refused",
                    r"[Cc]onnection.*refused",
                    r"No such file or directory",
                    r"command not found",
                    r"Permission denied.*execute",
                    r"ConnectionRefusedError",
                    r"ConnectionError",
                ],
                confidence_base=0.95,
                remediation_suggestions=[
                    "Verify the server command path is correct",
                    "Check if the server executable has proper permissions",
                    "Ensure the server is installed and accessible",
                    "Verify the working directory exists",
                ],
            ),
            # Timeout Issues
            IssuePattern(
                pattern_id="timeout_error",
                issue_type=IssueType.TIMEOUT,
                severity=IssueSeverity.MEDIUM,
                error_patterns=[
                    r"timeout",
                    r"timed out",
                    r"TimeoutError",
                    r"asyncio\.timeout",
                ],
                confidence_base=0.90,
                remediation_suggestions=[
                    "Increase timeout values in configuration",
                    "Check server performance and resource usage",
                    "Verify network connectivity",
                    "Consider implementing retry mechanisms",
                ],
            ),
            # Authentication Issues
            IssuePattern(
                pattern_id="auth_error",
                issue_type=IssueType.AUTHENTICATION_ERROR,
                severity=IssueSeverity.HIGH,
                error_patterns=[
                    r"authentication failed",
                    r"invalid credentials",
                    r"unauthorized",
                    r"access denied",
                ],
                confidence_base=0.92,
                remediation_suggestions=[
                    "Verify authentication credentials",
                    "Check API keys and tokens",
                    "Ensure proper environment variables are set",
                    "Review server authentication configuration",
                ],
            ),
            # Tool Execution Issues
            IssuePattern(
                pattern_id="tool_execution_error",
                issue_type=IssueType.TOOL_EXECUTION_ERROR,
                severity=IssueSeverity.MEDIUM,
                error_patterns=[
                    r"tool execution failed",
                    r"invalid tool arguments",
                    r"tool not found",
                    r"ToolException",
                ],
                confidence_base=0.85,
                remediation_suggestions=[
                    "Verify tool arguments and schema",
                    "Check tool availability and permissions",
                    "Review tool implementation",
                    "Validate input parameters",
                ],
            ),
            # Configuration Issues
            IssuePattern(
                pattern_id="config_error",
                issue_type=IssueType.CONFIGURATION_ERROR,
                severity=IssueSeverity.HIGH,
                error_patterns=[
                    r"configuration error",
                    r"invalid configuration",
                    r"missing required parameter",
                    r"ConfigurationError",
                ],
                confidence_base=0.88,
                remediation_suggestions=[
                    "Review server configuration file",
                    "Check required parameters are provided",
                    "Validate configuration syntax",
                    "Ensure all dependencies are configured",
                ],
            ),
            # Resource Issues
            IssuePattern(
                pattern_id="resource_exhaustion",
                issue_type=IssueType.RESOURCE_EXHAUSTION,
                severity=IssueSeverity.CRITICAL,
                error_patterns=[
                    r"out of memory",
                    r"memory error",
                    r"resource exhausted",
                    r"too many open files",
                ],
                confidence_base=0.93,
                remediation_suggestions=[
                    "Increase available memory",
                    "Check for memory leaks",
                    "Optimize resource usage",
                    "Implement resource limits and monitoring",
                ],
            ),
            # Protocol Issues
            IssuePattern(
                pattern_id="protocol_error",
                issue_type=IssueType.PROTOCOL_ERROR,
                severity=IssueSeverity.MEDIUM,
                error_patterns=[
                    r"protocol error",
                    r"invalid JSON-RPC",
                    r"malformed request",
                    r"protocol version mismatch",
                ],
                confidence_base=0.87,
                remediation_suggestions=[
                    "Check MCP protocol version compatibility",
                    "Verify JSON-RPC message format",
                    "Review protocol implementation",
                    "Update client or server to compatible version",
                ],
            ),
            # Dependency Issues
            IssuePattern(
                pattern_id="dependency_missing",
                issue_type=IssueType.DEPENDENCY_MISSING,
                severity=IssueSeverity.HIGH,
                error_patterns=[
                    r"module not found",
                    r"import error",
                    r"dependency not installed",
                    r"ModuleNotFoundError",
                ],
                confidence_base=0.91,
                remediation_suggestions=[
                    "Install missing dependencies",
                    "Check package requirements",
                    "Verify Python/Node.js environment",
                    "Update package manager and dependencies",
                ],
            ),
        ]

    async def monitor_server_health(
        self, server_config: ServerConfig, server_name: str
    ) -> HealthMetrics:
        """
        Monitor server health and collect metrics.

        Args:
            server_config: Server configuration to monitor
            server_name: Name identifier for the server

        Returns:
            HealthMetrics: Current health metrics for the server
        """
        start_time = time.time()

        try:
            # Create toolkit for health monitoring
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

            # Test basic connectivity
            connection_success = False
            error_count = 0
            warning_count = 0

            try:
                async with asyncio.timeout(5.0):
                    await toolkit._start_session()
                    connection_success = True
            except Exception as e:
                error_count += 1
                await self._log_health_issue(
                    server_name, "connection_failure", str(e)
                )

            # Test tool discovery if connection successful
            tool_execution_success = False
            if connection_success:
                try:
                    await toolkit.initialize()
                    tools = toolkit.get_tools()
                    tool_execution_success = len(tools) > 0
                    if not tool_execution_success:
                        warning_count += 1
                except Exception as e:
                    error_count += 1
                    await self._log_health_issue(
                        server_name, "tool_discovery_failure", str(e)
                    )

            # Calculate metrics
            response_time = time.time() - start_time

            # Update or create health metrics
            current_metrics = self._health_metrics.get(server_name)
            if current_metrics:
                # Update existing metrics with exponential moving average
                current_metrics.connection_success_rate = (
                    current_metrics.connection_success_rate * 0.8
                    + (1.0 if connection_success else 0.0) * 0.2
                )
                current_metrics.tool_execution_success_rate = (
                    current_metrics.tool_execution_success_rate * 0.8
                    + (1.0 if tool_execution_success else 0.0) * 0.2
                )
                current_metrics.average_response_time = (
                    current_metrics.average_response_time * 0.8
                    + response_time * 0.2
                )
                current_metrics.error_count += error_count
                current_metrics.warning_count += warning_count

                if connection_success:
                    current_metrics.last_successful_connection = datetime.now()
                    current_metrics.consecutive_failures = 0
                else:
                    current_metrics.consecutive_failures += 1

            else:
                # Create new metrics
                current_metrics = HealthMetrics(
                    server_name=server_name,
                    timestamp=datetime.now(),
                    connection_success_rate=1.0 if connection_success else 0.0,
                    tool_execution_success_rate=(
                        1.0 if tool_execution_success else 0.0
                    ),
                    average_response_time=response_time,
                    error_count=error_count,
                    warning_count=warning_count,
                    uptime_percentage=100.0 if connection_success else 0.0,
                    last_successful_connection=(
                        datetime.now() if connection_success else None
                    ),
                    consecutive_failures=0 if connection_success else 1,
                )

            # Update timestamp
            current_metrics.timestamp = datetime.now()
            self._health_metrics[server_name] = current_metrics

            # Cleanup
            try:
                await toolkit.close()
            except:
                pass

            return current_metrics

        except Exception:
            # Create error metrics
            error_metrics = HealthMetrics(
                server_name=server_name,
                timestamp=datetime.now(),
                connection_success_rate=0.0,
                tool_execution_success_rate=0.0,
                average_response_time=time.time() - start_time,
                error_count=1,
                warning_count=0,
                uptime_percentage=0.0,
                consecutive_failures=1,
            )
            self._health_metrics[server_name] = error_metrics
            return error_metrics

    async def analyze_test_failures(
        self, test_results: Union[TestResult, TestSuite, List[TestResult]]
    ) -> List[Issue]:
        """
        Analyze test failures and detect issues using pattern recognition.

        Args:
            test_results: Test results to analyze (single result, suite, or list)

        Returns:
            List[Issue]: Detected issues with confidence scores
        """
        detected_issues = []

        # Normalize input to list of TestResult
        if isinstance(test_results, TestResult):
            results_to_analyze = [test_results]
        elif isinstance(test_results, TestSuite):
            results_to_analyze = test_results.results
        else:
            results_to_analyze = test_results

        for result in results_to_analyze:
            if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                issues = await self._analyze_single_failure(result)
                detected_issues.extend(issues)

        # Group related issues and update confidence scores
        grouped_issues = self._group_related_issues(detected_issues)

        # Store in history
        self._issue_history.extend(grouped_issues)

        return grouped_issues

    async def _analyze_single_failure(
        self, test_result: TestResult
    ) -> List[Issue]:
        """Analyze a single test failure for issues."""
        detected_issues = []

        # Extract error information
        error_text = ""
        if test_result.error_info:
            error_text += test_result.error_info
        if test_result.message:
            error_text += " " + test_result.message

        # Match against known patterns
        for pattern in self._issue_patterns:
            confidence = await self._match_pattern(
                pattern, error_text, test_result
            )

            if confidence > 0.5:  # Threshold for issue detection
                issue = Issue(
                    issue_id=f"{test_result.test_name}_{pattern.pattern_id}_{int(time.time())}",
                    issue_type=pattern.issue_type,
                    severity=pattern.severity,
                    confidence_score=confidence,
                    title=f"{pattern.issue_type.value.replace('_', ' ').title()} in {test_result.test_name}",
                    description=self._generate_issue_description(
                        pattern, test_result, confidence
                    ),
                    server_name=(
                        test_result.test_name.split("_")[0]
                        if "_" in test_result.test_name
                        else "unknown"
                    ),
                    test_name=test_result.test_name,
                    error_message=test_result.message,
                    stack_trace=test_result.error_info,
                    context={
                        "execution_time": test_result.execution_time,
                        "test_status": test_result.status.value,
                        "test_details": test_result.details,
                    },
                    suggested_remediation=pattern.remediation_suggestions.copy(),
                )
                detected_issues.append(issue)

        # If no patterns matched, create generic issue
        if not detected_issues and test_result.status == TestStatus.ERROR:
            generic_issue = Issue(
                issue_id=f"{test_result.test_name}_unknown_{int(time.time())}",
                issue_type=IssueType.UNKNOWN_ERROR,
                severity=IssueSeverity.MEDIUM,
                confidence_score=0.6,
                title=f"Unknown Error in {test_result.test_name}",
                description=f"An unrecognized error occurred during test execution: {test_result.message}",
                server_name=(
                    test_result.test_name.split("_")[0]
                    if "_" in test_result.test_name
                    else "unknown"
                ),
                test_name=test_result.test_name,
                error_message=test_result.message,
                stack_trace=test_result.error_info,
                context={
                    "execution_time": test_result.execution_time,
                    "test_status": test_result.status.value,
                },
                suggested_remediation=[
                    "Review error message and stack trace",
                    "Check server logs for additional information",
                    "Verify server configuration and dependencies",
                    "Consider enabling debug mode for more details",
                ],
            )
            detected_issues.append(generic_issue)

        return detected_issues

    async def _match_pattern(
        self, pattern: IssuePattern, error_text: str, test_result: TestResult
    ) -> float:
        """Match error text against a pattern and return confidence score."""
        base_confidence = pattern.confidence_base

        # Check error patterns
        pattern_matches = 0
        for error_pattern in pattern.error_patterns:
            if re.search(error_pattern, error_text, re.IGNORECASE):
                pattern_matches += 1

        if pattern_matches == 0:
            return 0.0

        # Calculate confidence - if any pattern matches, use base confidence
        # Boost confidence for multiple matches
        if pattern_matches == 1:
            confidence = base_confidence
        else:
            # Multiple matches increase confidence
            match_ratio = min(
                pattern_matches / len(pattern.error_patterns), 1.0
            )
            confidence = (
                base_confidence + (1.0 - base_confidence) * match_ratio * 0.5
            )

        # Adjust confidence based on context
        if (
            test_result.execution_time > 10.0
            and pattern.issue_type == IssueType.TIMEOUT
        ):
            confidence = min(confidence + 0.1, 1.0)

        if test_result.status == TestStatus.ERROR:
            confidence = min(confidence + 0.05, 1.0)

        return confidence

    def _generate_issue_description(
        self, pattern: IssuePattern, test_result: TestResult, confidence: float
    ) -> str:
        """Generate a descriptive issue description."""
        description = f"Detected {pattern.issue_type.value.replace('_', ' ')} with {confidence:.1%} confidence. "
        description += f"Test '{test_result.test_name}' failed with status {test_result.status.value}. "

        if test_result.message:
            description += f"Error message: {test_result.message[:200]}..."

        return description

    def _group_related_issues(self, issues: List[Issue]) -> List[Issue]:
        """Group related issues and update confidence scores."""
        # Simple grouping by issue type and server
        grouped = defaultdict(list)

        for issue in issues:
            key = f"{issue.server_name}_{issue.issue_type.value}"
            grouped[key].append(issue)

        # Update confidence for grouped issues
        final_issues = []
        for group in grouped.values():
            if len(group) == 1:
                final_issues.extend(group)
            else:
                # Merge similar issues and boost confidence
                primary_issue = group[0]
                primary_issue.confidence_score = min(
                    primary_issue.confidence_score + (len(group) - 1) * 0.05,
                    1.0,
                )
                primary_issue.related_issues = [
                    issue.issue_id for issue in group[1:]
                ]
                final_issues.append(primary_issue)

        return final_issues

    async def categorize_issues(
        self, issues: List[Issue]
    ) -> Dict[str, List[Issue]]:
        """
        Categorize issues by type, severity, and other criteria.

        Args:
            issues: List of issues to categorize

        Returns:
            Dict[str, List[Issue]]: Categorized issues
        """
        categories = {
            "by_type": defaultdict(list),
            "by_severity": defaultdict(list),
            "by_server": defaultdict(list),
            "by_confidence": defaultdict(list),
            "recent": [],
            "recurring": [],
        }

        # Categorize by various criteria
        for issue in issues:
            categories["by_type"][issue.issue_type.value].append(issue)
            categories["by_severity"][issue.severity.value].append(issue)
            categories["by_server"][issue.server_name].append(issue)

            # Confidence categories
            if issue.confidence_score >= 0.9:
                categories["by_confidence"]["high"].append(issue)
            elif issue.confidence_score >= 0.7:
                categories["by_confidence"]["medium"].append(issue)
            else:
                categories["by_confidence"]["low"].append(issue)

            # Recent issues (last 24 hours)
            if issue.timestamp > datetime.now() - timedelta(hours=24):
                categories["recent"].append(issue)

        # Find recurring issues
        issue_signatures = Counter()
        for issue in self._issue_history:
            signature = f"{issue.server_name}_{issue.issue_type.value}"
            issue_signatures[signature] += 1

        for issue in issues:
            signature = f"{issue.server_name}_{issue.issue_type.value}"
            if issue_signatures[signature] > 2:  # Occurred more than twice
                categories["recurring"].append(issue)

        return dict(categories)

    async def suggest_remediation(self, issue: Issue) -> List[str]:
        """
        Generate specific remediation suggestions for an issue.

        Args:
            issue: Issue to generate remediation for

        Returns:
            List[str]: Specific remediation suggestions
        """
        suggestions = issue.suggested_remediation.copy()

        # Add context-specific suggestions
        if issue.issue_type == IssueType.CONNECTION_FAILURE:
            if "command not found" in (issue.error_message or "").lower():
                suggestions.insert(
                    0,
                    f"Install the required server executable: {issue.context.get('command', 'unknown')}",
                )

        elif issue.issue_type == IssueType.TIMEOUT:
            if issue.context.get("execution_time", 0) > 30:
                suggestions.insert(
                    0,
                    "Consider implementing asynchronous processing for long-running operations",
                )

        elif issue.issue_type == IssueType.AUTHENTICATION_ERROR:
            suggestions.insert(
                0,
                "Check environment variables and authentication configuration",
            )

        # Add confidence-based suggestions
        if issue.confidence_score < 0.8:
            suggestions.append(
                "This issue detection has lower confidence - manual verification recommended"
            )

        return suggestions

    async def _log_health_issue(
        self, server_name: str, issue_type: str, error_message: str
    ):
        """Log health monitoring issues for tracking."""
        # This could be extended to integrate with logging systems

    def get_health_metrics(
        self, server_name: Optional[str] = None
    ) -> Union[HealthMetrics, Dict[str, HealthMetrics]]:
        """Get health metrics for a specific server or all servers."""
        if server_name:
            return self._health_metrics.get(server_name)
        return self._health_metrics.copy()

    def get_issue_history(
        self,
        server_name: Optional[str] = None,
        issue_type: Optional[IssueType] = None,
        since: Optional[datetime] = None,
    ) -> List[Issue]:
        """Get filtered issue history."""
        filtered_issues = self._issue_history.copy()

        if server_name:
            filtered_issues = [
                i for i in filtered_issues if i.server_name == server_name
            ]

        if issue_type:
            filtered_issues = [
                i for i in filtered_issues if i.issue_type == issue_type
            ]

        if since:
            filtered_issues = [
                i for i in filtered_issues if i.timestamp >= since
            ]

        return filtered_issues
