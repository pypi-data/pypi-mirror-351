"""
Test suite for MCP Security Testing Module.

This module tests the security testing capabilities including authentication,
authorization, input validation, and vulnerability detection.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_client_cli.config import ServerConfig
from mcp_client_cli.testing.mcp_tester import TestStatus
from mcp_client_cli.testing.security_tester import (
    MCPSecurityTester,
    SecurityTestConfig,
    SecurityVulnerability,
)


@pytest.fixture
def security_config():
    """Create a test security configuration."""
    return SecurityTestConfig(
        test_authentication=True,
        test_authorization=True,
        test_input_validation=True,
        test_data_sanitization=True,
        timeout_seconds=10,
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
def security_tester(security_config):
    """Create a security tester instance."""
    return MCPSecurityTester(security_config)


class TestSecurityTestConfig:
    """Test SecurityTestConfig functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SecurityTestConfig()

        assert config.test_authentication is True
        assert config.test_authorization is True
        assert config.test_input_validation is True
        assert config.test_data_sanitization is True
        assert config.timeout_seconds == 30
        assert config.max_payload_size == 1024 * 1024

    def test_custom_config(self):
        """Test custom configuration values."""
        config = SecurityTestConfig(
            test_authentication=False,
            timeout_seconds=60,
            max_payload_size=2048,
        )

        assert config.test_authentication is False
        assert config.timeout_seconds == 60
        assert config.max_payload_size == 2048


class TestSecurityVulnerability:
    """Test SecurityVulnerability data class."""

    def test_vulnerability_creation(self):
        """Test creating a security vulnerability."""
        vuln = SecurityVulnerability(
            vulnerability_type="authentication_bypass",
            severity="high",
            description="Server accepts invalid credentials",
            affected_component="authentication_mechanism",
            test_payload="invalid_token",
            confidence_score=0.85,
        )

        assert vuln.vulnerability_type == "authentication_bypass"
        assert vuln.severity == "high"
        assert vuln.description == "Server accepts invalid credentials"
        assert vuln.affected_component == "authentication_mechanism"
        assert vuln.test_payload == "invalid_token"
        assert vuln.confidence_score == 0.85


class TestMCPSecurityTester:
    """Test MCPSecurityTester functionality."""

    def test_initialization(self, security_config):
        """Test security tester initialization."""
        tester = MCPSecurityTester(security_config)

        assert tester.config == security_config
        assert len(tester._vulnerabilities) == 0

    def test_default_initialization(self):
        """Test security tester with default config."""
        tester = MCPSecurityTester()

        assert isinstance(tester.config, SecurityTestConfig)
        assert tester.config.test_authentication is True

    @pytest.mark.asyncio
    async def test_authentication_test_success(
        self, security_tester, server_config
    ):
        """Test successful authentication testing."""
        with (
            patch.object(
                security_tester,
                "_test_no_credentials",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_invalid_credentials",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_expired_credentials",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_malformed_auth_headers",
                return_value={"secure": True},
            ),
        ):

            result = await security_tester.test_authentication(
                server_config, "test_server"
            )

            assert result.status == TestStatus.PASSED
            assert result.confidence_score == 0.90
            assert "0 vulnerabilities found" in result.message
            assert len(security_tester._vulnerabilities) == 0

    @pytest.mark.asyncio
    async def test_authentication_test_failure(
        self, security_tester, server_config
    ):
        """Test authentication testing with vulnerabilities."""
        with (
            patch.object(
                security_tester,
                "_test_no_credentials",
                return_value={
                    "secure": False,
                    "issue": "Server accepts connections without authentication",
                    "payload": "no_credentials",
                },
            ),
            patch.object(
                security_tester,
                "_test_invalid_credentials",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_expired_credentials",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_malformed_auth_headers",
                return_value={"secure": True},
            ),
        ):

            result = await security_tester.test_authentication(
                server_config, "test_server"
            )

            assert result.status == TestStatus.FAILED
            assert result.confidence_score == 0.80
            assert "1 vulnerabilities found" in result.message
            assert len(security_tester._vulnerabilities) == 1
            assert (
                security_tester._vulnerabilities[0].vulnerability_type
                == "authentication_bypass"
            )

    @pytest.mark.asyncio
    async def test_authentication_test_error(
        self, security_tester, server_config
    ):
        """Test authentication test with error."""
        # Mock the internal authentication test methods to raise exceptions
        with patch.object(
            security_tester,
            "_test_no_credentials",
            side_effect=Exception("Test error"),
        ):
            result = await security_tester.test_authentication(
                server_config, "test_server"
            )

            # When authentication tests encounter exceptions, they should be marked as FAILED
            # (vulnerabilities found) rather than ERROR (system failure)
            assert result.status == TestStatus.FAILED
            assert result.confidence_score >= 0.8
            assert "vulnerabilities found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_authorization_test(self, security_tester, server_config):
        """Test authorization testing."""
        mock_toolkit = Mock()
        mock_toolkit.initialize = AsyncMock()
        mock_toolkit.get_tools.return_value = ["test_tool"]

        with (
            patch(
                "mcp_client_cli.testing.security_tester.McpToolkit",
                return_value=mock_toolkit,
            ),
            patch.object(
                security_tester,
                "_test_privilege_escalation",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_unauthorized_tool_access",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_resource_access_controls",
                return_value={"secure": True},
            ),
        ):

            result = await security_tester.test_authorization(
                server_config, "test_server"
            )

            assert result.status == TestStatus.PASSED
            assert result.confidence_score == 0.88
            assert "0 vulnerabilities found" in result.message

    @pytest.mark.asyncio
    async def test_input_validation_test(self, security_tester, server_config):
        """Test input validation testing."""
        mock_toolkit = Mock()
        mock_toolkit.initialize = AsyncMock()
        mock_toolkit.get_tools.return_value = ["test_tool"]

        with (
            patch(
                "mcp_client_cli.testing.security_tester.McpToolkit",
                return_value=mock_toolkit,
            ),
            patch.object(
                security_tester,
                "_test_tool_with_payload",
                return_value={"vulnerable": False},
            ),
        ):

            result = await security_tester.test_input_validation(
                server_config, "test_server"
            )

            assert result.status == TestStatus.PASSED
            assert result.confidence_score == 0.85
            assert "0 vulnerabilities found" in result.message

    @pytest.mark.asyncio
    async def test_data_sanitization_test(
        self, security_tester, server_config
    ):
        """Test data sanitization testing."""
        with (
            patch.object(
                security_tester,
                "_test_xss_prevention",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_sql_injection_prevention",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_command_injection_prevention",
                return_value={"secure": True},
            ),
            patch.object(
                security_tester,
                "_test_path_traversal_prevention",
                return_value={"secure": True},
            ),
        ):

            result = await security_tester.test_data_sanitization(
                server_config, "test_server"
            )

            assert result.status == TestStatus.PASSED
            assert result.confidence_score == 0.87
            assert "0 vulnerabilities found" in result.message

    @pytest.mark.asyncio
    async def test_comprehensive_security_scan(
        self, security_tester, server_config
    ):
        """Test comprehensive security scan."""
        # Mock all individual test methods
        with (
            patch.object(security_tester, "test_authentication") as mock_auth,
            patch.object(security_tester, "test_authorization") as mock_authz,
            patch.object(
                security_tester, "test_input_validation"
            ) as mock_input,
            patch.object(
                security_tester, "test_data_sanitization"
            ) as mock_sanitization,
        ):

            # Configure mock return values
            mock_auth.return_value = Mock(status=TestStatus.PASSED)
            mock_authz.return_value = Mock(status=TestStatus.PASSED)
            mock_input.return_value = Mock(status=TestStatus.PASSED)
            mock_sanitization.return_value = Mock(status=TestStatus.PASSED)

            results = await security_tester.run_comprehensive_security_scan(
                server_config, "test_server"
            )

            assert len(results) == 4
            assert "authentication" in results
            assert "authorization" in results
            assert "input_validation" in results
            assert "data_sanitization" in results

            # Verify all tests were called
            mock_auth.assert_called_once_with(server_config, "test_server")
            mock_authz.assert_called_once_with(server_config, "test_server")
            mock_input.assert_called_once_with(server_config, "test_server")
            mock_sanitization.assert_called_once_with(
                server_config, "test_server"
            )

    def test_get_vulnerabilities(self, security_tester):
        """Test getting vulnerabilities."""
        # Add some test vulnerabilities
        vuln1 = SecurityVulnerability(
            vulnerability_type="test_vuln_1",
            severity="high",
            description="Test vulnerability 1",
            affected_component="component_1",
        )
        vuln2 = SecurityVulnerability(
            vulnerability_type="test_vuln_2",
            severity="medium",
            description="Test vulnerability 2",
            affected_component="component_2",
        )

        security_tester._vulnerabilities = [vuln1, vuln2]

        vulnerabilities = security_tester.get_vulnerabilities()

        assert len(vulnerabilities) == 2
        assert vulnerabilities[0] == vuln1
        assert vulnerabilities[1] == vuln2

        # Verify it returns a copy
        vulnerabilities.append(
            SecurityVulnerability("test", "low", "test", "test")
        )
        assert len(security_tester._vulnerabilities) == 2

    def test_get_security_report(self, security_tester):
        """Test generating security report."""
        # Add test vulnerabilities
        vuln1 = SecurityVulnerability(
            vulnerability_type="auth_bypass",
            severity="high",
            description="Authentication bypass",
            affected_component="auth",
            confidence_score=0.9,
        )
        vuln2 = SecurityVulnerability(
            vulnerability_type="input_validation",
            severity="medium",
            description="Input validation issue",
            affected_component="input",
            confidence_score=0.8,
        )

        security_tester._vulnerabilities = [vuln1, vuln2]

        report = security_tester.get_security_report()

        assert report["total_vulnerabilities"] == 2
        assert report["by_severity"]["high"] == 1
        assert report["by_severity"]["medium"] == 1
        assert report["by_severity"]["low"] == 0
        assert report["by_severity"]["critical"] == 0

        assert len(report["vulnerabilities"]) == 2
        assert len(report["recommendations"]) > 0

    def test_generate_malicious_payloads(self, security_tester):
        """Test malicious payload generation."""
        payloads = security_tester._generate_malicious_payloads()

        assert "sql_injection" in payloads
        assert "xss_script" in payloads
        assert "command_injection" in payloads
        assert "path_traversal" in payloads
        assert "buffer_overflow" in payloads

        # Verify payload content
        assert "DROP TABLE" in payloads["sql_injection"]
        assert "<script>" in payloads["xss_script"]
        assert "../../../" in payloads["path_traversal"]

    @pytest.mark.asyncio
    async def test_test_tool_with_payload_vulnerable(self, security_tester):
        """Test tool testing with vulnerable response."""
        mock_toolkit = Mock()
        mock_toolkit.call_tool = AsyncMock(
            return_value="Payload: <script>alert('XSS')</script>"
        )

        result = await security_tester._test_tool_with_payload(
            mock_toolkit, "test_tool", "<script>alert('XSS')</script>"
        )

        assert result["vulnerable"] is True
        assert result["severity"] == "high"
        assert "Payload reflected in output" in result["issue"]

    @pytest.mark.asyncio
    async def test_test_tool_with_payload_secure(self, security_tester):
        """Test tool testing with secure response."""
        mock_toolkit = Mock()
        mock_toolkit.call_tool = AsyncMock(return_value="Safe output")

        result = await security_tester._test_tool_with_payload(
            mock_toolkit, "test_tool", "<script>alert('XSS')</script>"
        )

        assert result["vulnerable"] is False

    @pytest.mark.asyncio
    async def test_test_tool_with_payload_validation_error(
        self, security_tester
    ):
        """Test tool testing with validation error."""
        mock_toolkit = Mock()
        mock_toolkit.call_tool = AsyncMock(
            side_effect=Exception("Invalid input")
        )

        result = await security_tester._test_tool_with_payload(
            mock_toolkit, "test_tool", "malicious_payload"
        )

        assert result["vulnerable"] is False  # Validation error is good

    @pytest.mark.asyncio
    async def test_test_tool_with_payload_unexpected_error(
        self, security_tester
    ):
        """Test tool testing with unexpected error."""
        mock_toolkit = Mock()
        mock_toolkit.call_tool = AsyncMock(
            side_effect=Exception("Unexpected error")
        )

        result = await security_tester._test_tool_with_payload(
            mock_toolkit, "test_tool", "malicious_payload"
        )

        assert result["vulnerable"] is True
        assert result["severity"] == "medium"
        assert "Unexpected error" in result["issue"]

    def test_generate_security_recommendations(self, security_tester):
        """Test security recommendation generation."""
        # Add vulnerabilities of different types
        security_tester._vulnerabilities = [
            SecurityVulnerability(
                "authentication_bypass", "high", "Auth bypass", "auth"
            ),
            SecurityVulnerability(
                "input_validation_bypass", "medium", "Input bypass", "input"
            ),
        ]

        recommendations = security_tester._generate_security_recommendations()

        assert "Implement proper authentication mechanisms" in recommendations
        assert "Implement comprehensive input validation" in recommendations
        assert len(recommendations) >= 2

    def test_generate_security_recommendations_no_vulns(self, security_tester):
        """Test security recommendations with no vulnerabilities."""
        recommendations = security_tester._generate_security_recommendations()

        assert len(recommendations) == 1
        assert "Continue regular security testing" in recommendations[0]


if __name__ == "__main__":
    pytest.main([__file__])
