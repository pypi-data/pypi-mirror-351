"""
MCP Server Testing Framework.

This package provides comprehensive testing capabilities for MCP servers,
including core testing, security validation, performance benchmarking,
issue detection, and automated remediation.
"""

from .cli_integration import MCPTestCLI
from .issue_detector import (
    HealthMetrics,
    Issue,
    IssuePattern,
    IssueSeverity,
    IssueType,
    MCPIssueDetector,
)
from .issue_storage import IssueTrackingManager
from .mcp_tester import MCPServerTester, TestResult, TestStatus, TestSuite
from .performance_tester import (
    LoadTestResult,
    MCPPerformanceTester,
    PerformanceMetrics,
    PerformanceTestConfig,
    ResourceMonitor,
)
from .remediation import (
    MCPRemediationEngine,
    RemediationAction,
    RemediationResult,
    RemediationStatus,
    RemediationStrategy,
    RetryConfig,
)
from .security_tester import (
    MCPSecurityTester,
    SecurityTestConfig,
    SecurityVulnerability,
)
from .test_storage import TestResultManager

__all__ = [
    # Core Testing
    "MCPServerTester",
    "TestResult",
    "TestStatus",
    "TestSuite",
    "TestResultManager",
    "MCPTestCLI",
    # Security Testing
    "MCPSecurityTester",
    "SecurityTestConfig",
    "SecurityVulnerability",
    # Performance Testing
    "MCPPerformanceTester",
    "PerformanceTestConfig",
    "PerformanceMetrics",
    "LoadTestResult",
    "ResourceMonitor",
    # Issue Detection
    "MCPIssueDetector",
    "Issue",
    "IssueType",
    "IssueSeverity",
    "HealthMetrics",
    "IssuePattern",
    # Automated Remediation
    "MCPRemediationEngine",
    "RemediationResult",
    "RemediationStatus",
    "RemediationStrategy",
    "RemediationAction",
    "RetryConfig",
    # Issue Storage
    "IssueTrackingManager",
]
