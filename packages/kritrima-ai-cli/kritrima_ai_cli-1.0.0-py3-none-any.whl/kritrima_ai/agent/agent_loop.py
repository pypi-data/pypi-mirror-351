"""
Autonomous agent loop system for Kritrima AI CLI.

This module implements the core agent orchestration system that manages:
- AI conversation flow and context management
- Tool calling and execution with comprehensive approval system
- Streaming response handling with real-time updates
- Error recovery and fallback mechanisms
- Performance monitoring and metrics
- Session persistence and state management
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from kritrima_ai.agent.tool_registry import ToolRegistry
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.providers.ai_client import AIClient
from kritrima_ai.security.approval import ApprovalSystem
from kritrima_ai.storage.command_history import CommandHistory
from kritrima_ai.storage.session_manager import SessionManager
from kritrima_ai.utils.logger import get_logger, performance_timer

logger = get_logger(__name__)


class ResponseType(Enum):
    """Types of agent responses."""

    TEXT = "text"
    TOOL_CALL = "tool_call"
    ERROR = "error"
    THINKING = "thinking"
    SYSTEM = "system"
    APPROVAL_REQUIRED = "approval_required"
    STREAMING_START = "streaming_start"
    STREAMING_END = "streaming_end"


@dataclass
class AgentResponse:
    """Response from the agent loop."""

    type: ResponseType
    content: str
    metadata: Dict[str, Any] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[str] = None
    timestamp: float = None
    request_id: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())


class AgentLoop:
    """
    Core autonomous agent loop system.

    The agent loop manages the conversation flow between the user and AI,
    including tool execution, context management, and response streaming.
    """

    def __init__(
        self,
        config: AppConfig,
        session_manager: SessionManager,
        command_history: CommandHistory,
        approval_callback: Optional[Callable] = None,
    ) -> None:
        """
        Initialize the agent loop.

        Args:
            config: Application configuration
            session_manager: Session management system
            command_history: Command history manager
            approval_callback: Callback for approval requests
        """
        self.config = config
        self.session_manager = session_manager
        self.command_history = command_history
        self.approval_callback = approval_callback

        # Initialize AI client
        self.ai_client = AIClient(config)

        # Initialize tool registry
        self.tool_registry = ToolRegistry(config)

        # Initialize approval system
        self.approval_system = ApprovalSystem(config)

        # Conversation context
        self.context: List[Dict[str, Any]] = []
        self.system_prompt = self._create_comprehensive_system_prompt()

        # State management
        self._current_request_id: Optional[str] = None
        self._is_processing = False
        self._abort_controller: Optional[asyncio.Event] = None

        # Performance tracking
        self._total_requests = 0
        self._total_tokens = 0
        self._total_thinking_time = 0.0
        self._conversation_start_time = time.time()

        # Tool execution cache
        self._tool_results_cache: Dict[str, Any] = {}

        logger.info("Agent loop initialized with full tool calling and approval system")

    async def send_message(self, message: str, **kwargs) -> AgentResponse:
        """
        Send a message to the AI and get a response.

        Args:
            message: User message
            **kwargs: Additional parameters

        Returns:
            Agent response
        """
        try:
            with performance_timer("agent_send_message", logger):
                self._total_requests += 1
                request_id = str(uuid.uuid4())
                self._current_request_id = request_id

                # Add user message to context
                await self._add_message_to_context("user", message, request_id)

                # Add to session and command history
                await self._persist_user_message(message, request_id)

                # Get AI response with tool calling support
                response = await self._get_ai_response_with_tools(request_id)

                # Add assistant response to context
                await self._add_message_to_context(
                    "assistant", response.content, request_id
                )

                # Persist assistant response
                await self._persist_assistant_response(response)

                return response

        except Exception as e:
            logger.error(f"Error in agent send_message: {e}", exc_info=True)

            # Send error notification
            try:
                from kritrima_ai.utils.notifications import notify_error

                await notify_error(f"Agent error: {str(e)}")
            except Exception:
                pass  # Don't fail on notification errors

            # Create crash report for serious errors
            try:
                from kritrima_ai.utils.bug_reporter import get_bug_reporter

                bug_reporter = get_bug_reporter()
                if bug_reporter:
                    context = {
                        "message": message,
                        "request_id": request_id,
                        "config": {
                            "provider": self.config.provider,
                            "model": self.config.model,
                            "approval_mode": self.config.approval_mode,
                        },
                    }
                    await bug_reporter.create_crash_report(
                        e, context, self.session_manager, self.command_history
                    )
            except Exception:
                pass  # Don't fail on bug reporting errors

            return AgentResponse(
                type=ResponseType.ERROR,
                content=f"Agent error: {str(e)}",
                request_id=request_id,
            )
        finally:
            self._current_request_id = None
            self._is_processing = False

    async def send_message_stream(
        self, message: str, **kwargs
    ) -> AsyncIterator[AgentResponse]:
        """
        Send a message and stream the response with full tool calling.

        Args:
            message: User message
            **kwargs: Additional parameters

        Yields:
            Agent response chunks
        """
        try:
            with performance_timer("agent_send_message_stream", logger):
                self._total_requests += 1
                request_id = str(uuid.uuid4())
                self._current_request_id = request_id
                self._is_processing = True

                # Signal streaming start
                yield AgentResponse(
                    type=ResponseType.STREAMING_START, content="", request_id=request_id
                )

                # Add user message to context
                await self._add_message_to_context("user", message, request_id)

                # Add to session and command history
                await self._persist_user_message(message, request_id)

                # Stream AI response with tool handling
                full_response = ""
                tool_calls = []

                async for chunk in self._stream_ai_response_with_tools(request_id):
                    if chunk.type == ResponseType.TEXT:
                        full_response += chunk.content
                        yield chunk
                    elif chunk.type == ResponseType.TOOL_CALL:
                        tool_calls.append(chunk)
                        yield chunk
                    elif chunk.type == ResponseType.APPROVAL_REQUIRED:
                        yield chunk
                    elif chunk.type == ResponseType.ERROR:
                        yield chunk
                        return

                # Add complete response to context if we have content
                if full_response:
                    await self._add_message_to_context(
                        "assistant", full_response, request_id
                    )
                    await self._persist_assistant_response(
                        AgentResponse(
                            type=ResponseType.TEXT,
                            content=full_response,
                            request_id=request_id,
                        )
                    )

                # Signal streaming end
                yield AgentResponse(
                    type=ResponseType.STREAMING_END,
                    content="",
                    request_id=request_id,
                    metadata={"tool_calls_executed": len(tool_calls)},
                )

        except Exception as e:
            logger.error(f"Error in agent send_message_stream: {e}", exc_info=True)
            yield AgentResponse(
                type=ResponseType.ERROR,
                content=f"Agent streaming error: {str(e)}",
                request_id=request_id,
            )
        finally:
            self._current_request_id = None
            self._is_processing = False

    async def add_context(self, context: Dict[str, Any]) -> None:
        """
        Add additional context to the conversation.

        Args:
            context: Context dictionary containing files, project info, etc.
        """
        try:
            # Format context as a system message
            context_message = self._format_context_message(context)

            await self._add_message_to_context(
                "system", context_message, str(uuid.uuid4())
            )

            logger.debug(f"Added context with {len(context)} items")

        except Exception as e:
            logger.error(f"Error adding context: {e}")

    async def _get_ai_response_with_tools(self, request_id: str) -> AgentResponse:
        """
        Get AI response with comprehensive tool calling support.

        Args:
            request_id: Unique request identifier

        Returns:
            Agent response with tool execution results
        """
        try:
            # Prepare messages with full context
            messages = self._prepare_messages()

            # Get available tools
            tools = await self.tool_registry.get_available_tools()

            # Add thinking indicator
            thinking_start = time.time()

            # Make AI request with tools
            ai_response = await self.ai_client.chat_completion(
                messages=messages,
                tools=tools,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            thinking_time = time.time() - thinking_start
            self._total_thinking_time += thinking_time

            # Track token usage
            if "usage" in ai_response:
                self._total_tokens += ai_response["usage"].get("total_tokens", 0)

            # Process response
            choice = ai_response["choices"][0]

            if choice.get("finish_reason") == "tool_calls":
                # Handle tool calls
                tool_calls = choice["message"].get("tool_calls", [])
                return await self._execute_tool_calls(tool_calls, request_id)
            else:
                # Regular text response
                content = choice["message"]["content"]
                return AgentResponse(
                    type=ResponseType.TEXT,
                    content=content,
                    request_id=request_id,
                    metadata={"thinking_time": thinking_time},
                )

        except Exception as e:
            logger.error(f"Error getting AI response: {e}", exc_info=True)
            return AgentResponse(
                type=ResponseType.ERROR,
                content=f"AI response error: {str(e)}",
                request_id=request_id,
            )

    async def _stream_ai_response_with_tools(
        self, request_id: str
    ) -> AsyncIterator[AgentResponse]:
        """
        Stream AI response with tool calling support.

        Args:
            request_id: Unique request identifier

        Yields:
            Agent response chunks
        """
        try:
            # Prepare messages and tools
            messages = self._prepare_messages()
            tools = await self.tool_registry.get_available_tools()

            # Start thinking timer
            thinking_start = time.time()

            # Stream response from AI
            accumulated_content = ""
            accumulated_tool_calls = []

            async for chunk in self.ai_client.chat_completion_stream(
                messages=messages,
                tools=tools,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            ):
                # Process chunk based on type
                if "choices" in chunk and chunk["choices"]:
                    choice = chunk["choices"][0]
                    delta = choice.get("delta", {})

                    # Handle content delta
                    if "content" in delta and delta["content"]:
                        content_chunk = delta["content"]
                        accumulated_content += content_chunk

                        yield AgentResponse(
                            type=ResponseType.TEXT,
                            content=content_chunk,
                            request_id=request_id,
                        )

                    # Handle tool calls
                    if "tool_calls" in delta:
                        for tool_call in delta["tool_calls"]:
                            accumulated_tool_calls.append(tool_call)

                    # Handle finish reason
                    if choice.get("finish_reason") == "tool_calls":
                        # Execute accumulated tool calls
                        if accumulated_tool_calls:
                            async for tool_response in self._stream_tool_execution(
                                accumulated_tool_calls, request_id
                            ):
                                yield tool_response

            thinking_time = time.time() - thinking_start
            self._total_thinking_time += thinking_time

        except Exception as e:
            logger.error(f"Error streaming AI response: {e}", exc_info=True)
            yield AgentResponse(
                type=ResponseType.ERROR,
                content=f"AI streaming error: {str(e)}",
                request_id=request_id,
            )

    async def _execute_tool_calls(
        self, tool_calls: List[Dict[str, Any]], request_id: str
    ) -> AgentResponse:
        """
        Execute tool calls with approval system integration.

        Args:
            tool_calls: List of tool calls from AI
            request_id: Request identifier

        Returns:
            Agent response with tool execution results
        """
        try:
            results = []

            for tool_call in tool_calls:
                tool_id = tool_call.get("id", str(uuid.uuid4()))
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args_str = function.get("arguments", "{}")

                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Failed to parse tool arguments: {tool_args_str}, error: {e}"
                    )
                    tool_args = {}

                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                # Check approval
                approval_result = await self.approval_system.request_approval(
                    tool_name=tool_name,
                    arguments=tool_args,
                    context={"request_id": request_id},
                )

                if not approval_result.approved:
                    results.append(
                        {
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "tool_args": tool_args,
                            "tool_result": f"Tool execution denied: {approval_result.reason}",
                            "approved": False,
                            "execution_time": 0,
                        }
                    )
                    continue

                # Execute tool
                start_time = time.time()
                try:
                    tool_result = await self.tool_registry.execute_tool(
                        tool_name, tool_args, context={"request_id": request_id}
                    )
                    execution_time = time.time() - start_time

                    # Cache successful results
                    cache_key = f"{tool_name}:{hash(str(tool_args))}"
                    self._tool_results_cache[cache_key] = {
                        "result": tool_result,
                        "timestamp": time.time(),
                    }

                    # Send success notification for tool execution
                    try:
                        from kritrima_ai.utils.notifications import (
                            notify_tool_execution,
                        )

                        await notify_tool_execution(tool_name, "completed")
                    except Exception:
                        pass  # Don't fail on notification errors

                except Exception as tool_error:
                    execution_time = time.time() - start_time
                    tool_result = f"Tool execution failed: {str(tool_error)}"
                    logger.error(f"Tool {tool_name} execution failed: {tool_error}")

                # Record tool call in session
                await self.session_manager.add_tool_call_to_current(
                    tool_name=tool_name,
                    arguments=tool_args,
                    result=str(tool_result),
                    execution_time=execution_time,
                    approved=approval_result.approved,
                )

                results.append(
                    {
                        "tool_id": tool_id,
                        "tool_name": tool_name,
                        "tool_args": tool_args,
                        "tool_result": str(tool_result),
                        "approved": True,
                        "execution_time": execution_time,
                    }
                )

            # Format comprehensive response
            return self._format_tool_results_response(results, request_id)

        except Exception as e:
            logger.error(f"Error executing tool calls: {e}")
            return AgentResponse(
                type=ResponseType.ERROR,
                content=f"Tool execution error: {str(e)}",
                request_id=request_id,
            )

    async def _stream_tool_execution(
        self, tool_calls: List[Dict[str, Any]], request_id: str
    ) -> AsyncIterator[AgentResponse]:
        """
        Stream tool execution with real-time output.

        Args:
            tool_calls: List of tool calls to execute
            request_id: Request identifier

        Yields:
            Agent response chunks for tool execution
        """
        try:
            results = []

            for tool_call in tool_calls:
                tool_id = tool_call.get("id", str(uuid.uuid4()))
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args_str = function.get("arguments", "{}")

                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Failed to parse tool arguments: {tool_args_str}, error: {e}"
                    )
                    tool_args = {}

                # Yield tool call start
                yield AgentResponse(
                    type=ResponseType.TOOL_CALL,
                    content=f"Executing {tool_name}...",
                    tool_name=tool_name,
                    tool_args=tool_args,
                    request_id=request_id,
                )

                # Check approval
                approval_result = await self.approval_system.request_approval(
                    tool_name=tool_name,
                    arguments=tool_args,
                    context={"request_id": request_id},
                )

                if not approval_result.approved:
                    yield AgentResponse(
                        type=ResponseType.ERROR,
                        content=f"Tool execution denied: {approval_result.reason}",
                        tool_name=tool_name,
                        request_id=request_id,
                    )
                    results.append(
                        {
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "tool_args": tool_args,
                            "tool_result": f"Tool execution denied: {approval_result.reason}",
                            "approved": False,
                            "execution_time": 0,
                        }
                    )
                    continue

                # Execute tool with streaming
                start_time = time.time()
                try:
                    # Check if tool supports streaming
                    tool_metadata = self.tool_registry.get_tool_metadata(tool_name)
                    if tool_metadata and tool_metadata.supports_streaming:
                        # Stream tool execution
                        accumulated_output = ""
                        async for (
                            output_chunk
                        ) in self.tool_registry.execute_tool_stream(
                            tool_name, tool_args, context={"request_id": request_id}
                        ):
                            accumulated_output += output_chunk
                            yield AgentResponse(
                                type=ResponseType.TEXT,
                                content=output_chunk,
                                tool_name=tool_name,
                                request_id=request_id,
                            )
                        tool_result = accumulated_output
                    else:
                        # Regular tool execution
                        tool_result = await self.tool_registry.execute_tool(
                            tool_name, tool_args, context={"request_id": request_id}
                        )

                        # Yield the result
                        yield AgentResponse(
                            type=ResponseType.TEXT,
                            content=str(tool_result),
                            tool_name=tool_name,
                            request_id=request_id,
                        )

                    execution_time = time.time() - start_time

                    # Cache successful results
                    cache_key = f"{tool_name}:{hash(str(tool_args))}"
                    self._tool_results_cache[cache_key] = {
                        "result": tool_result,
                        "timestamp": time.time(),
                    }

                except Exception as tool_error:
                    execution_time = time.time() - start_time
                    tool_result = f"Tool execution failed: {str(tool_error)}"
                    logger.error(f"Tool {tool_name} execution failed: {tool_error}")

                    yield AgentResponse(
                        type=ResponseType.ERROR,
                        content=tool_result,
                        tool_name=tool_name,
                        request_id=request_id,
                    )

                # Record tool call in session
                await self.session_manager.add_tool_call_to_current(
                    tool_name=tool_name,
                    arguments=tool_args,
                    result=str(tool_result),
                    execution_time=execution_time,
                    approved=approval_result.approved,
                )

                # Add to command history
                await self.command_history.add_tool_execution(
                    tool_name=tool_name,
                    arguments=tool_args,
                    result=str(tool_result),
                    success=not isinstance(tool_result, str)
                    or not tool_result.startswith("Tool execution failed"),
                )

                results.append(
                    {
                        "tool_id": tool_id,
                        "tool_name": tool_name,
                        "tool_args": tool_args,
                        "tool_result": str(tool_result),
                        "approved": approval_result.approved,
                        "execution_time": execution_time,
                    }
                )

            # Yield final summary
            yield AgentResponse(
                type=ResponseType.SYSTEM,
                content=f"Completed execution of {len(results)} tool(s)",
                request_id=request_id,
                metadata={"tool_results": results},
            )

        except Exception as e:
            logger.error(f"Error in stream tool execution: {e}", exc_info=True)
            yield AgentResponse(
                type=ResponseType.ERROR,
                content=f"Tool execution error: {str(e)}",
                request_id=request_id,
            )

    def _format_tool_results_response(
        self, results: List[Dict[str, Any]], request_id: str
    ) -> AgentResponse:
        """Format tool execution results into a comprehensive response."""
        if not results:
            return AgentResponse(
                type=ResponseType.SYSTEM,
                content="No tools were executed.",
                request_id=request_id,
            )

        if len(results) == 1:
            result = results[0]
            return AgentResponse(
                type=ResponseType.TOOL_CALL,
                content=f"Executed {result['tool_name']}: {result['tool_result']}",
                tool_name=result["tool_name"],
                tool_args=result["tool_args"],
                tool_result=result["tool_result"],
                request_id=request_id,
                metadata={
                    "execution_time": result["execution_time"],
                    "approved": result["approved"],
                },
            )
        else:
            # Multiple tool calls
            content_lines = [f"Executed {len(results)} tools:"]
            total_time = 0
            approved_count = 0

            for result in results:
                status = "✓" if result["approved"] else "✗"
                content_lines.append(
                    f"{status} {result['tool_name']}: {result['tool_result'][:100]}..."
                )
                total_time += result["execution_time"]
                if result["approved"]:
                    approved_count += 1

            return AgentResponse(
                type=ResponseType.TOOL_CALL,
                content="\n".join(content_lines),
                request_id=request_id,
                metadata={
                    "tool_results": results,
                    "total_execution_time": total_time,
                    "approved_count": approved_count,
                    "total_count": len(results),
                },
            )

    async def _add_message_to_context(
        self, role: str, content: str, request_id: str
    ) -> None:
        """Add a message to the conversation context."""
        self.context.append(
            {
                "role": role,
                "content": content,
                "timestamp": time.time(),
                "request_id": request_id,
            }
        )

        # Trim context if too large
        if len(self.context) > 100:
            # Keep system messages and recent messages
            system_messages = [msg for msg in self.context if msg["role"] == "system"]
            other_messages = [msg for msg in self.context if msg["role"] != "system"]
            self.context = system_messages + other_messages[-80:]

    async def _persist_user_message(self, message: str, request_id: str) -> None:
        """Persist user message to session and command history."""
        # Add to session
        await self.session_manager.add_message_to_current("user", message)

        # Add to command history
        await self.command_history.add_command(
            message,
            session_id=(
                self.session_manager.get_current_session().session_id
                if self.session_manager.get_current_session()
                else None
            ),
            metadata={"request_id": request_id},
        )

    async def _persist_assistant_response(self, response: AgentResponse) -> None:
        """Persist assistant response to session."""
        await self.session_manager.add_message_to_current("assistant", response.content)

    def _prepare_messages(self) -> List[Dict[str, str]]:
        """
        Prepare messages for AI request with comprehensive context.

        Returns:
            List of messages formatted for AI
        """
        messages = []

        # Add comprehensive system prompt
        messages.append({"role": "system", "content": self.system_prompt})

        # Add context messages with optimization
        context_messages = self._optimize_context(self.context.copy())

        for msg in context_messages:
            messages.append({"role": msg["role"], "content": msg["content"]})

        return messages

    def _optimize_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize context to fit within token limits intelligently.

        Args:
            messages: Original messages

        Returns:
            Optimized messages
        """
        if len(messages) <= 50:
            return messages

        # Separate by role
        system_messages = [msg for msg in messages if msg["role"] == "system"]
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]

        # Keep all system messages
        optimized = system_messages.copy()

        # Interleave recent user/assistant messages
        recent_conversation = []
        user_iter = iter(reversed(user_messages[-15:]))
        assistant_iter = iter(reversed(assistant_messages[-15:]))

        # Create alternating pattern
        for _ in range(min(15, len(user_messages), len(assistant_messages))):
            try:
                recent_conversation.append(next(user_iter))
                recent_conversation.append(next(assistant_iter))
            except StopIteration:
                break

        # Reverse to maintain chronological order
        recent_conversation.reverse()
        optimized.extend(recent_conversation)

        logger.debug(
            f"Optimized context from {len(messages)} to {len(optimized)} messages"
        )
        return optimized

    def _create_comprehensive_system_prompt(self) -> str:
        """Create a comprehensive system prompt for the AI agent."""
        return f"""You are Kritrima AI, a sophisticated AI assistant designed to help with coding, development, and comprehensive technical tasks. You are part of an advanced CLI system with extensive capabilities.

CORE CAPABILITIES:
- Advanced code analysis, generation, and refactoring
- Comprehensive file operations and project management
- System command execution with security safeguards
- Multi-language programming support (Python, JavaScript, TypeScript, Go, Rust, Java, C++, etc.)
- Architecture design and technical documentation
- Database design and query optimization
- DevOps and infrastructure guidance
- Security analysis and vulnerability assessment

AVAILABLE TOOLS:
You have access to a comprehensive set of tools for:
- File Operations: read, write, create, delete, move, copy files and directories
- Command Execution: run shell commands, scripts, and system operations
- Code Analysis: syntax checking, linting, testing, profiling
- Project Management: dependency management, build systems, version control
- System Information: environment details, resource monitoring
- Full Context Analysis: comprehensive project structure analysis

SECURITY & APPROVAL SYSTEM:
- All tool executions go through an approval system
- Destructive operations require explicit user consent
- Commands are sandboxed for security
- You will be notified if approval is required
- Respect user preferences for automation vs manual approval

INTERACTION PRINCIPLES:
1. **Safety First**: Always prioritize security and data integrity
2. **Clear Communication**: Explain your reasoning and intended actions
3. **Incremental Approach**: Break complex tasks into manageable steps
4. **Context Awareness**: Leverage project structure and existing code patterns
5. **Best Practices**: Follow industry standards and conventions
6. **Error Handling**: Provide robust error handling and recovery suggestions

RESPONSE FORMAT:
- Be concise but thorough
- Use code blocks with appropriate syntax highlighting
- Structure responses clearly with headers and bullet points
- Provide alternatives when multiple approaches exist
- Include explanations for complex operations

TOOL USAGE GUIDELINES:
- Use tools proactively to gather information and make changes
- Always check file contents before making modifications
- Verify system state before executing commands
- Use appropriate tools for each task type
- Handle tool failures gracefully

CURRENT SESSION CONTEXT:
- Provider: {self.config.provider}
- Model: {self.config.model}
- Approval Mode: {self.config.approval_mode}
- Working Directory: Available via system tools
- Session ID: Available via session manager

Remember: You are an autonomous agent capable of taking action. Use your tools wisely to provide comprehensive assistance while maintaining safety and user control."""

    def _format_context_message(self, context: Dict[str, Any]) -> str:
        """
        Format context information as a comprehensive message.

        Args:
            context: Context dictionary

        Returns:
            Formatted context message
        """
        lines = ["=== ADDITIONAL CONTEXT ==="]

        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"\n{key.upper()}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (list, dict)):
                        lines.append(
                            f"  {sub_key}: {type(sub_value).__name__} with {len(sub_value)} items"
                        )
                    else:
                        lines.append(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list):
                lines.append(f"\n{key.upper()} ({len(value)} items):")
                for i, item in enumerate(value[:10]):  # Show first 10 items
                    lines.append(f"  {i + 1}. {item}")
                if len(value) > 10:
                    lines.append(f"  ... and {len(value) - 10} more items")
            else:
                lines.append(f"{key.upper()}: {value}")

        lines.append("=== END CONTEXT ===")
        return "\n".join(lines)

    async def interrupt_current_request(self) -> bool:
        """
        Interrupt the current request if one is in progress.

        Returns:
            True if request was interrupted, False otherwise
        """
        if not self._is_processing:
            return False

        if self._abort_controller:
            self._abort_controller.set()
            logger.info("Current request interrupted by user")
            return True

        return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics for the agent.

        Returns:
            Performance statistics dictionary
        """
        session_duration = time.time() - self._conversation_start_time

        return {
            "total_requests": self._total_requests,
            "total_tokens": self._total_tokens,
            "total_thinking_time": self._total_thinking_time,
            "average_thinking_time": self._total_thinking_time
            / max(self._total_requests, 1),
            "context_messages": len(self.context),
            "available_tools": len(self.tool_registry.get_registered_tools()),
            "session_duration": session_duration,
            "requests_per_minute": (
                (self._total_requests / session_duration) * 60
                if session_duration > 0
                else 0
            ),
            "tool_cache_size": len(self._tool_results_cache),
            "current_provider": self.config.provider,
            "current_model": self.config.model,
            "approval_mode": self.config.approval_mode,
        }

    async def reset_conversation(self) -> None:
        """Reset the conversation context and clear caches."""
        self.context.clear()
        self._tool_results_cache.clear()
        self._conversation_start_time = time.time()
        logger.info("Conversation context and caches reset")

    async def cleanup(self) -> None:
        """Clean up agent resources comprehensively."""
        try:
            # Interrupt any ongoing requests
            if self._is_processing:
                await self.interrupt_current_request()

            # Cleanup AI client
            if hasattr(self.ai_client, "cleanup"):
                await self.ai_client.cleanup()

            # Cleanup tool registry
            if hasattr(self.tool_registry, "cleanup"):
                await self.tool_registry.cleanup()

            # Cleanup approval system
            if hasattr(self.approval_system, "cleanup"):
                await self.approval_system.cleanup()

            # Clear caches
            self._tool_results_cache.clear()

            logger.info("Agent loop cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during agent cleanup: {e}")

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the current context.

        Returns:
            Context summary dictionary
        """
        recent_messages = self.context[-10:] if self.context else []

        return {
            "total_messages": len(self.context),
            "user_messages": len([m for m in self.context if m["role"] == "user"]),
            "assistant_messages": len(
                [m for m in self.context if m["role"] == "assistant"]
            ),
            "system_messages": len([m for m in self.context if m["role"] == "system"]),
            "last_message_time": (
                self.context[-1]["timestamp"] if self.context else None
            ),
            "recent_message_types": [msg["role"] for msg in recent_messages],
            "context_size_estimate": sum(len(msg["content"]) for msg in self.context),
            "session_active": self._current_request_id is not None,
            "processing_state": self._is_processing,
        }
