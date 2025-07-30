"""
Status components for Kritrima AI CLI terminal interface.

This module provides status indicators, performance monitors, and context displays
for enhanced user awareness of system state and performance.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.timer import Timer
from textual.widgets import Static

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Connection status types."""

    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class PerformanceLevel(Enum):
    """Performance level indicators."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class SystemMetrics:
    """System performance metrics."""

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used: int = 0
    memory_total: int = 0
    disk_usage: float = 0.0
    network_sent: int = 0
    network_recv: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def memory_used_mb(self) -> float:
        """Memory used in MB."""
        return self.memory_used / (1024 * 1024)

    @property
    def memory_total_mb(self) -> float:
        """Total memory in MB."""
        return self.memory_total / (1024 * 1024)


@dataclass
class ContextInfo:
    """Context information for the current session."""

    current_model: str = "Unknown"
    provider: str = "Unknown"
    session_id: str = ""
    workspace_path: str = ""
    active_files: List[str] = field(default_factory=list)
    token_count: int = 0
    message_count: int = 0
    session_duration: timedelta = field(default_factory=timedelta)


class StatusBar(Container):
    """Main status bar widget showing system status and context."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 3;
        background: $surface;
        border-top: solid $border;
    }
    
    StatusBar .left {
        width: 1fr;
        padding: 0 1;
    }
    
    StatusBar .center {
        width: auto;
        padding: 0 1;
    }
    
    StatusBar .right {
        width: auto;
        padding: 0 1;
    }
    
    StatusBar .status-item {
        margin: 0 1;
    }
    
    StatusBar .connected {
        color: $success;
    }
    
    StatusBar .connecting {
        color: $warning;
    }
    
    StatusBar .disconnected {
        color: $error;
    }
    
    StatusBar .error {
        color: $error;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_info = ContextInfo()
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.last_update = datetime.now()
        self.update_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        """Compose the status bar."""
        with Horizontal():
            # Left section - Context info
            with Container(classes="left"):
                yield Static("", id="context-info")

            # Center section - Connection status
            with Container(classes="center"):
                yield Static("", id="connection-status")

            # Right section - Time and performance
            with Container(classes="right"):
                yield Static("", id="time-info")

    def on_mount(self) -> None:
        """Start status updates when mounted."""
        self.update_timer = self.set_interval(1.0, self.update_status)
        self.update_status()

    def on_unmount(self) -> None:
        """Stop updates when unmounted."""
        if self.update_timer:
            self.update_timer.stop()

    def update_context(self, context: ContextInfo) -> None:
        """Update context information."""
        self.context_info = context
        self.update_status()

    def update_connection(self, status: ConnectionStatus) -> None:
        """Update connection status."""
        self.connection_status = status
        self.update_status()

    def update_status(self) -> None:
        """Update all status displays."""
        self._update_context_display()
        self._update_connection_display()
        self._update_time_display()

    def _update_context_display(self) -> None:
        """Update context information display."""
        context_widget = self.query_one("#context-info", Static)

        parts = []
        if self.context_info.current_model:
            parts.append(f"Model: {self.context_info.current_model}")

        if self.context_info.provider:
            parts.append(f"Provider: {self.context_info.provider}")

        if self.context_info.message_count > 0:
            parts.append(f"Messages: {self.context_info.message_count}")

        if self.context_info.token_count > 0:
            parts.append(f"Tokens: {self.context_info.token_count:,}")

        context_text = " | ".join(parts) if parts else "No active session"
        context_widget.update(context_text)

    def _update_connection_display(self) -> None:
        """Update connection status display."""
        status_widget = self.query_one("#connection-status", Static)

        status_icons = {
            ConnectionStatus.CONNECTED: "🟢",
            ConnectionStatus.CONNECTING: "🟡",
            ConnectionStatus.DISCONNECTED: "🔴",
            ConnectionStatus.ERROR: "❌",
            ConnectionStatus.RATE_LIMITED: "⏳",
        }

        icon = status_icons.get(self.connection_status, "❓")
        status_text = f"{icon} {self.connection_status.value.title()}"

        status_widget.update(status_text)
        status_widget.set_class(self.connection_status.value, True)

    def _update_time_display(self) -> None:
        """Update time and session duration display."""
        time_widget = self.query_one("#time-info", Static)

        current_time = datetime.now().strftime("%H:%M:%S")
        duration = datetime.now() - (
            datetime.now() - self.context_info.session_duration
        )
        duration_str = str(duration).split(".")[0]  # Remove microseconds

        time_text = f"{current_time} | Session: {duration_str}"
        time_widget.update(time_text)


class PerformanceIndicator(Container):
    """Widget showing system performance metrics."""

    DEFAULT_CSS = """
    PerformanceIndicator {
        height: auto;
        border: solid $border;
        padding: 1;
        margin: 1 0;
    }
    
    PerformanceIndicator .header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    PerformanceIndicator .metric {
        margin: 0 0 1 0;
    }
    
    PerformanceIndicator .excellent {
        color: $success;
    }
    
    PerformanceIndicator .good {
        color: $success;
    }
    
    PerformanceIndicator .fair {
        color: $warning;
    }
    
    PerformanceIndicator .poor {
        color: $error;
    }
    
    PerformanceIndicator .critical {
        color: $error;
        text-style: bold;
    }
    """

    def __init__(self, update_interval: float = 2.0, **kwargs):
        super().__init__(**kwargs)
        self.update_interval = update_interval
        self.metrics = SystemMetrics()
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 60  # Keep 60 data points
        self.update_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        """Compose the performance indicator."""
        yield Static("📊 System Performance", classes="header")
        yield Static("", id="cpu-metric", classes="metric")
        yield Static("", id="memory-metric", classes="metric")
        yield Static("", id="disk-metric", classes="metric")
        yield Static("", id="network-metric", classes="metric")

    def on_mount(self) -> None:
        """Start performance monitoring when mounted."""
        self.update_timer = self.set_interval(self.update_interval, self.update_metrics)
        self.update_metrics()

    def on_unmount(self) -> None:
        """Stop monitoring when unmounted."""
        if self.update_timer:
            self.update_timer.stop()

    def update_metrics(self) -> None:
        """Update system metrics."""
        try:
            # Get current metrics
            self.metrics = SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=None),
                memory_percent=psutil.virtual_memory().percent,
                memory_used=psutil.virtual_memory().used,
                memory_total=psutil.virtual_memory().total,
                disk_usage=psutil.disk_usage("/").percent,
                timestamp=datetime.now(),
            )

            # Add to history
            self.metrics_history.append(self.metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)

            # Update display
            self._update_display()

        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    def _update_display(self) -> None:
        """Update the performance display."""
        # CPU
        cpu_widget = self.query_one("#cpu-metric", Static)
        cpu_level = self._get_performance_level(
            self.metrics.cpu_percent, [20, 40, 60, 80]
        )
        cpu_text = f"CPU: {self.metrics.cpu_percent:5.1f}% {self._get_bar(self.metrics.cpu_percent)}"
        cpu_widget.update(cpu_text)
        cpu_widget.set_class(cpu_level.value, True)

        # Memory
        memory_widget = self.query_one("#memory-metric", Static)
        memory_level = self._get_performance_level(
            self.metrics.memory_percent, [30, 50, 70, 85]
        )
        memory_text = f"RAM: {self.metrics.memory_percent:5.1f}% ({self.metrics.memory_used_mb:,.0f}MB) {self._get_bar(self.metrics.memory_percent)}"
        memory_widget.update(memory_text)
        memory_widget.set_class(memory_level.value, True)

        # Disk
        disk_widget = self.query_one("#disk-metric", Static)
        disk_level = self._get_performance_level(
            self.metrics.disk_usage, [50, 70, 85, 95]
        )
        disk_text = f"Disk: {self.metrics.disk_usage:5.1f}% {self._get_bar(self.metrics.disk_usage)}"
        disk_widget.update(disk_text)
        disk_widget.set_class(disk_level.value, True)

        # Network (simplified)
        network_widget = self.query_one("#network-metric", Static)
        network_text = f"Network: {self._format_bytes(self.metrics.network_sent)}↑ {self._format_bytes(self.metrics.network_recv)}↓"
        network_widget.update(network_text)

    def _get_performance_level(
        self, value: float, thresholds: List[float]
    ) -> PerformanceLevel:
        """Get performance level based on value and thresholds."""
        if value <= thresholds[0]:
            return PerformanceLevel.EXCELLENT
        elif value <= thresholds[1]:
            return PerformanceLevel.GOOD
        elif value <= thresholds[2]:
            return PerformanceLevel.FAIR
        elif value <= thresholds[3]:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL

    def _get_bar(self, percentage: float, width: int = 10) -> str:
        """Generate a simple text-based progress bar."""
        filled = int(percentage / 100 * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes in human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_value < 1024:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f}TB"


class ContextIndicator(Container):
    """Widget showing current context and session information."""

    DEFAULT_CSS = """
    ContextIndicator {
        height: auto;
        border: solid $border;
        padding: 1;
        margin: 1 0;
    }
    
    ContextIndicator .header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    ContextIndicator .context-item {
        margin: 0 0 1 0;
    }
    
    ContextIndicator .active {
        color: $success;
    }
    
    ContextIndicator .inactive {
        color: $text-muted;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = ContextInfo()
        self.update_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        """Compose the context indicator."""
        yield Static("🎯 Current Context", classes="header")
        yield Static("", id="model-info", classes="context-item")
        yield Static("", id="session-info", classes="context-item")
        yield Static("", id="workspace-info", classes="context-item")
        yield Static("", id="files-info", classes="context-item")

    def on_mount(self) -> None:
        """Start context updates when mounted."""
        self.update_timer = self.set_interval(5.0, self.update_display)
        self.update_display()

    def on_unmount(self) -> None:
        """Stop updates when unmounted."""
        if self.update_timer:
            self.update_timer.stop()

    def update_context(self, context: ContextInfo) -> None:
        """Update context information."""
        self.context = context
        self.update_display()

    def update_display(self) -> None:
        """Update the context display."""
        # Model info
        model_widget = self.query_one("#model-info", Static)
        model_text = f"Model: {self.context.current_model} ({self.context.provider})"
        model_widget.update(model_text)
        model_widget.set_class(
            "active" if self.context.current_model != "Unknown" else "inactive", True
        )

        # Session info
        session_widget = self.query_one("#session-info", Static)
        session_text = f"Session: {self.context.session_id[:8]}... | Messages: {self.context.message_count} | Tokens: {self.context.token_count:,}"
        session_widget.update(session_text)
        session_widget.set_class(
            "active" if self.context.session_id else "inactive", True
        )

        # Workspace info
        workspace_widget = self.query_one("#workspace-info", Static)
        workspace_path = self.context.workspace_path
        if len(workspace_path) > 50:
            workspace_path = "..." + workspace_path[-47:]
        workspace_text = f"Workspace: {workspace_path or 'None'}"
        workspace_widget.update(workspace_text)
        workspace_widget.set_class(
            "active" if self.context.workspace_path else "inactive", True
        )

        # Active files
        files_widget = self.query_one("#files-info", Static)
        file_count = len(self.context.active_files)
        if file_count == 0:
            files_text = "Files: None"
            files_widget.set_class("inactive", True)
        else:
            files_text = f"Files: {file_count} active"
            if file_count <= 3:
                files_text += f" ({', '.join(self.context.active_files)})"
            files_widget.set_class("active", True)
        files_widget.update(files_text)


class ConnectionIndicator(Container):
    """Widget showing connection status and API information."""

    DEFAULT_CSS = """
    ConnectionIndicator {
        height: auto;
        border: solid $border;
        padding: 1;
        margin: 1 0;
    }
    
    ConnectionIndicator .header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    ConnectionIndicator .connection-item {
        margin: 0 0 1 0;
    }
    
    ConnectionIndicator .connected {
        color: $success;
    }
    
    ConnectionIndicator .connecting {
        color: $warning;
    }
    
    ConnectionIndicator .disconnected {
        color: $error;
    }
    
    ConnectionIndicator .error {
        color: $error;
        text-style: bold;
    }
    
    ConnectionIndicator .rate-limited {
        color: $warning;
        text-style: italic;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connections: Dict[str, ConnectionStatus] = {}
        self.api_info: Dict[str, Dict[str, Any]] = {}
        self.update_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        """Compose the connection indicator."""
        yield Static("🌐 Connections", classes="header")
        yield Static("", id="primary-connection", classes="connection-item")
        yield Static("", id="api-status", classes="connection-item")
        yield Static("", id="rate-limits", classes="connection-item")

    def on_mount(self) -> None:
        """Start connection monitoring when mounted."""
        self.update_timer = self.set_interval(3.0, self.update_display)
        self.update_display()

    def on_unmount(self) -> None:
        """Stop monitoring when unmounted."""
        if self.update_timer:
            self.update_timer.stop()

    def update_connection(
        self,
        provider: str,
        status: ConnectionStatus,
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update connection status for a provider."""
        self.connections[provider] = status
        if info:
            self.api_info[provider] = info
        self.update_display()

    def update_display(self) -> None:
        """Update the connection display."""
        # Primary connection
        primary_widget = self.query_one("#primary-connection", Static)
        if self.connections:
            primary_provider = list(self.connections.keys())[0]
            primary_status = self.connections[primary_provider]
            status_icon = self._get_status_icon(primary_status)
            primary_text = (
                f"{status_icon} {primary_provider}: {primary_status.value.title()}"
            )
            primary_widget.update(primary_text)
            primary_widget.set_class(primary_status.value, True)
        else:
            primary_widget.update("No active connections")
            primary_widget.set_class("disconnected", True)

        # API status
        api_widget = self.query_one("#api-status", Static)
        connected_count = sum(
            1
            for status in self.connections.values()
            if status == ConnectionStatus.CONNECTED
        )
        total_count = len(self.connections)
        api_text = f"APIs: {connected_count}/{total_count} connected"
        api_widget.update(api_text)

        # Rate limits
        rate_widget = self.query_one("#rate-limits", Static)
        rate_limited = [
            provider
            for provider, status in self.connections.items()
            if status == ConnectionStatus.RATE_LIMITED
        ]
        if rate_limited:
            rate_text = f"Rate Limited: {', '.join(rate_limited)}"
            rate_widget.set_class("rate-limited", True)
        else:
            rate_text = "Rate Limits: OK"
            rate_widget.set_class("connected", True)
        rate_widget.update(rate_text)

    def _get_status_icon(self, status: ConnectionStatus) -> str:
        """Get icon for connection status."""
        icons = {
            ConnectionStatus.CONNECTED: "🟢",
            ConnectionStatus.CONNECTING: "🟡",
            ConnectionStatus.DISCONNECTED: "🔴",
            ConnectionStatus.ERROR: "❌",
            ConnectionStatus.RATE_LIMITED: "⏳",
        }
        return icons.get(status, "❓")


# Status update messages
class StatusUpdate(Message):
    """Status update message."""

    def __init__(self, component: str, data: Dict[str, Any]) -> None:
        super().__init__()
        self.component = component
        self.data = data


class ContextUpdate(Message):
    """Context update message."""

    def __init__(self, context: ContextInfo) -> None:
        super().__init__()
        self.context = context


class ConnectionUpdate(Message):
    """Connection update message."""

    def __init__(
        self,
        provider: str,
        status: ConnectionStatus,
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self.provider = provider
        self.status = status
        self.info = info or {}


class PerformanceUpdate(Message):
    """Performance metrics update message."""

    def __init__(self, metrics: SystemMetrics) -> None:
        super().__init__()
        self.metrics = metrics
