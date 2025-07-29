"""
Core MCP Testing Framework Tests.

This module contains comprehensive tests for the MCP testing infrastructure,
including functional testing capabilities and configuration validation.
"""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_client_cli.config import (
    AppConfig,
    LLMConfig,
    ServerConfig,
    TestConfig,
)
from mcp_client_cli.testing import (
    MCPServerTester,
    TestResult,
    TestStatus,
    TestSuite,
)


@pytest.fixture
def sample_config():
    """Create a sample AppConfig for testing."""
    return AppConfig(
        llm=LLMConfig(model="gpt-4o-mini", provider="openai", temperature=0.0),
        system_prompt="Test system prompt",
        mcp_servers={
            "test-server": ServerConfig(
                command="python",
                args=["examples/python_mcp_server.py"],
                env={},
                enabled=True,
                exclude_tools=[],
                requires_confirmation=[],
            )
        },
        tools_requires_confirmation=[],
        testing=TestConfig(),
    )


@pytest.mark.asyncio
async def test_configuration_validation_valid():
    """Test configuration validation with valid config."""
    config = AppConfig(
        llm=LLMConfig(model="gpt-4o", provider="openai"),
        system_prompt="Test prompt",
        mcp_servers={"test": ServerConfig(command="python", args=[])},
        tools_requires_confirmation=[],
        testing=TestConfig(),
    )

    tester = MCPServerTester(config)
    result = await tester.validate_configuration(config)

    assert result.status == TestStatus.PASSED
    assert result.confidence_score >= 0.85
    assert "Configuration validation passed" in result.message


@pytest.mark.asyncio
async def test_configuration_validation_invalid():
    """Test configuration validation with invalid config."""
    config = AppConfig(
        llm=LLMConfig(model="", provider=""),  # Invalid
        system_prompt="",  # Invalid
        mcp_servers={},  # Invalid
        tools_requires_confirmation=[],
        testing=TestConfig(),
    )

    tester = MCPServerTester(config)
    result = await tester.validate_configuration(config)

    assert result.status == TestStatus.FAILED
    assert result.confidence_score >= 0.90
    assert "Configuration validation failed" in result.message


@pytest.mark.asyncio
async def test_server_connectivity_mock():
    """Test server connectivity with mocked toolkit."""
    config = AppConfig(
        llm=LLMConfig(model="gpt-4o", provider="openai"),
        system_prompt="Test",
        mcp_servers={"test": ServerConfig(command="python", args=[])},
        tools_requires_confirmation=[],
        testing=TestConfig(),
    )

    tester = MCPServerTester(config)
    server_config = config.mcp_servers["test"]

    # Mock successful connection
    with patch(
        "mcp_client_cli.testing.mcp_tester.McpToolkit"
    ) as mock_toolkit_class:
        mock_toolkit = AsyncMock()
        mock_toolkit._start_session = AsyncMock()
        mock_toolkit_class.return_value = mock_toolkit

        result = await tester.test_server_connectivity(server_config, "test")

        assert result.status == TestStatus.PASSED
        assert result.confidence_score == 0.95
        assert "Successfully connected" in result.message


def test_test_result_creation():
    """Test TestResult dataclass creation."""
    result = TestResult(
        test_name="test",
        status=TestStatus.PASSED,
        confidence_score=0.95,
        execution_time=0.1,
        message="Test passed",
    )

    assert result.test_name == "test"
    assert result.status == TestStatus.PASSED
    assert result.confidence_score == 0.95
    assert result.execution_time == 0.1
    assert result.message == "Test passed"


def test_test_suite_creation():
    """Test TestSuite dataclass creation."""
    suite = TestSuite(
        server_name="test-server",
        total_tests=3,
        passed_tests=2,
        failed_tests=1,
        error_tests=0,
        skipped_tests=0,
        overall_confidence=0.85,
        execution_time=1.5,
    )

    assert suite.server_name == "test-server"
    assert suite.total_tests == 3
    assert suite.passed_tests == 2
    assert suite.overall_confidence == 0.85
