"""MCP server implementing Claude Code capabilities."""

from typing import Literal, cast, final

from fastmcp import FastMCP

from mcp_claude_code.prompts import register_all_prompts
from mcp_claude_code.tools import register_all_tools
from mcp_claude_code.tools.common.context import DocumentContext
from mcp_claude_code.tools.common.permissions import PermissionManager
from mcp_claude_code.tools.shell.command_executor import CommandExecutor


@final
class ClaudeCodeServer:
    """MCP server implementing Claude Code capabilities."""

    def __init__(
        self,
        name: str = "claude-code",
        allowed_paths: list[str] | None = None,
        project_paths: list[str] | None = None,
        mcp_instance: FastMCP | None = None,
        agent_model: str | None = None,
        agent_max_tokens: int | None = None,
        agent_api_key: str | None = None,
        agent_base_url: str | None = None,
        agent_max_iterations: int = 10,
        agent_max_tool_uses: int = 30,
        enable_agent_tool: bool = False,
        command_timeout: float = 120.0,
    ):
        """Initialize the Claude Code server.

        Args:
            name: The name of the server
            allowed_paths: list of paths that the server is allowed to access
            project_paths: list of project paths to generate prompts for
            mcp_instance: Optional FastMCP instance for testing
            agent_model: Optional model name for agent tool in LiteLLM format
            agent_max_tokens: Optional maximum tokens for agent responses
            agent_api_key: Optional API key for the LLM provider
            agent_base_url: Optional base URL for the LLM provider API endpoint
            agent_max_iterations: Maximum number of iterations for agent (default: 10)
            agent_max_tool_uses: Maximum number of total tool uses for agent (default: 30)
            enable_agent_tool: Whether to enable the agent tool (default: False)
            command_timeout: Default timeout for command execution in seconds (default: 120.0)
        """
        self.mcp = mcp_instance if mcp_instance is not None else FastMCP(name)

        # Initialize context, permissions, and command executor
        self.document_context = DocumentContext()
        self.permission_manager = PermissionManager()

        # Initialize command executor
        self.command_executor = CommandExecutor(
            permission_manager=self.permission_manager,
            verbose=False,  # Set to True for debugging
        )

        # Add allowed paths
        if allowed_paths:
            for path in allowed_paths:
                self.permission_manager.add_allowed_path(path)
                self.document_context.add_allowed_path(path)

        # Store project paths
        self.project_paths = project_paths

        # Store agent options
        self.agent_model = agent_model
        self.agent_max_tokens = agent_max_tokens
        self.agent_api_key = agent_api_key
        self.agent_base_url = agent_base_url
        self.agent_max_iterations = agent_max_iterations
        self.agent_max_tool_uses = agent_max_tool_uses
        self.enable_agent_tool = enable_agent_tool
        self.command_timeout = command_timeout

        # Register all tools
        register_all_tools(
            mcp_server=self.mcp,
            document_context=self.document_context,
            permission_manager=self.permission_manager,
            agent_model=self.agent_model,
            agent_max_tokens=self.agent_max_tokens,
            agent_api_key=self.agent_api_key,
            agent_base_url=self.agent_base_url,
            agent_max_iterations=self.agent_max_iterations,
            agent_max_tool_uses=self.agent_max_tool_uses,
            enable_agent_tool=self.enable_agent_tool,
        )

        register_all_prompts(mcp_server=self.mcp, projects=self.project_paths)

    def run(self, transport: str = "stdio", allowed_paths: list[str] | None = None):
        """Run the MCP server.

        Args:
            transport: The transport to use (stdio or sse)
            allowed_paths: list of paths that the server is allowed to access
        """
        # Add allowed paths if provided
        allowed_paths_list = allowed_paths or []
        for path in allowed_paths_list:
            self.permission_manager.add_allowed_path(path)
            self.document_context.add_allowed_path(path)

        # Run the server
        transport_type = cast(Literal["stdio", "sse"], transport)
        self.mcp.run(transport=transport_type)
