"""
CLI Integration for MCP Testing Framework.

This module provides command-line integration for the MCP testing capabilities,
allowing users to run tests directly from the CLI interface.
"""

from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..config import AppConfig
from .mcp_tester import MCPServerTester, TestStatus, TestSuite
from .test_storage import TestResultManager


class MCPTestCLI:
    """
    Command-line interface for MCP testing framework.

    Provides user-friendly commands for running MCP server tests
    and viewing results with rich formatting.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize the MCP Test CLI.

        Args:
            config: Application configuration
        """
        self.config = config
        self.console = Console()
        self.tester = MCPServerTester(config)
        self.storage = TestResultManager()

    async def run_tests(
        self, server_name: Optional[str] = None, save_results: bool = True
    ) -> Dict[str, TestSuite]:
        """
        Run comprehensive tests for MCP servers.

        Args:
            server_name: Optional specific server to test
            save_results: Whether to save results to storage

        Returns:
            Dict[str, TestSuite]: Test results for each server
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:

                if server_name:
                    task = progress.add_task(
                        f"Testing {server_name}...", total=None
                    )
                else:
                    enabled_servers = self.config.get_enabled_servers()
                    task = progress.add_task(
                        f"Testing {len(enabled_servers)} servers...",
                        total=None,
                    )

                # Run tests
                results = await self.tester.run_comprehensive_test_suite(
                    server_name
                )

                progress.update(task, description="Tests completed!")

            # Display results
            self._display_test_results(results)

            # Save results if requested
            if save_results:
                await self._save_results(results)

            return results

        except Exception as e:
            self.console.print(f"[red]Error running tests: {e}[/red]")
            raise
        finally:
            await self.tester.cleanup()

    async def show_test_history(
        self, server_name: Optional[str] = None, limit: int = 10
    ):
        """
        Show test history from storage.

        Args:
            server_name: Optional server name filter
            limit: Maximum number of results to show
        """
        try:
            suites = await self.storage.get_latest_test_suites(
                server_name, limit
            )

            if not suites:
                self.console.print("[yellow]No test history found.[/yellow]")
                return

            self._display_test_history(suites)

        except Exception as e:
            self.console.print(
                f"[red]Error retrieving test history: {e}[/red]"
            )

    async def show_test_statistics(
        self, server_name: Optional[str] = None, days: int = 30
    ):
        """
        Show test statistics.

        Args:
            server_name: Optional server name filter
            days: Number of days to include in statistics
        """
        try:
            stats = await self.storage.get_test_statistics(server_name, days)
            self._display_test_statistics(stats, server_name, days)

        except Exception as e:
            self.console.print(
                f"[red]Error retrieving test statistics: {e}[/red]"
            )

    def _display_test_results(self, results: Dict[str, TestSuite]):
        """Display test results in a formatted table."""
        for server_name, suite in results.items():
            # Create summary panel
            summary_text = (
                f"Server: {suite.server_name}\n"
                f"Total Tests: {suite.total_tests}\n"
                f"Passed: {suite.passed_tests} | "
                f"Failed: {suite.failed_tests} | "
                f"Errors: {suite.error_tests} | "
                f"Skipped: {suite.skipped_tests}\n"
                f"Overall Confidence: {suite.overall_confidence:.2%}\n"
                f"Execution Time: {suite.execution_time:.2f}s"
            )

            # Determine panel color based on results
            if suite.failed_tests == 0 and suite.error_tests == 0:
                panel_style = "green"
                title = f"✅ {server_name} - All Tests Passed"
            elif suite.error_tests > 0:
                panel_style = "red"
                title = f"❌ {server_name} - Tests Failed with Errors"
            else:
                panel_style = "yellow"
                title = f"⚠️ {server_name} - Some Tests Failed"

            panel = Panel(summary_text, title=title, style=panel_style)
            self.console.print(panel)

            # Create detailed results table
            table = Table(title=f"Detailed Results for {server_name}")
            table.add_column("Test Name", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Confidence", justify="right")
            table.add_column("Time (s)", justify="right")
            table.add_column("Message", style="dim")

            for result in suite.results:
                # Format status with color
                if result.status == TestStatus.PASSED:
                    status = "[green]PASSED[/green]"
                elif result.status == TestStatus.FAILED:
                    status = "[red]FAILED[/red]"
                elif result.status == TestStatus.ERROR:
                    status = "[red]ERROR[/red]"
                elif result.status == TestStatus.SKIPPED:
                    status = "[yellow]SKIPPED[/yellow]"
                else:
                    status = str(result.status.value)

                table.add_row(
                    result.test_name,
                    status,
                    f"{result.confidence_score:.2%}",
                    f"{result.execution_time:.3f}",
                    (
                        result.message[:50] + "..."
                        if len(result.message) > 50
                        else result.message
                    ),
                )

            self.console.print(table)
            self.console.print()  # Add spacing

    def _display_test_history(self, suites: list[TestSuite]):
        """Display test history in a formatted table."""
        table = Table(title="Test History")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Server", style="bold")
        table.add_column("Tests", justify="center")
        table.add_column("Passed", justify="center", style="green")
        table.add_column("Failed", justify="center", style="red")
        table.add_column("Confidence", justify="right")
        table.add_column("Duration", justify="right")

        for suite in suites:
            table.add_row(
                suite.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                suite.server_name,
                str(suite.total_tests),
                str(suite.passed_tests),
                str(suite.failed_tests + suite.error_tests),
                f"{suite.overall_confidence:.2%}",
                f"{suite.execution_time:.2f}s",
            )

        self.console.print(table)

    def _display_test_statistics(
        self, stats: Dict[str, Any], server_name: Optional[str], days: int
    ):
        """Display test statistics."""
        title = f"Test Statistics"
        if server_name:
            title += f" for {server_name}"
        title += f" (Last {days} days)"

        # Overall statistics
        overall_text = (
            f"Total Test Suites: {stats['total_suites']}\n"
            f"Success Rate: {stats['success_rate']:.2%}\n"
            f"Average Confidence: {stats['average_confidence']:.2%}\n"
            f"Average Execution Time: {stats['average_execution_time']:.2f}s\n\n"
            f"Test Distribution:\n"
            f"  Passed: {stats['test_distribution']['passed']}\n"
            f"  Failed: {stats['test_distribution']['failed']}\n"
            f"  Errors: {stats['test_distribution']['errors']}"
        )

        panel = Panel(overall_text, title=title, style="blue")
        self.console.print(panel)

        # Server breakdown (if not filtering by server)
        if not server_name and stats["server_breakdown"]:
            table = Table(title="Server Breakdown")
            table.add_column("Server", style="cyan")
            table.add_column("Test Suites", justify="center")
            table.add_column("Success Rate", justify="right")
            table.add_column("Avg Confidence", justify="right")

            for server, server_stats in stats["server_breakdown"].items():
                table.add_row(
                    server,
                    str(server_stats["suite_count"]),
                    f"{server_stats['success_rate']:.2%}",
                    f"{server_stats['average_confidence']:.2%}",
                )

            self.console.print(table)

    async def _save_results(self, results: Dict[str, TestSuite]):
        """Save test results to storage."""
        try:
            for suite in results.values():
                await self.storage.save_test_suite(suite)

            self.console.print(
                "[green]✅ Test results saved to storage.[/green]"
            )

        except Exception as e:
            self.console.print(
                f"[yellow]⚠️ Warning: Could not save test results: {e}[/yellow]"
            )


# CLI command functions that can be integrated into the main CLI
async def run_mcp_tests(
    config: AppConfig,
    server_name: Optional[str] = None,
    save_results: bool = True,
) -> Dict[str, TestSuite]:
    """
    Run MCP server tests from CLI.

    Args:
        config: Application configuration
        server_name: Optional specific server to test
        save_results: Whether to save results to storage

    Returns:
        Dict[str, TestSuite]: Test results
    """
    cli = MCPTestCLI(config)
    return await cli.run_tests(server_name, save_results)


async def show_mcp_test_history(
    config: AppConfig, server_name: Optional[str] = None, limit: int = 10
):
    """
    Show MCP test history from CLI.

    Args:
        config: Application configuration
        server_name: Optional server name filter
        limit: Maximum number of results to show
    """
    cli = MCPTestCLI(config)
    await cli.show_test_history(server_name, limit)


async def show_mcp_test_statistics(
    config: AppConfig, server_name: Optional[str] = None, days: int = 30
):
    """
    Show MCP test statistics from CLI.

    Args:
        config: Application configuration
        server_name: Optional server name filter
        days: Number of days to include in statistics
    """
    cli = MCPTestCLI(config)
    await cli.show_test_statistics(server_name, days)
