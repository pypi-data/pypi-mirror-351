"""Configuration management for the MCP client CLI."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import commentjson

from .const import CONFIG_DIR, CONFIG_FILE


@dataclass
class LLMConfig:
    """Configuration for the LLM model."""

    model: str = "gpt-4o"
    provider: str = "openai"
    api_key: Optional[str] = None
    temperature: float = 0
    base_url: Optional[str] = None

    @classmethod
    def from_dict(cls, config: dict) -> "LLMConfig":
        """Create LLMConfig from dictionary."""
        return cls(
            model=config.get("model", cls.model),
            provider=config.get("provider", cls.provider),
            api_key=config.get(
                "api_key",
                os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")),
            ),
            temperature=config.get("temperature", cls.temperature),
            base_url=config.get("base_url"),
        )


@dataclass
class ServerConfig:
    """Configuration for an MCP server."""

    command: str
    args: List[str] = None
    env: Dict[str, str] = None
    enabled: bool = True
    exclude_tools: List[str] = None
    requires_confirmation: List[str] = None

    @classmethod
    def from_dict(cls, config: dict) -> "ServerConfig":
        """Create ServerConfig from dictionary."""
        return cls(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {}),
            enabled=config.get("enabled", True),
            exclude_tools=config.get("exclude_tools", []),
            requires_confirmation=config.get("requires_confirmation", []),
        )


@dataclass
class TestConfig:
    """Configuration for MCP testing."""

    enabled: bool = True
    timeout: int = 30
    parallel_execution: bool = False
    output_format: str = "table"
    security_tests_enabled: bool = True
    performance_tests_enabled: bool = True
    issue_detection_enabled: bool = True
    auto_remediation_enabled: bool = False
    test_data_retention_days: int = 30
    confidence_threshold: float = 0.7
    max_concurrent_tests: int = 5
    test_environments: List[str] = None
    custom_test_patterns: Dict[str, str] = None

    @classmethod
    def from_dict(cls, config: dict) -> "TestConfig":
        """Create TestConfig from dictionary."""
        return cls(
            enabled=config.get("enabled", cls.enabled),
            timeout=config.get("timeout", cls.timeout),
            parallel_execution=config.get(
                "parallel_execution", cls.parallel_execution
            ),
            output_format=config.get("output_format", cls.output_format),
            security_tests_enabled=config.get(
                "security_tests_enabled", cls.security_tests_enabled
            ),
            performance_tests_enabled=config.get(
                "performance_tests_enabled", cls.performance_tests_enabled
            ),
            issue_detection_enabled=config.get(
                "issue_detection_enabled", cls.issue_detection_enabled
            ),
            auto_remediation_enabled=config.get(
                "auto_remediation_enabled", cls.auto_remediation_enabled
            ),
            test_data_retention_days=config.get(
                "test_data_retention_days", cls.test_data_retention_days
            ),
            confidence_threshold=config.get(
                "confidence_threshold", cls.confidence_threshold
            ),
            max_concurrent_tests=config.get(
                "max_concurrent_tests", cls.max_concurrent_tests
            ),
            test_environments=config.get(
                "test_environments", cls.test_environments or ["local"]
            ),
            custom_test_patterns=config.get(
                "custom_test_patterns", cls.custom_test_patterns or {}
            ),
        )


@dataclass
class AppConfig:
    """Main application configuration."""

    llm: LLMConfig
    system_prompt: str
    mcp_servers: Dict[str, ServerConfig]
    tools_requires_confirmation: List[str]
    testing: TestConfig

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """Load configuration from file."""
        if config_path:
            config_paths = [Path(config_path)]
        else:
            config_paths = [CONFIG_FILE, CONFIG_DIR / "config.json"]

        chosen_path = next(
            (path for path in config_paths if os.path.exists(path)), None
        )

        if chosen_path is None:
            raise FileNotFoundError(
                f"Could not find config file in any of: {', '.join(map(str, config_paths))}"
            )

        with open(chosen_path, "r") as f:
            config = commentjson.load(f)

        # Extract tools requiring confirmation
        tools_requires_confirmation = []
        for server_config in config["mcpServers"].values():
            tools_requires_confirmation.extend(
                server_config.get("requires_confirmation", [])
            )

        return cls(
            llm=LLMConfig.from_dict(config.get("llm", {})),
            system_prompt=config["systemPrompt"],
            mcp_servers={
                name: ServerConfig.from_dict(server_config)
                for name, server_config in config["mcpServers"].items()
            },
            tools_requires_confirmation=tools_requires_confirmation,
            testing=TestConfig.from_dict(config.get("testing", {})),
        )

    def get_enabled_servers(self) -> Dict[str, ServerConfig]:
        """Get only enabled server configurations."""
        return {
            name: config
            for name, config in self.mcp_servers.items()
            if config.enabled
        }

    def get_test_config(self) -> TestConfig:
        """Get testing configuration."""
        return self.testing

    def save_test_config(
        self, test_config: TestConfig, config_path: Optional[str] = None
    ) -> None:
        """Save updated test configuration to file."""
        if config_path:
            target_path = Path(config_path)
        else:
            config_paths = [CONFIG_FILE, CONFIG_DIR / "config.json"]
            target_path = next(
                (path for path in config_paths if os.path.exists(path)),
                config_paths[0],
            )

        # Load existing config
        if os.path.exists(target_path):
            with open(target_path, "r") as f:
                config = commentjson.load(f)
        else:
            config = {}

        # Update testing section
        config["testing"] = {
            "enabled": test_config.enabled,
            "timeout": test_config.timeout,
            "parallel_execution": test_config.parallel_execution,
            "output_format": test_config.output_format,
            "security_tests_enabled": test_config.security_tests_enabled,
            "performance_tests_enabled": test_config.performance_tests_enabled,
            "issue_detection_enabled": test_config.issue_detection_enabled,
            "auto_remediation_enabled": test_config.auto_remediation_enabled,
            "test_data_retention_days": test_config.test_data_retention_days,
            "confidence_threshold": test_config.confidence_threshold,
            "max_concurrent_tests": test_config.max_concurrent_tests,
            "test_environments": test_config.test_environments,
            "custom_test_patterns": test_config.custom_test_patterns,
        }

        # Save updated config
        with open(target_path, "w") as f:
            commentjson.dump(config, f, indent=2)
