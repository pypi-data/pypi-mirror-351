#!/usr/bin/env python3

"""
Simple llm CLI that acts as MCP client.
"""

import argparse
import asyncio
import base64
import json
import mimetypes
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, TypedDict

import anyio
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep
from langgraph.prebuilt import create_react_agent
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import AppConfig
from .const import *
from .input import *
from .memory import *
from .output import *
from .prompt import *
from .storage import *
from .testing import (
    IssueTrackingManager,
    MCPIssueDetector,
    MCPPerformanceTester,
    MCPSecurityTester,
    MCPServerTester,
    MCPTestCLI,
    TestResult,
    TestStatus,
)
from .tool import *


# The AgentState class is used to maintain the state of the agent during a conversation.
class AgentState(TypedDict):
    # A list of messages exchanged in the conversation.
    messages: Annotated[list[BaseMessage], add_messages]
    # A flag indicating whether the current step is the last step in the conversation.
    is_last_step: IsLastStep
    # The current date and time, used for context in the conversation.
    today_datetime: str
    # The user's memories.
    memories: str = "no memories"
    remaining_steps: int = 5


async def run() -> None:
    """Run the LLM agent."""
    args = setup_argument_parser()
    query, is_conversation_continuation = parse_query(args)

    # Load configuration (with custom test config if provided)
    if args.test_config and hasattr(args, "test_config"):
        app_config = AppConfig.load(args.test_config)
    else:
        app_config = AppConfig.load()

    if args.list_tools:
        await handle_list_tools(app_config, args)
        return

    if args.show_memories:
        await handle_show_memories()
        return

    if args.list_prompts:
        handle_list_prompts()
        return

    # Handle testing commands
    if args.test_mcp_servers:
        await handle_test_mcp_servers(app_config, args)
        return

    if args.run_test_suite:
        await handle_run_test_suite(app_config, args)
        return

    if args.generate_test_report:
        await handle_generate_test_report(app_config, args)
        return

    await handle_conversation(
        args, query, is_conversation_continuation, app_config
    )


def setup_argument_parser() -> argparse.Namespace:
    """Setup and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Run LangChain agent with MCP tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  llm "What is the capital of France?"     Ask a simple question
  llm c "tell me more"                     Continue previous conversation
  llm p review                             Use a prompt template
  cat file.txt | llm                       Process input from a file
  llm --list-tools                         Show available tools
  llm --list-prompts                       Show available prompt templates
  llm --no-confirmations "search web"      Run tools without confirmation
  llm --test-mcp-servers                   Test all configured MCP servers
  llm --run-test-suite functional          Run specific test suite
  llm --test-config config.json           Use custom test configuration
  llm --generate-test-report               Generate comprehensive test report
        """,
    )
    parser.add_argument(
        "query",
        nargs="*",
        default=[],
        help="The query to process (default: read from stdin). "
        "Special prefixes:\n"
        "  c: Continue previous conversation\n"
        "  p: Use prompt template",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available LLM tools",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List all available prompts",
    )
    parser.add_argument(
        "--no-confirmations",
        action="store_true",
        help="Bypass tool confirmation requirements",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh of tools capabilities",
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Print output as raw text instead of parsing markdown",
    )
    parser.add_argument(
        "--no-tools", action="store_true", help="Do not add any tools"
    )
    parser.add_argument(
        "--no-intermediates",
        action="store_true",
        help="Only print the final message",
    )
    parser.add_argument(
        "--show-memories", action="store_true", help="Show user memories"
    )
    parser.add_argument(
        "--model", help="Override the model specified in config"
    )

    # Testing-related arguments
    parser.add_argument(
        "--test-mcp-servers",
        action="store_true",
        help="Test all configured MCP servers",
    )
    parser.add_argument(
        "--run-test-suite",
        choices=[
            "functional",
            "security",
            "performance",
            "integration",
            "all",
        ],
        help="Run specific test suite type",
    )
    parser.add_argument(
        "--test-config", help="Path to custom test configuration file"
    )
    parser.add_argument(
        "--generate-test-report",
        action="store_true",
        help="Generate comprehensive test report",
    )
    parser.add_argument(
        "--test-output-format",
        choices=["table", "json", "html"],
        default="table",
        help="Output format for test results",
    )
    parser.add_argument(
        "--test-timeout",
        type=int,
        default=30,
        help="Timeout for individual tests in seconds",
    )
    parser.add_argument(
        "--test-parallel",
        action="store_true",
        help="Run tests in parallel when possible",
    )

    return parser.parse_args()


async def handle_list_tools(
    app_config: AppConfig, args: argparse.Namespace
) -> None:
    """Handle the --list-tools command."""
    server_configs = [
        McpServerConfig(
            server_name=name,
            server_param=StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env={**(config.env or {}), **os.environ},
            ),
            exclude_tools=config.exclude_tools or [],
        )
        for name, config in app_config.get_enabled_servers().items()
    ]
    toolkits, tools = await load_tools(
        server_configs, args.no_tools, args.force_refresh
    )

    console = Console()
    table = Table(title="Available LLM Tools")
    table.add_column("Toolkit", style="cyan")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Description", style="green")

    for tool in tools:
        if isinstance(tool, McpTool):
            table.add_row(tool.toolkit_name, tool.name, tool.description)

    console.print(table)

    for toolkit in toolkits:
        await toolkit.close()


async def handle_show_memories() -> None:
    """Handle the --show-memories command."""
    store = SqliteStore(SQLITE_DB)
    memories = await get_memories(store)
    console = Console()
    table = Table(title="My LLM Memories")
    for memory in memories:
        table.add_row(memory)
    console.print(table)


def handle_list_prompts() -> None:
    """Handle the --list-prompts command."""
    console = Console()
    table = Table(title="Available Prompt Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Template")
    table.add_column("Arguments")

    for name, template in prompt_templates.items():
        table.add_row(
            name, template, ", ".join(re.findall(r"\{(\w+)\}", template))
        )

    console.print(table)


async def load_tools(
    server_configs: list[McpServerConfig], no_tools: bool, force_refresh: bool
) -> tuple[list, list]:
    """Load and convert MCP tools to LangChain tools."""
    if no_tools:
        return [], []

    toolkits = []
    langchain_tools = []

    async def convert_toolkit(server_config: McpServerConfig):
        toolkit = await convert_mcp_to_langchain_tools(
            server_config, force_refresh
        )
        toolkits.append(toolkit)
        langchain_tools.extend(toolkit.get_tools())

    async with anyio.create_task_group() as tg:
        for server_param in server_configs:
            tg.start_soon(convert_toolkit, server_param)

    langchain_tools.append(save_memory)
    return toolkits, langchain_tools


async def handle_conversation(
    args: argparse.Namespace,
    query: HumanMessage,
    is_conversation_continuation: bool,
    app_config: AppConfig,
) -> None:
    """Handle the main conversation flow."""
    server_configs = [
        McpServerConfig(
            server_name=name,
            server_param=StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env={**(config.env or {}), **os.environ},
            ),
            exclude_tools=config.exclude_tools or [],
        )
        for name, config in app_config.get_enabled_servers().items()
    ]
    toolkits, tools = await load_tools(
        server_configs, args.no_tools, args.force_refresh
    )

    extra_body = {}
    if app_config.llm.base_url and "openrouter" in app_config.llm.base_url:
        extra_body = {"transforms": ["middle-out"]}
    # Override model if specified in command line
    if args.model:
        app_config.llm.model = args.model

    model: BaseChatModel = init_chat_model(
        model=app_config.llm.model,
        model_provider=app_config.llm.provider,
        api_key=app_config.llm.api_key,
        temperature=app_config.llm.temperature,
        base_url=app_config.llm.base_url,
        default_headers={
            "X-Title": "mcp-client-cli",
            "HTTP-Referer": "https://github.com/adhikasp/mcp-client-cli",
        },
        extra_body=extra_body,
    )

    conversation_manager = ConversationManager(SQLITE_DB)

    checkpointer = MemorySaver()
    store = SqliteStore(SQLITE_DB)
    memories = await get_memories(store)
    formatted_memories = "\n".join(f"- {memory}" for memory in memories)
    agent_executor = create_react_agent(
        model,
        tools,
        state_schema=AgentState,
        checkpointer=checkpointer,
        store=store,
    )

    thread_id = (
        await conversation_manager.get_last_id()
        if is_conversation_continuation
        else uuid.uuid4().hex
    )

    input_messages = AgentState(
        messages=[query],
        today_datetime=datetime.now().isoformat(),
        memories=formatted_memories,
        remaining_steps=3,
    )

    output = OutputHandler(
        text_only=args.text_only, only_last_message=args.no_intermediates
    )
    output.start()
    try:
        async for chunk in agent_executor.astream(
            input_messages,
            stream_mode=["messages", "values"],
            config={
                "configurable": {"thread_id": thread_id, "user_id": "myself"},
                "recursion_limit": 100,
            },
        ):
            output.update(chunk)
            if not args.no_confirmations:
                if not output.confirm_tool_call(app_config.__dict__, chunk):
                    break
    except Exception as e:
        output.update_error(e)
    finally:
        output.finish()

    await conversation_manager.save_id(
        thread_id, None
    )  # MemorySaver doesn't have a conn attribute

    for toolkit in toolkits:
        await toolkit.close()


def parse_query(args: argparse.Namespace) -> tuple[HumanMessage, bool]:
    """
    Parse the query from command line arguments.
    Returns a tuple of (HumanMessage, is_conversation_continuation).
    """
    query_parts = " ".join(args.query).split()
    stdin_content = ""
    stdin_image = None
    is_continuation = False

    # Handle clipboard content if requested
    if query_parts and query_parts[0] == "cb":
        # Remove 'cb' from query parts
        query_parts = query_parts[1:]
        # Try to get content from clipboard
        clipboard_result = get_clipboard_content()
        if clipboard_result:
            content, mime_type = clipboard_result
            if mime_type:  # It's an image
                stdin_image = base64.b64encode(content).decode("utf-8")
            else:  # It's text
                stdin_content = content
        else:
            print("No content found in clipboard")
            raise Exception("Clipboard is empty")
    # Check if there's input from pipe
    elif not sys.stdin.isatty():
        stdin_data = sys.stdin.buffer.read()
        # Try to detect if it's an image by checking magic bytes
        image_type = None
        mime_type = None
        
        if stdin_data.startswith(b'\xff\xd8\xff'):
            image_type = 'jpeg'
            mime_type = 'image/jpeg'
        elif stdin_data.startswith(b'\x89PNG\r\n\x1a\n'):
            image_type = 'png'
            mime_type = 'image/png'
        elif stdin_data.startswith(b'GIF87a') or stdin_data.startswith(b'GIF89a'):
            image_type = 'gif'
            mime_type = 'image/gif'
        elif stdin_data.startswith(b'RIFF') and b'WEBP' in stdin_data[:12]:
            image_type = 'webp'
            mime_type = 'image/webp'
        
        if image_type:
            # It's an image, encode it as base64
            stdin_image = base64.b64encode(stdin_data).decode("utf-8")
        else:
            # It's text
            stdin_content = stdin_data.decode("utf-8").strip()

    # Process the query text
    query_text = ""
    if query_parts:
        if query_parts[0] == "c":
            is_continuation = True
            query_text = " ".join(query_parts[1:])
        elif query_parts[0] == "p" and len(query_parts) >= 2:
            template_name = query_parts[1]
            if template_name not in prompt_templates:
                print(f"Error: Prompt template '{template_name}' not found.")
                print(
                    "Available templates:", ", ".join(prompt_templates.keys())
                )
                return HumanMessage(content=""), False

            template = prompt_templates[template_name]
            template_args = query_parts[2:]
            try:
                # Extract variable names from the template
                var_names = re.findall(r"\{(\w+)\}", template)
                # Create dict mapping parameter names to arguments
                template_vars = dict(zip(var_names, template_args))
                query_text = template.format(**template_vars)
            except KeyError as e:
                print(f"Error: Missing argument {e}")
                return HumanMessage(content=""), False
        else:
            query_text = " ".join(query_parts)

    # Combine stdin content with query text if both exist
    if stdin_content and query_text:
        query_text = f"{stdin_content}\n\n{query_text}"
    elif stdin_content:
        query_text = stdin_content
    elif not query_text and not stdin_image:
        return HumanMessage(content=""), False

    # Create the message content
    if stdin_image:
        content = [
            {
                "type": "text",
                "text": query_text or "What do you see in this image?",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{stdin_image}"},
            },
        ]
    else:
        content = query_text

    return HumanMessage(content=content), is_continuation


def main() -> None:
    """Entry point of the script."""
    asyncio.run(run())


async def handle_test_mcp_servers(
    app_config: AppConfig, args: argparse.Namespace
) -> None:
    """Handle the --test-mcp-servers command."""
    console = Console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Testing MCP servers...", total=None)

        # Get server configurations
        server_configs = [
            McpServerConfig(
                server_name=name,
                server_param=StdioServerParameters(
                    command=config.command,
                    args=config.args or [],
                    env={**(config.env or {}), **os.environ},
                ),
                exclude_tools=config.exclude_tools or [],
            )
            for name, config in app_config.get_enabled_servers().items()
        ]

        if not server_configs:
            console.print(
                "[yellow]No enabled MCP servers found in configuration[/yellow]"
            )
            return

        # Initialize tester
        tester = MCPServerTester(app_config)
        MCPTestCLI(app_config)

        # Run tests for each server
        all_results = []
        for server_config in server_configs:
            progress.update(
                task, description=f"Testing {server_config.server_name}..."
            )

            try:
                # Run comprehensive test suite
                test_suites = await tester.run_comprehensive_test_suite(
                    server_config.server_name
                )

                # Extract all results from test suites
                for suite in test_suites.values():
                    all_results.extend(suite.results)

            except Exception as e:
                error_result = TestResult(
                    test_name=f"{server_config.server_name}_error",
                    status=TestStatus.ERROR,
                    message=str(e),
                    confidence_score=0.95,
                    execution_time=0.0,
                )
                all_results.append(error_result)

    # Display results
    await _display_test_results(all_results, args.test_output_format, console)


async def handle_run_test_suite(
    app_config: AppConfig, args: argparse.Namespace
) -> None:
    """Handle the --run-test-suite command."""
    console = Console()
    suite_type = args.run_test_suite

    console.print(f"[bold blue]Running {suite_type} test suite...[/bold blue]")

    # Get server configurations
    server_configs = [
        McpServerConfig(
            server_name=name,
            server_param=StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env={**(config.env or {}), **os.environ},
            ),
            exclude_tools=config.exclude_tools or [],
        )
        for name, config in app_config.get_enabled_servers().items()
    ]

    if not server_configs:
        console.print(
            "[yellow]No enabled MCP servers found in configuration[/yellow]"
        )
        return

    all_results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        for server_config in server_configs:
            task = progress.add_task(
                f"Testing {server_config.server_name}...", total=None
            )

            try:
                if suite_type in ["functional", "all"]:
                    progress.update(
                        task,
                        description=f"Running functional tests for {server_config.server_name}...",
                    )
                    tester = MCPServerTester(app_config)
                    test_suites = await tester.run_comprehensive_test_suite(
                        server_config.server_name
                    )
                    # Extract functional results from test suites
                    for suite in test_suites.values():
                        all_results.extend(suite.results)

                if suite_type in ["security", "all"]:
                    progress.update(
                        task,
                        description=f"Running security tests for {server_config.server_name}...",
                    )
                    security_tester = MCPSecurityTester()
                    results = await security_tester.run_security_tests(
                        server_config
                    )
                    all_results.extend(results)

                if suite_type in ["performance", "all"]:
                    progress.update(
                        task,
                        description=f"Running performance tests for {server_config.server_name}...",
                    )
                    perf_tester = MCPPerformanceTester()
                    results = await perf_tester.run_performance_tests(
                        server_config
                    )
                    all_results.extend(results)

                if suite_type in ["integration", "all"]:
                    progress.update(
                        task,
                        description=f"Running integration tests for {server_config.server_name}...",
                    )
                    tester = MCPServerTester(app_config)
                    test_suites = await tester.run_comprehensive_test_suite(
                        server_config.server_name
                    )
                    # Extract results from test suites for integration testing
                    for suite in test_suites.values():
                        all_results.extend(suite.results)

            except Exception as e:
                error_result = TestResult(
                    test_name=f"{server_config.server_name}_{suite_type}_error",
                    status=TestStatus.ERROR,
                    error_message=str(e),
                    server_name=server_config.server_name,
                    confidence_score=0.95,
                )
                all_results.append(error_result)

    # Display results
    await _display_test_results(all_results, args.test_output_format, console)

    # Run issue detection if there are failures
    failed_results = [
        r
        for r in all_results
        if r.status in [TestStatus.FAILED, TestStatus.ERROR]
    ]
    if failed_results:
        console.print(
            "\n[yellow]Analyzing failures for potential issues...[/yellow]"
        )
        issue_detector = MCPIssueDetector()

        for result in failed_results:
            issues = await issue_detector.analyze_test_failures(result)
            if issues:
                console.print(
                    f"\n[red]Issues detected for {result.test_name}:[/red]"
                )
                for issue in issues:
                    console.print(
                        f"  • {issue.issue_type.value}: {issue.error_message}"
                    )
                    if issue.remediation_suggestions:
                        console.print(
                            f"    Suggestions: {', '.join(issue.remediation_suggestions[:2])}"
                        )


async def handle_generate_test_report(
    app_config: AppConfig, args: argparse.Namespace
) -> None:
    """Handle the --generate-test-report command."""
    console = Console()

    console.print(
        "[bold blue]Generating comprehensive test report...[/bold blue]"
    )

    # Get server configurations
    server_configs = [
        McpServerConfig(
            server_name=name,
            server_param=StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env={**(config.env or {}), **os.environ},
            ),
            exclude_tools=config.exclude_tools or [],
        )
        for name, config in app_config.get_enabled_servers().items()
    ]

    if not server_configs:
        console.print(
            "[yellow]No enabled MCP servers found in configuration[/yellow]"
        )
        return

    # Run comprehensive tests
    all_results = []
    issue_tracking = IssueTrackingManager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        for server_config in server_configs:
            task = progress.add_task(
                f"Comprehensive testing of {server_config.server_name}...",
                total=None,
            )

            try:
                # Functional tests
                progress.update(
                    task,
                    description=f"Functional tests - {server_config.server_name}...",
                )
                tester = MCPServerTester(app_config)
                test_suites = await tester.run_comprehensive_test_suite(
                    server_config.server_name
                )
                # Extract functional results from test suites
                for suite in test_suites.values():
                    all_results.extend(suite.results)

                # Security tests
                progress.update(
                    task,
                    description=f"Security tests - {server_config.server_name}...",
                )
                security_tester = MCPSecurityTester()
                sec_results = await security_tester.run_security_tests(
                    server_config
                )
                all_results.extend(sec_results)

                # Performance tests
                progress.update(
                    task,
                    description=f"Performance tests - {server_config.server_name}...",
                )
                perf_tester = MCPPerformanceTester()
                perf_results = await perf_tester.run_performance_tests(
                    server_config
                )
                all_results.extend(perf_results)

                # Issue detection and tracking
                progress.update(
                    task,
                    description=f"Issue analysis - {server_config.server_name}...",
                )
                issue_detector = MCPIssueDetector()
                failed_results = [
                    r
                    for r in all_results
                    if r.status in [TestStatus.FAILED, TestStatus.ERROR]
                ]

                for result in failed_results:
                    issues = await issue_detector.analyze_test_failures(result)
                    for issue in issues:
                        await issue_tracking.save_issue(issue)

            except Exception as e:
                error_result = TestResult(
                    test_name=f"{server_config.server_name}_comprehensive_error",
                    status=TestStatus.ERROR,
                    error_message=str(e),
                    server_name=server_config.server_name,
                    confidence_score=0.95,
                )
                all_results.append(error_result)

    # Generate and display comprehensive report
    await _generate_comprehensive_report(
        all_results, issue_tracking, args.test_output_format, console
    )


async def _display_test_results(
    results: list[TestResult], output_format: str, console: Console
) -> None:
    """Display test results in the specified format."""
    if output_format == "json":
        # Convert results to JSON
        results_data = []
        for result in results:
            results_data.append(
                {
                    "test_name": result.test_name,
                    "status": result.status.value,
                    "execution_time": result.execution_time,
                    "message": result.message,
                    "confidence_score": result.confidence_score,
                    "timestamp": (
                        result.timestamp.isoformat()
                        if result.timestamp
                        else None
                    ),
                    "error_info": result.error_info,
                }
            )

        output_file = Path("test_results.json")
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2)
        console.print(f"[green]Test results saved to {output_file}[/green]")

    elif output_format == "html":
        # Generate HTML report
        html_content = _generate_html_report(results)
        output_file = Path("test_results.html")
        with open(output_file, "w") as f:
            f.write(html_content)
        console.print(
            f"[green]HTML test report saved to {output_file}[/green]"
        )

    else:  # table format (default)
        # Display results in a table
        table = Table(title="MCP Server Test Results")
        table.add_column("Test", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Time (s)", justify="right")
        table.add_column("Confidence", justify="right")
        table.add_column("Message", style="dim")

        for result in results:
            status_style = {
                TestStatus.PASSED: "[green]PASSED[/green]",
                TestStatus.FAILED: "[red]FAILED[/red]",
                TestStatus.ERROR: "[bold red]ERROR[/bold red]",
                TestStatus.SKIPPED: "[yellow]SKIPPED[/yellow]",
            }.get(result.status, str(result.status.value))

            # Truncate message if too long
            message = result.message or ""
            if len(message) > 50:
                message = message[:50] + "..."

            table.add_row(
                result.test_name,
                status_style,
                (
                    f"{result.execution_time:.2f}"
                    if result.execution_time
                    else "N/A"
                ),
                (
                    f"{result.confidence_score:.1%}"
                    if result.confidence_score
                    else "N/A"
                ),
                message,
            )

        console.print(table)

        # Summary statistics
        total_tests = len(results)
        passed = len([r for r in results if r.status == TestStatus.PASSED])
        failed = len([r for r in results if r.status == TestStatus.FAILED])
        errors = len([r for r in results if r.status == TestStatus.ERROR])
        skipped = len([r for r in results if r.status == TestStatus.SKIPPED])

        console.print(
            f"\n[bold]Summary:[/bold] {total_tests} tests - "
            f"[green]{passed} passed[/green], "
            f"[red]{failed} failed[/red], "
            f"[bold red]{errors} errors[/bold red], "
            f"[yellow]{skipped} skipped[/yellow]"
        )


async def _generate_comprehensive_report(
    results: list[TestResult],
    issue_tracking: IssueTrackingManager,
    output_format: str,
    console: Console,
) -> None:
    """Generate a comprehensive test report with issue analysis."""
    # Get issue statistics
    issue_stats = await issue_tracking.get_issue_statistics()

    console.print(
        "\n[bold green]Comprehensive Test Report Generated[/bold green]"
    )

    # Display basic results
    await _display_test_results(results, output_format, console)

    # Display issue analysis
    if issue_stats:
        console.print("\n[bold yellow]Issue Analysis Summary[/bold yellow]")
        issue_table = Table()
        issue_table.add_column("Issue Type", style="cyan")
        issue_table.add_column("Count", justify="right")
        issue_table.add_column("Avg Confidence", justify="right")

        for issue_type, stats in issue_stats.items():
            issue_table.add_row(
                issue_type,
                str(stats.get("count", 0)),
                f"{stats.get('avg_confidence', 0):.1%}",
            )

        console.print(issue_table)


def _generate_html_report(results: list[TestResult]) -> str:
    """Generate an HTML report for test results."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Server Test Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .passed { color: green; font-weight: bold; }
            .failed { color: red; font-weight: bold; }
            .error { color: darkred; font-weight: bold; }
            .skipped { color: orange; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>MCP Server Test Results</h1>
        <table>
            <tr>
                <th>Test</th>
                <th>Status</th>
                <th>Execution Time (s)</th>
                <th>Confidence</th>
                <th>Message</th>
            </tr>
    """

    for result in results:
        status_class = result.status.value.lower()
        html_template += f"""
            <tr>
                <td>{result.test_name}</td>
                <td class="{status_class}">{result.status.value}</td>
                <td>{result.execution_time:.2f if result.execution_time else 'N/A'}</td>
                <td>{result.confidence_score:.1% if result.confidence_score else 'N/A'}</td>
                <td>{result.message or ''}</td>
            </tr>
        """

    html_template += """
        </table>
    </body>
    </html>
    """

    return html_template


if __name__ == "__main__":
    main()
