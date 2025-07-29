"""
mcp-testing-framework: Comprehensive testing framework for Model Context
Protocol (MCP) servers

Enhanced fork of mcp-client-cli with advanced testing capabilities.
Author: Tosin Akinosho (tosin@decisioncrafters.com)
"""

__version__ = "1.0.0"
__author__ = "Tosin Akinosho"
__email__ = "tosin@decisioncrafters.com"
__description__ = (
    "Comprehensive testing framework for Model Context Protocol (MCP) servers"
)

# Package metadata
__package_name__ = "mcp-testing-framework"
__original_project__ = "mcp-client-cli"
__license__ = "MIT"

# Export main components
from .cli import main
from .config import AppConfig, ServerConfig
from .testing.mcp_tester import MCPServerTester

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "main",
    "AppConfig",
    "ServerConfig",
    "MCPServerTester",
]
