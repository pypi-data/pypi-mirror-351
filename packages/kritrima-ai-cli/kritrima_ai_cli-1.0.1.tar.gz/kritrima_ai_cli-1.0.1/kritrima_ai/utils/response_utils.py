"""
Response utilities for Kritrima AI CLI.

This module provides utilities for processing and handling AI responses,
including streaming response processing, content formatting, and response
validation.
"""

import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseEventType(Enum):
    """Types of response events."""

    RESPONSE_CREATED = "response.created"
    OUTPUT_TEXT_DELTA = "response.output_text.delta"
    OUTPUT_TEXT_DONE = "response.output_text.done"
    FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
    FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
    RESPONSE_COMPLETED = "response.completed"
    ERROR = "response.error"
    THINKING_START = "response.thinking.start"
    THINKING_END = "response.thinking.end"


@dataclass
class ResponseEvent:
    """Response event from AI provider."""

    type: ResponseEventType
    data: Dict[str, Any]
    timestamp: float = None
    event_id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())


@dataclass
class ResponseContentItem:
    """Individual content item in a response."""

    type: str  # "text", "function_call", "image", etc.
    content: Any
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProcessedResponse:
    """Fully processed AI response."""

    content_items: List[ResponseContentItem]
    metadata: Dict[str, Any]
    total_tokens: Optional[int] = None
    thinking_time: Optional[float] = None
    response_id: str = None

    def __post_init__(self):
        if self.response_id is None:
            self.response_id = str(uuid.uuid4())


class ResponseProcessor:
    """
    Response processor for handling AI responses.

    Processes streaming responses, validates content, and formats
    output for consumption by the terminal interface.
    """

    def __init__(self) -> None:
        """Initialize response processor."""
        self._current_response_id: Optional[str] = None
        self._accumulated_content: str = ""
        self._function_calls: List[Dict[str, Any]] = []
        self._thinking_start_time: Optional[float] = None

    async def process_streaming_response(
        self,
        response_stream: AsyncIterator[Dict[str, Any]],
        response_id: Optional[str] = None,
    ) -> AsyncIterator[ResponseEvent]:
        """
        Process streaming response from AI provider.

        Args:
            response_stream: Async iterator of response chunks
            response_id: Optional response ID

        Yields:
            Processed response events
        """
        try:
            self._current_response_id = response_id or str(uuid.uuid4())
            self._accumulated_content = ""
            self._function_calls = []

            # Emit response created event
            yield ResponseEvent(
                type=ResponseEventType.RESPONSE_CREATED,
                data={"response_id": self._current_response_id},
            )

            async for chunk in response_stream:
                events = await self._process_chunk(chunk)
                for event in events:
                    yield event

            # Emit completion event
            yield ResponseEvent(
                type=ResponseEventType.RESPONSE_COMPLETED,
                data={
                    "response_id": self._current_response_id,
                    "total_content_length": len(self._accumulated_content),
                    "function_calls_count": len(self._function_calls),
                },
            )

        except Exception as e:
            logger.error(f"Error processing streaming response: {e}")
            yield ResponseEvent(
                type=ResponseEventType.ERROR,
                data={"error": str(e), "response_id": self._current_response_id},
            )

    async def _process_chunk(self, chunk: Dict[str, Any]) -> List[ResponseEvent]:
        """
        Process individual response chunk.

        Args:
            chunk: Response chunk from AI provider

        Returns:
            List of response events
        """
        events = []

        try:
            # Handle different chunk types based on provider format
            if "choices" in chunk:
                # OpenAI-style response
                events.extend(await self._process_openai_chunk(chunk))
            elif "delta" in chunk:
                # Anthropic-style response
                events.extend(await self._process_anthropic_chunk(chunk))
            elif "content" in chunk:
                # Generic content chunk
                events.extend(await self._process_generic_chunk(chunk))
            else:
                logger.warning(f"Unknown chunk format: {chunk}")

        except Exception as e:
            logger.error(f"Error processing chunk: {e}")
            events.append(
                ResponseEvent(
                    type=ResponseEventType.ERROR,
                    data={"error": f"Chunk processing error: {str(e)}"},
                )
            )

        return events

    async def _process_openai_chunk(self, chunk: Dict[str, Any]) -> List[ResponseEvent]:
        """Process OpenAI-style response chunk."""
        events = []

        choices = chunk.get("choices", [])
        if not choices:
            return events

        choice = choices[0]
        delta = choice.get("delta", {})

        # Handle text content
        if "content" in delta and delta["content"]:
            content = delta["content"]
            self._accumulated_content += content

            events.append(
                ResponseEvent(
                    type=ResponseEventType.OUTPUT_TEXT_DELTA,
                    data={"delta": content, "accumulated": self._accumulated_content},
                )
            )

        # Handle function calls
        if "function_call" in delta:
            function_call = delta["function_call"]

            if "name" in function_call:
                # New function call
                self._function_calls.append(
                    {"name": function_call["name"], "arguments": ""}
                )

            if "arguments" in function_call and self._function_calls:
                # Add to current function call arguments
                self._function_calls[-1]["arguments"] += function_call["arguments"]

                events.append(
                    ResponseEvent(
                        type=ResponseEventType.FUNCTION_CALL_ARGUMENTS_DELTA,
                        data={
                            "function_name": self._function_calls[-1]["name"],
                            "arguments_delta": function_call["arguments"],
                            "accumulated_arguments": self._function_calls[-1][
                                "arguments"
                            ],
                        },
                    )
                )

        # Handle tool calls (newer OpenAI format)
        if "tool_calls" in delta:
            for tool_call in delta["tool_calls"]:
                if tool_call.get("type") == "function":
                    function = tool_call.get("function", {})

                    if "name" in function:
                        self._function_calls.append(
                            {
                                "id": tool_call.get("id"),
                                "name": function["name"],
                                "arguments": "",
                            }
                        )

                    if "arguments" in function and self._function_calls:
                        self._function_calls[-1]["arguments"] += function["arguments"]

                        events.append(
                            ResponseEvent(
                                type=ResponseEventType.FUNCTION_CALL_ARGUMENTS_DELTA,
                                data={
                                    "function_name": self._function_calls[-1]["name"],
                                    "arguments_delta": function["arguments"],
                                    "accumulated_arguments": self._function_calls[-1][
                                        "arguments"
                                    ],
                                },
                            )
                        )

        # Check for completion
        finish_reason = choice.get("finish_reason")
        if finish_reason:
            if finish_reason == "function_call" or finish_reason == "tool_calls":
                # Function call completed
                for func_call in self._function_calls:
                    events.append(
                        ResponseEvent(
                            type=ResponseEventType.FUNCTION_CALL_ARGUMENTS_DONE,
                            data={
                                "function_name": func_call["name"],
                                "arguments": func_call["arguments"],
                            },
                        )
                    )
            elif finish_reason == "stop":
                # Text output completed
                events.append(
                    ResponseEvent(
                        type=ResponseEventType.OUTPUT_TEXT_DONE,
                        data={"content": self._accumulated_content},
                    )
                )

        return events

    async def _process_anthropic_chunk(
        self, chunk: Dict[str, Any]
    ) -> List[ResponseEvent]:
        """Process Anthropic-style response chunk."""
        events = []

        delta = chunk.get("delta", {})

        # Handle text content
        if "text" in delta:
            content = delta["text"]
            self._accumulated_content += content

            events.append(
                ResponseEvent(
                    type=ResponseEventType.OUTPUT_TEXT_DELTA,
                    data={"delta": content, "accumulated": self._accumulated_content},
                )
            )

        # Handle thinking (if supported)
        if chunk.get("type") == "thinking_start":
            self._thinking_start_time = time.time()
            events.append(
                ResponseEvent(
                    type=ResponseEventType.THINKING_START,
                    data={"timestamp": self._thinking_start_time},
                )
            )

        elif chunk.get("type") == "thinking_end":
            thinking_time = None
            if self._thinking_start_time:
                thinking_time = time.time() - self._thinking_start_time

            events.append(
                ResponseEvent(
                    type=ResponseEventType.THINKING_END,
                    data={"thinking_time": thinking_time},
                )
            )

        return events

    async def _process_generic_chunk(
        self, chunk: Dict[str, Any]
    ) -> List[ResponseEvent]:
        """Process generic content chunk."""
        events = []

        content = chunk.get("content", "")
        if content:
            self._accumulated_content += content

            events.append(
                ResponseEvent(
                    type=ResponseEventType.OUTPUT_TEXT_DELTA,
                    data={"delta": content, "accumulated": self._accumulated_content},
                )
            )

        return events

    def create_processed_response(
        self,
        content_items: List[ResponseContentItem],
        metadata: Optional[Dict[str, Any]] = None,
        total_tokens: Optional[int] = None,
        thinking_time: Optional[float] = None,
    ) -> ProcessedResponse:
        """
        Create a processed response object.

        Args:
            content_items: List of content items
            metadata: Optional metadata
            total_tokens: Optional token count
            thinking_time: Optional thinking time

        Returns:
            Processed response object
        """
        return ProcessedResponse(
            content_items=content_items,
            metadata=metadata or {},
            total_tokens=total_tokens,
            thinking_time=thinking_time,
        )

    def format_response_for_display(self, response: ProcessedResponse) -> str:
        """
        Format response for terminal display.

        Args:
            response: Processed response

        Returns:
            Formatted response string
        """
        formatted_parts = []

        for item in response.content_items:
            if item.type == "text":
                formatted_parts.append(str(item.content))
            elif item.type == "function_call":
                func_name = item.metadata.get("function_name", "unknown")
                formatted_parts.append(f"[Function Call: {func_name}]")
            elif item.type == "image":
                formatted_parts.append("[Image]")
            else:
                formatted_parts.append(f"[{item.type.title()}]")

        result = "\n".join(formatted_parts)

        # Add metadata if available
        if response.metadata:
            if response.total_tokens:
                result += f"\n\n[Tokens: {response.total_tokens}]"
            if response.thinking_time:
                result += f"\n[Thinking time: {response.thinking_time:.2f}s]"

        return result

    def validate_response(self, response: ProcessedResponse) -> bool:
        """
        Validate response content.

        Args:
            response: Response to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check basic structure
            if not response.content_items:
                logger.warning("Response has no content items")
                return False

            # Validate each content item
            for item in response.content_items:
                if not item.type:
                    logger.warning("Content item missing type")
                    return False

                if item.content is None:
                    logger.warning("Content item has no content")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating response: {e}")
            return False


# Convenience functions
async def stream_responses(
    response_stream: AsyncIterator[Dict[str, Any]], response_id: Optional[str] = None
) -> AsyncIterator[ResponseEvent]:
    """
    Stream and process AI responses.

    Args:
        response_stream: Raw response stream
        response_id: Optional response ID

    Yields:
        Processed response events
    """
    processor = ResponseProcessor()
    async for event in processor.process_streaming_response(
        response_stream, response_id
    ):
        yield event


def create_text_response(
    text: str, metadata: Optional[Dict[str, Any]] = None
) -> ProcessedResponse:
    """
    Create a simple text response.

    Args:
        text: Response text
        metadata: Optional metadata

    Returns:
        Processed response
    """
    content_item = ResponseContentItem(
        type="text", content=text, metadata=metadata or {}
    )

    processor = ResponseProcessor()
    return processor.create_processed_response([content_item], metadata)


def create_function_call_response(
    function_name: str,
    arguments: Dict[str, Any],
    result: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> ProcessedResponse:
    """
    Create a function call response.

    Args:
        function_name: Name of the function
        arguments: Function arguments
        result: Optional function result
        metadata: Optional metadata

    Returns:
        Processed response
    """
    func_metadata = {
        "function_name": function_name,
        "arguments": arguments,
        "result": result,
    }
    if metadata:
        func_metadata.update(metadata)

    content_item = ResponseContentItem(
        type="function_call",
        content={"name": function_name, "arguments": arguments, "result": result},
        metadata=func_metadata,
    )

    processor = ResponseProcessor()
    return processor.create_processed_response([content_item], metadata)
