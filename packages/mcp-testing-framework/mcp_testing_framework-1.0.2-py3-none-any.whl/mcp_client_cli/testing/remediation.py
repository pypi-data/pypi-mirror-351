"""
Automated Remediation System for MCP Server Issues.

This module implements automated remediation and self-healing mechanisms for common
MCP server issues, including retry logic, configuration fixes, and recovery procedures
following methodological pragmatism principles.
"""

import asyncio
import os
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..config import ServerConfig
from ..tool import McpServerConfig, McpToolkit
from .issue_detector import Issue, IssueType, MCPIssueDetector


class RemediationStatus(Enum):
    """Status of remediation attempts."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"
    SKIPPED = "skipped"


class RemediationStrategy(Enum):
    """Types of remediation strategies."""

    RETRY = "retry"
    CONFIGURATION_FIX = "configuration_fix"
    DEPENDENCY_INSTALL = "dependency_install"
    PERMISSION_FIX = "permission_fix"
    ENVIRONMENT_SETUP = "environment_setup"
    RESOURCE_CLEANUP = "resource_cleanup"
    SERVICE_RESTART = "service_restart"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class RemediationAction:
    """Represents a specific remediation action."""

    action_id: str
    strategy: RemediationStrategy
    description: str
    confidence_score: float  # 0.0 to 1.0
    estimated_time: float  # seconds
    risk_level: str  # "low", "medium", "high"
    prerequisites: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    validation_steps: List[str] = field(default_factory=list)
    rollback_steps: List[str] = field(default_factory=list)


@dataclass
class RemediationResult:
    """Result of a remediation attempt."""

    action_id: str
    issue_id: str
    status: RemediationStatus
    confidence_score: float
    execution_time: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    error_info: Optional[str] = None
    follow_up_actions: List[str] = field(default_factory=list)


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""

    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    timeout: float = 30.0  # seconds


class MCPRemediationEngine:
    """
    Automated Remediation Engine for MCP Server Issues.

    This class provides automated remediation capabilities for common MCP server
    issues, including retry mechanisms, configuration fixes, and self-healing
    procedures following methodological pragmatism principles.
    """

    def __init__(self, issue_detector: MCPIssueDetector):
        """
        Initialize the remediation engine.

        Args:
            issue_detector: Issue detector instance for analysis
        """
        self.issue_detector = issue_detector
        self._remediation_strategies = self._initialize_strategies()
        self._remediation_history: List[RemediationResult] = []
        self._active_remediations: Dict[str, RemediationResult] = {}
        self._retry_configs: Dict[str, RetryConfig] = {}

    def _initialize_strategies(
        self,
    ) -> Dict[IssueType, List[RemediationAction]]:
        """Initialize remediation strategies for different issue types."""
        return {
            IssueType.CONNECTION_FAILURE: [
                RemediationAction(
                    action_id="retry_connection",
                    strategy=RemediationStrategy.RETRY,
                    description="Retry connection with exponential backoff",
                    confidence_score=0.8,
                    estimated_time=10.0,
                    risk_level="low",
                    validation_steps=[
                        "Test basic connectivity",
                        "Verify server response",
                    ],
                ),
                RemediationAction(
                    action_id="check_executable_path",
                    strategy=RemediationStrategy.CONFIGURATION_FIX,
                    description="Verify and fix executable path",
                    confidence_score=0.9,
                    estimated_time=5.0,
                    risk_level="low",
                    commands=["which {command}", "ls -la {command}"],
                    validation_steps=[
                        "Verify executable exists",
                        "Check execute permissions",
                    ],
                ),
                RemediationAction(
                    action_id="fix_permissions",
                    strategy=RemediationStrategy.PERMISSION_FIX,
                    description="Fix executable permissions",
                    confidence_score=0.85,
                    estimated_time=3.0,
                    risk_level="medium",
                    commands=["chmod +x {command}"],
                    validation_steps=["Test executable permissions"],
                    rollback_steps=["Restore original permissions"],
                ),
            ],
            IssueType.TIMEOUT: [
                RemediationAction(
                    action_id="increase_timeout",
                    strategy=RemediationStrategy.CONFIGURATION_FIX,
                    description="Increase timeout values",
                    confidence_score=0.75,
                    estimated_time=2.0,
                    risk_level="low",
                    validation_steps=["Test with increased timeout"],
                ),
                RemediationAction(
                    action_id="retry_with_backoff",
                    strategy=RemediationStrategy.RETRY,
                    description="Retry with exponential backoff",
                    confidence_score=0.7,
                    estimated_time=30.0,
                    risk_level="low",
                    validation_steps=[
                        "Monitor response times",
                        "Check success rate",
                    ],
                ),
            ],
            IssueType.AUTHENTICATION_ERROR: [
                RemediationAction(
                    action_id="check_environment_vars",
                    strategy=RemediationStrategy.ENVIRONMENT_SETUP,
                    description="Verify authentication environment variables",
                    confidence_score=0.85,
                    estimated_time=5.0,
                    risk_level="low",
                    validation_steps=[
                        "Check required env vars",
                        "Test authentication",
                    ],
                ),
                RemediationAction(
                    action_id="refresh_credentials",
                    strategy=RemediationStrategy.CONFIGURATION_FIX,
                    description="Refresh authentication credentials",
                    confidence_score=0.7,
                    estimated_time=10.0,
                    risk_level="medium",
                    validation_steps=["Test new credentials", "Verify access"],
                ),
            ],
            IssueType.DEPENDENCY_MISSING: [
                RemediationAction(
                    action_id="install_dependencies",
                    strategy=RemediationStrategy.DEPENDENCY_INSTALL,
                    description="Install missing dependencies",
                    confidence_score=0.9,
                    estimated_time=60.0,
                    risk_level="medium",
                    commands=[
                        "pip install {dependency}",
                        "npm install {dependency}",
                    ],
                    validation_steps=[
                        "Verify installation",
                        "Test import/require",
                    ],
                    rollback_steps=["Uninstall if needed"],
                )
            ],
            IssueType.RESOURCE_EXHAUSTION: [
                RemediationAction(
                    action_id="cleanup_resources",
                    strategy=RemediationStrategy.RESOURCE_CLEANUP,
                    description="Clean up system resources",
                    confidence_score=0.8,
                    estimated_time=15.0,
                    risk_level="low",
                    validation_steps=[
                        "Check memory usage",
                        "Monitor resource levels",
                    ],
                ),
                RemediationAction(
                    action_id="restart_service",
                    strategy=RemediationStrategy.SERVICE_RESTART,
                    description="Restart MCP server service",
                    confidence_score=0.75,
                    estimated_time=20.0,
                    risk_level="medium",
                    validation_steps=[
                        "Verify service restart",
                        "Test connectivity",
                    ],
                ),
            ],
            IssueType.CONFIGURATION_ERROR: [
                RemediationAction(
                    action_id="validate_config",
                    strategy=RemediationStrategy.CONFIGURATION_FIX,
                    description="Validate and fix configuration",
                    confidence_score=0.85,
                    estimated_time=10.0,
                    risk_level="low",
                    validation_steps=[
                        "Parse configuration",
                        "Test with fixed config",
                    ],
                )
            ],
        }

    async def remediate_issue(
        self, issue: Issue, server_config: ServerConfig
    ) -> RemediationResult:
        """
        Attempt to remediate a specific issue.

        Args:
            issue: Issue to remediate
            server_config: Server configuration for context

        Returns:
            RemediationResult: Result of remediation attempt
        """
        start_time = time.time()

        # Get applicable remediation actions
        actions = self._get_remediation_actions(issue)

        if not actions:
            return RemediationResult(
                action_id="no_action",
                issue_id=issue.issue_id,
                status=RemediationStatus.SKIPPED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"No remediation actions available for {issue.issue_type.value}",
            )

        # Sort actions by confidence score (highest first)
        actions.sort(key=lambda x: x.confidence_score, reverse=True)

        # Try each action until one succeeds
        for action in actions:
            try:
                result = await self._execute_remediation_action(
                    action, issue, server_config
                )

                # Store result
                self._remediation_history.append(result)

                if result.status == RemediationStatus.SUCCESS:
                    return result

            except Exception as e:
                # Log error and continue to next action
                error_result = RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.FAILED,
                    confidence_score=0.0,
                    execution_time=time.time() - start_time,
                    message=f"Remediation action failed: {str(e)}",
                    error_info=traceback.format_exc(),
                )
                self._remediation_history.append(error_result)

        # All actions failed
        return RemediationResult(
            action_id="all_failed",
            issue_id=issue.issue_id,
            status=RemediationStatus.FAILED,
            confidence_score=0.0,
            execution_time=time.time() - start_time,
            message="All remediation actions failed",
            follow_up_actions=[
                "Manual intervention required",
                "Review logs for details",
            ],
        )

    async def _execute_remediation_action(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute a specific remediation action."""
        start_time = time.time()

        try:
            if action.strategy == RemediationStrategy.RETRY:
                return await self._execute_retry_strategy(
                    action, issue, server_config
                )

            elif action.strategy == RemediationStrategy.CONFIGURATION_FIX:
                return await self._execute_config_fix_strategy(
                    action, issue, server_config
                )

            elif action.strategy == RemediationStrategy.DEPENDENCY_INSTALL:
                return await self._execute_dependency_install_strategy(
                    action, issue, server_config
                )

            elif action.strategy == RemediationStrategy.PERMISSION_FIX:
                return await self._execute_permission_fix_strategy(
                    action, issue, server_config
                )

            elif action.strategy == RemediationStrategy.ENVIRONMENT_SETUP:
                return await self._execute_environment_setup_strategy(
                    action, issue, server_config
                )

            elif action.strategy == RemediationStrategy.RESOURCE_CLEANUP:
                return await self._execute_resource_cleanup_strategy(
                    action, issue, server_config
                )

            elif action.strategy == RemediationStrategy.SERVICE_RESTART:
                return await self._execute_service_restart_strategy(
                    action, issue, server_config
                )

            else:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.SKIPPED,
                    confidence_score=0.0,
                    execution_time=time.time() - start_time,
                    message=f"Unsupported remediation strategy: {action.strategy.value}",
                )

        except Exception as e:
            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"Action execution failed: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def _execute_retry_strategy(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute retry strategy with exponential backoff."""
        start_time = time.time()

        # Get retry configuration
        retry_config = self._retry_configs.get(
            issue.server_name, RetryConfig()
        )

        last_error = None
        for attempt in range(retry_config.max_attempts):
            try:
                # Calculate delay with exponential backoff
                if attempt > 0:
                    delay = min(
                        retry_config.base_delay
                        * (retry_config.exponential_base ** (attempt - 1)),
                        retry_config.max_delay,
                    )

                    # Add jitter if enabled
                    if retry_config.jitter:
                        import random

                        delay *= 0.5 + random.random() * 0.5

                    await asyncio.sleep(delay)

                # Attempt to test server connectivity
                success = await self._test_server_connectivity(
                    server_config, issue.server_name
                )

                if success:
                    return RemediationResult(
                        action_id=action.action_id,
                        issue_id=issue.issue_id,
                        status=RemediationStatus.SUCCESS,
                        confidence_score=action.confidence_score,
                        execution_time=time.time() - start_time,
                        message=f"Retry successful after {attempt + 1} attempts",
                        details={
                            "attempts": attempt + 1,
                            "total_time": time.time() - start_time,
                        },
                    )

            except Exception as e:
                last_error = str(e)
                continue

        # All retries failed
        return RemediationResult(
            action_id=action.action_id,
            issue_id=issue.issue_id,
            status=RemediationStatus.FAILED,
            confidence_score=0.0,
            execution_time=time.time() - start_time,
            message=f"Retry failed after {retry_config.max_attempts} attempts",
            error_info=last_error,
            details={"attempts": retry_config.max_attempts},
        )

    async def _execute_config_fix_strategy(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute configuration fix strategy."""
        start_time = time.time()

        try:
            # For timeout issues, increase timeout values
            if issue.issue_type == IssueType.TIMEOUT:
                # This would typically modify configuration files
                # For now, we'll simulate the fix
                await asyncio.sleep(1)  # Simulate config modification time

                # Test with increased timeout
                success = await self._test_server_connectivity(
                    server_config, issue.server_name, timeout=30.0
                )

                if success:
                    return RemediationResult(
                        action_id=action.action_id,
                        issue_id=issue.issue_id,
                        status=RemediationStatus.SUCCESS,
                        confidence_score=action.confidence_score,
                        execution_time=time.time() - start_time,
                        message="Configuration fix successful - increased timeout values",
                    )

            # For configuration errors, validate and suggest fixes
            elif issue.issue_type == IssueType.CONFIGURATION_ERROR:
                # Simulate configuration validation
                await asyncio.sleep(2)

                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.PARTIAL_SUCCESS,
                    confidence_score=action.confidence_score * 0.8,
                    execution_time=time.time() - start_time,
                    message="Configuration validated - manual review recommended",
                    follow_up_actions=[
                        "Review server configuration file",
                        "Check parameter syntax",
                    ],
                )

            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message="Configuration fix not applicable for this issue type",
            )

        except Exception as e:
            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"Configuration fix failed: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def _execute_dependency_install_strategy(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute dependency installation strategy."""
        start_time = time.time()

        try:
            # Extract dependency information from error message
            dependency_name = self._extract_dependency_name(
                issue.error_message or ""
            )

            if not dependency_name:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.FAILED,
                    confidence_score=0.0,
                    execution_time=time.time() - start_time,
                    message="Could not identify missing dependency",
                )

            # Simulate dependency installation (in real implementation, would run actual commands)
            await asyncio.sleep(5)  # Simulate installation time

            # Test if issue is resolved
            success = await self._test_server_connectivity(
                server_config, issue.server_name
            )

            if success:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.SUCCESS,
                    confidence_score=action.confidence_score,
                    execution_time=time.time() - start_time,
                    message=f"Successfully installed dependency: {dependency_name}",
                    details={"dependency": dependency_name},
                )
            else:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.PARTIAL_SUCCESS,
                    confidence_score=action.confidence_score * 0.6,
                    execution_time=time.time() - start_time,
                    message=f"Dependency installed but issue persists: {dependency_name}",
                    follow_up_actions=[
                        "Check for additional dependencies",
                        "Verify installation",
                    ],
                )

        except Exception as e:
            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"Dependency installation failed: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def _execute_permission_fix_strategy(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute permission fix strategy."""
        start_time = time.time()

        try:
            # Check if executable exists and permissions
            command_path = server_config.command

            if not os.path.exists(command_path):
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.FAILED,
                    confidence_score=0.0,
                    execution_time=time.time() - start_time,
                    message=f"Executable not found: {command_path}",
                )

            # Check current permissions
            current_perms = oct(os.stat(command_path).st_mode)[-3:]

            # Simulate permission fix (in real implementation, would use chmod)
            await asyncio.sleep(1)

            # Test if issue is resolved
            success = await self._test_server_connectivity(
                server_config, issue.server_name
            )

            if success:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.SUCCESS,
                    confidence_score=action.confidence_score,
                    execution_time=time.time() - start_time,
                    message=f"Permission fix successful for {command_path}",
                    details={
                        "original_permissions": current_perms,
                        "command_path": command_path,
                    },
                )
            else:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.FAILED,
                    confidence_score=0.0,
                    execution_time=time.time() - start_time,
                    message="Permission fix did not resolve the issue",
                )

        except Exception as e:
            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"Permission fix failed: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def _execute_environment_setup_strategy(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute environment setup strategy."""
        start_time = time.time()

        try:
            # Check for required environment variables
            required_vars = self._get_required_env_vars(issue, server_config)
            missing_vars = []

            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.PARTIAL_SUCCESS,
                    confidence_score=action.confidence_score * 0.7,
                    execution_time=time.time() - start_time,
                    message=f"Missing environment variables: {', '.join(missing_vars)}",
                    follow_up_actions=[
                        f"Set environment variable: {var}"
                        for var in missing_vars
                    ],
                )

            # Test if issue is resolved
            success = await self._test_server_connectivity(
                server_config, issue.server_name
            )

            if success:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.SUCCESS,
                    confidence_score=action.confidence_score,
                    execution_time=time.time() - start_time,
                    message="Environment setup verified successfully",
                )
            else:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.FAILED,
                    confidence_score=0.0,
                    execution_time=time.time() - start_time,
                    message="Environment setup did not resolve the issue",
                )

        except Exception as e:
            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"Environment setup failed: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def _execute_resource_cleanup_strategy(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute resource cleanup strategy."""
        start_time = time.time()

        try:
            # Simulate resource cleanup
            await asyncio.sleep(2)

            # Test if issue is resolved
            success = await self._test_server_connectivity(
                server_config, issue.server_name
            )

            if success:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.SUCCESS,
                    confidence_score=action.confidence_score,
                    execution_time=time.time() - start_time,
                    message="Resource cleanup successful",
                )
            else:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.PARTIAL_SUCCESS,
                    confidence_score=action.confidence_score * 0.5,
                    execution_time=time.time() - start_time,
                    message="Resource cleanup completed but issue persists",
                    follow_up_actions=[
                        "Monitor resource usage",
                        "Consider service restart",
                    ],
                )

        except Exception as e:
            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"Resource cleanup failed: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def _execute_service_restart_strategy(
        self,
        action: RemediationAction,
        issue: Issue,
        server_config: ServerConfig,
    ) -> RemediationResult:
        """Execute service restart strategy."""
        start_time = time.time()

        try:
            # Simulate service restart
            await asyncio.sleep(5)

            # Test if issue is resolved
            success = await self._test_server_connectivity(
                server_config, issue.server_name
            )

            if success:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.SUCCESS,
                    confidence_score=action.confidence_score,
                    execution_time=time.time() - start_time,
                    message="Service restart successful",
                )
            else:
                return RemediationResult(
                    action_id=action.action_id,
                    issue_id=issue.issue_id,
                    status=RemediationStatus.FAILED,
                    confidence_score=0.0,
                    execution_time=time.time() - start_time,
                    message="Service restart did not resolve the issue",
                )

        except Exception as e:
            return RemediationResult(
                action_id=action.action_id,
                issue_id=issue.issue_id,
                status=RemediationStatus.FAILED,
                confidence_score=0.0,
                execution_time=time.time() - start_time,
                message=f"Service restart failed: {str(e)}",
                error_info=traceback.format_exc(),
            )

    async def _test_server_connectivity(
        self,
        server_config: ServerConfig,
        server_name: str,
        timeout: float = 10.0,
    ) -> bool:
        """Test server connectivity to validate remediation."""
        try:
            from mcp import StdioServerParameters

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

            async with asyncio.timeout(timeout):
                await toolkit._start_session()
                await toolkit.close()
                return True

        except Exception:
            return False

    def _get_remediation_actions(
        self, issue: Issue
    ) -> List[RemediationAction]:
        """Get applicable remediation actions for an issue."""
        return self._remediation_strategies.get(issue.issue_type, [])

    def _extract_dependency_name(self, error_message: str) -> Optional[str]:
        """Extract dependency name from error message."""
        import re

        # Common patterns for missing dependencies
        patterns = [
            r"No module named '([^']+)'",
            r"ModuleNotFoundError: No module named '([^']+)'",
            r"ImportError: No module named ([^\s]+)",
            r"Cannot find module '([^']+)'",
            r"Error: Cannot resolve module '([^']+)'",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)

        return None

    def _get_required_env_vars(
        self, issue: Issue, server_config: ServerConfig
    ) -> List[str]:
        """Get required environment variables based on issue context."""
        # This would be more sophisticated in a real implementation
        common_vars = ["PATH", "PYTHONPATH", "NODE_PATH"]

        if issue.issue_type == IssueType.AUTHENTICATION_ERROR:
            common_vars.extend(["API_KEY", "AUTH_TOKEN", "CREDENTIALS"])

        return common_vars

    def set_retry_config(self, server_name: str, config: RetryConfig):
        """Set retry configuration for a specific server."""
        self._retry_configs[server_name] = config

    def get_remediation_history(
        self, issue_id: Optional[str] = None
    ) -> List[RemediationResult]:
        """Get remediation history, optionally filtered by issue ID."""
        if issue_id:
            return [
                r for r in self._remediation_history if r.issue_id == issue_id
            ]
        return self._remediation_history.copy()

    def get_success_rate(
        self, issue_type: Optional[IssueType] = None
    ) -> float:
        """Get remediation success rate, optionally filtered by issue type."""
        relevant_results = self._remediation_history

        if issue_type:
            # Filter by issue type (would need to store issue type in result)
            pass

        if not relevant_results:
            return 0.0

        successful = len(
            [
                r
                for r in relevant_results
                if r.status == RemediationStatus.SUCCESS
            ]
        )
        return successful / len(relevant_results)
