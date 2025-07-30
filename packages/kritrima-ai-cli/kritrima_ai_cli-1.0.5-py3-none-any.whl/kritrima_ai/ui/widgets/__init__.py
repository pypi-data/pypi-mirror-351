"""
Advanced UI widgets for Kritrima AI CLI terminal interface.

This module provides specialized widgets for enhanced terminal interaction
including text buffers, overlays, spinners, and advanced input components.
"""

from kritrima_ai.ui.widgets.advanced_input import (
    AdvancedInput,
    CommandInput,
    FileTagInput,
    MultilineEditor,
)
from kritrima_ai.ui.widgets.chat_components import (
    ChatContainer,
    ChatMessage,
    ChatMessageRenderer,
    CodeBlockWidget,
    DiffWidget,
    StreamingResponseWidget,
    ToolCallWidget,
)
from kritrima_ai.ui.widgets.overlays import (
    ApprovalModeOverlay,
    ConfigOverlay,
    DebugOverlay,
    DiffOverlay,
    FileSuggestionsOverlay,
    HelpOverlay,
)
from kritrima_ai.ui.widgets.selection_components import (
    HistoryBrowser,
    HistoryEntry,
    ModelInfo,
    ModelSelector,
    ProviderInfo,
    ProviderSelector,
    SessionBrowser,
    SessionInfo,
)
from kritrima_ai.ui.widgets.spinner import (
    LoadingSpinner,
    ProgressSpinner,
    ThinkingSpinner,
)
from kritrima_ai.ui.widgets.status_components import (
    ConnectionIndicator,
    ConnectionStatus,
    ContextIndicator,
    ContextInfo,
    PerformanceIndicator,
    StatusBar,
    SystemMetrics,
)
from kritrima_ai.ui.widgets.text_buffer import TextBuffer, TextBufferWidget

__all__ = [
    # Text Buffer
    "TextBuffer",
    "TextBufferWidget",
    # Overlays
    "HelpOverlay",
    "DiffOverlay",
    "ApprovalModeOverlay",
    "ConfigOverlay",
    "FileSuggestionsOverlay",
    "DebugOverlay",
    # Spinners
    "ThinkingSpinner",
    "LoadingSpinner",
    "ProgressSpinner",
    # Advanced Input
    "AdvancedInput",
    "MultilineEditor",
    "FileTagInput",
    "CommandInput",
    # Chat Components
    "ChatMessage",
    "ChatMessageRenderer",
    "StreamingResponseWidget",
    "CodeBlockWidget",
    "DiffWidget",
    "ToolCallWidget",
    "ChatContainer",
    # Status Components
    "StatusBar",
    "PerformanceIndicator",
    "ContextIndicator",
    "ConnectionIndicator",
    "SystemMetrics",
    "ContextInfo",
    "ConnectionStatus",
    # Selection Components
    "ModelSelector",
    "ProviderSelector",
    "SessionBrowser",
    "HistoryBrowser",
    "ModelInfo",
    "ProviderInfo",
    "SessionInfo",
    "HistoryEntry",
]
