"""
Desktop notification system for Kritrima AI CLI.

This module provides cross-platform desktop notifications for various events
including AI responses, tool executions, and system alerts.
"""

import asyncio
import platform
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationType(Enum):
    """Types of notifications."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    AI_RESPONSE = "ai_response"
    TOOL_EXECUTION = "tool_execution"


@dataclass
class NotificationConfig:
    """Notification configuration."""

    enabled: bool = True
    show_ai_responses: bool = True
    show_tool_executions: bool = True
    show_errors: bool = True
    show_warnings: bool = True
    sound_enabled: bool = True
    icon_path: Optional[str] = None


class DesktopNotificationManager:
    """
    Cross-platform desktop notification manager.

    Provides desktop notifications for various events using platform-specific
    notification systems (macOS Notification Center, Windows toast, Linux notify-send).
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the notification manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.notification_config = NotificationConfig(
            enabled=config.ui.notifications,
            show_ai_responses=getattr(
                config.ui, "show_ai_response_notifications", True
            ),
            show_tool_executions=getattr(
                config.ui, "show_tool_execution_notifications", True
            ),
            show_errors=getattr(config.ui, "show_error_notifications", True),
            show_warnings=getattr(config.ui, "show_warning_notifications", True),
            sound_enabled=getattr(config.ui, "notification_sound", True),
        )

        self.platform = platform.system().lower()
        self.notification_method = self._detect_notification_method()

        logger.info(f"Desktop notifications initialized for {self.platform}")

    def _detect_notification_method(self) -> str:
        """Detect the best notification method for the current platform."""
        if self.platform == "darwin":  # macOS
            return "osascript"
        elif self.platform == "windows":  # Windows
            if self._command_exists("powershell"):
                return "powershell"
            else:
                return "msg"
        elif self.platform == "linux":  # Linux
            if self._command_exists("notify-send"):
                return "notify-send"
            elif self._command_exists("zenity"):
                return "zenity"
            else:
                return "terminal"
        else:
            return "terminal"

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run(
                [command, "--version"], capture_output=True, check=False, timeout=5
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            return False

    async def notify(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        icon: Optional[str] = None,
        sound: Optional[str] = None,
        timeout: int = 5,
    ) -> bool:
        """
        Send a desktop notification.

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            icon: Custom icon path
            sound: Custom sound name
            timeout: Notification timeout in seconds

        Returns:
            True if notification was sent successfully
        """
        if not self.notification_config.enabled:
            return False

        # Check type-specific settings
        if not self._should_show_notification(notification_type):
            return False

        try:
            # Clean and truncate message
            clean_title = self._clean_text(title)[:50]
            clean_message = self._clean_text(message)[:200]

            if self.notification_method == "osascript":
                return await self._notify_macos(
                    clean_title, clean_message, notification_type, sound
                )
            elif self.notification_method == "powershell":
                return await self._notify_windows_powershell(
                    clean_title, clean_message, notification_type
                )
            elif self.notification_method == "msg":
                return await self._notify_windows_msg(clean_title, clean_message)
            elif self.notification_method == "notify-send":
                return await self._notify_linux_notify_send(
                    clean_title, clean_message, notification_type, icon, timeout
                )
            elif self.notification_method == "zenity":
                return await self._notify_linux_zenity(
                    clean_title, clean_message, notification_type
                )
            else:
                # Fallback to terminal output
                return await self._notify_terminal(
                    clean_title, clean_message, notification_type
                )

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def _should_show_notification(self, notification_type: NotificationType) -> bool:
        """Check if a notification type should be shown based on configuration."""
        if notification_type == NotificationType.AI_RESPONSE:
            return self.notification_config.show_ai_responses
        elif notification_type == NotificationType.TOOL_EXECUTION:
            return self.notification_config.show_tool_executions
        elif notification_type == NotificationType.ERROR:
            return self.notification_config.show_errors
        elif notification_type == NotificationType.WARNING:
            return self.notification_config.show_warnings
        else:
            return True

    def _clean_text(self, text: str) -> str:
        """Clean text for safe use in notifications."""
        # Remove problematic characters and escape quotes
        cleaned = text.replace('"', '\\"').replace("'", "\\'")
        cleaned = cleaned.replace("\n", " ").replace("\r", " ")
        return cleaned.strip()

    async def _notify_macos(
        self,
        title: str,
        message: str,
        notification_type: NotificationType,
        sound: Optional[str] = None,
    ) -> bool:
        """Send notification on macOS using osascript."""
        try:
            # Determine sound
            if self.notification_config.sound_enabled and sound is None:
                sound_map = {
                    NotificationType.SUCCESS: "Glass",
                    NotificationType.ERROR: "Basso",
                    NotificationType.WARNING: "Sosumi",
                    NotificationType.AI_RESPONSE: "Ping",
                    NotificationType.TOOL_EXECUTION: "Pop",
                }
                sound = sound_map.get(notification_type, "default")

            # Build AppleScript command
            script_parts = [
                "display notification",
                f'"{message}"',
                f'with title "{title}"',
                f'subtitle "Kritrima AI CLI"',
            ]

            if sound and self.notification_config.sound_enabled:
                script_parts.append(f'sound name "{sound}"')

            script = " ".join(script_parts)

            # Execute osascript
            result = await self._run_command(["osascript", "-e", script])

            return result.returncode == 0

        except Exception as e:
            logger.error(f"macOS notification failed: {e}")
            return False

    async def _notify_windows_powershell(
        self, title: str, message: str, notification_type: NotificationType
    ) -> bool:
        """Send notification on Windows using PowerShell and Windows Toast."""
        try:
            # PowerShell script for Windows 10+ toast notifications
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)

            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Kritrima AI CLI").Show($toast)
            """

            result = await self._run_command(["powershell", "-Command", ps_script])

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Windows PowerShell notification failed: {e}")
            return False

    async def _notify_windows_msg(self, title: str, message: str) -> bool:
        """Send notification on Windows using msg command (fallback)."""
        try:
            # Simple message box notification
            full_message = f"{title}\n\n{message}"

            result = await self._run_command(["msg", "*", full_message])

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Windows msg notification failed: {e}")
            return False

    async def _notify_linux_notify_send(
        self,
        title: str,
        message: str,
        notification_type: NotificationType,
        icon: Optional[str] = None,
        timeout: int = 5,
    ) -> bool:
        """Send notification on Linux using notify-send."""
        try:
            # Determine urgency and icon
            urgency_map = {
                NotificationType.ERROR: "critical",
                NotificationType.WARNING: "normal",
                NotificationType.SUCCESS: "low",
                NotificationType.AI_RESPONSE: "normal",
                NotificationType.TOOL_EXECUTION: "low",
            }
            urgency = urgency_map.get(notification_type, "normal")

            # Default icons
            if not icon:
                icon_map = {
                    NotificationType.ERROR: "dialog-error",
                    NotificationType.WARNING: "dialog-warning",
                    NotificationType.SUCCESS: "dialog-information",
                    NotificationType.AI_RESPONSE: "dialog-information",
                    NotificationType.TOOL_EXECUTION: "system-run",
                }
                icon = icon_map.get(notification_type, "dialog-information")

            # Build notify-send command
            cmd = [
                "notify-send",
                f"--urgency={urgency}",
                f"--expire-time={timeout * 1000}",  # milliseconds
                f"--icon={icon}",
                f"--app-name=Kritrima AI CLI",
                title,
                message,
            ]

            result = await self._run_command(cmd)
            return result.returncode == 0

        except Exception as e:
            logger.error(f"Linux notify-send notification failed: {e}")
            return False

    async def _notify_linux_zenity(
        self, title: str, message: str, notification_type: NotificationType
    ) -> bool:
        """Send notification on Linux using zenity (fallback)."""
        try:
            zenity_type = "info"
            if notification_type == NotificationType.ERROR:
                zenity_type = "error"
            elif notification_type == NotificationType.WARNING:
                zenity_type = "warning"

            cmd = [
                "zenity",
                f"--{zenity_type}",
                f"--title={title}",
                f"--text={message}",
                "--no-wrap",
            ]

            result = await self._run_command(cmd)
            return result.returncode == 0

        except Exception as e:
            logger.error(f"Linux zenity notification failed: {e}")
            return False

    async def _notify_terminal(
        self, title: str, message: str, notification_type: NotificationType
    ) -> bool:
        """Fallback terminal notification."""
        try:
            # Use ANSI colors for terminal output
            color_map = {
                NotificationType.ERROR: "\033[91m",  # Red
                NotificationType.WARNING: "\033[93m",  # Yellow
                NotificationType.SUCCESS: "\033[92m",  # Green
                NotificationType.AI_RESPONSE: "\033[96m",  # Cyan
                NotificationType.TOOL_EXECUTION: "\033[94m",  # Blue
                NotificationType.INFO: "\033[97m",  # White
            }

            color = color_map.get(notification_type, "\033[97m")
            reset = "\033[0m"

            # Print to stderr so it doesn't interfere with main output
            notification_text = f"{color}[{title}] {message}{reset}"
            print(notification_text, file=sys.stderr)

            return True

        except Exception as e:
            logger.error(f"Terminal notification failed: {e}")
            return False

    async def _run_command(
        self, cmd: list, timeout: int = 10
    ) -> subprocess.CompletedProcess:
        """Run a command asynchronously."""
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                result.communicate(), timeout=timeout
            )

            return subprocess.CompletedProcess(cmd, result.returncode, stdout, stderr)

        except asyncio.TimeoutError:
            logger.warning(f"Command timeout: {' '.join(cmd)}")
            raise
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise

    # Convenience methods for common notification types
    async def notify_ai_response(self, message: str, model: str = "") -> bool:
        """Send AI response notification."""
        title = f"AI Response"
        if model:
            title += f" ({model})"

        return await self.notify(
            title=title,
            message=message[:100] + "..." if len(message) > 100 else message,
            notification_type=NotificationType.AI_RESPONSE,
        )

    async def notify_tool_execution(
        self, tool_name: str, status: str = "completed"
    ) -> bool:
        """Send tool execution notification."""
        return await self.notify(
            title="Tool Execution",
            message=f"{tool_name} {status}",
            notification_type=NotificationType.TOOL_EXECUTION,
        )

    async def notify_error(self, error_message: str) -> bool:
        """Send error notification."""
        return await self.notify(
            title="Error",
            message=error_message,
            notification_type=NotificationType.ERROR,
        )

    async def notify_success(self, message: str) -> bool:
        """Send success notification."""
        return await self.notify(
            title="Success", message=message, notification_type=NotificationType.SUCCESS
        )


# Global notification manager instance
_notification_manager: Optional[DesktopNotificationManager] = None


def initialize_notifications(config: AppConfig) -> DesktopNotificationManager:
    """Initialize the global notification manager."""
    global _notification_manager
    _notification_manager = DesktopNotificationManager(config)
    return _notification_manager


def get_notification_manager() -> Optional[DesktopNotificationManager]:
    """Get the global notification manager instance."""
    return _notification_manager


# Convenience functions for easy notification sending
async def notify_ai_response(message: str, model: str = "") -> bool:
    """Send AI response notification."""
    if _notification_manager:
        return await _notification_manager.notify_ai_response(message, model)
    return False


async def notify_tool_execution(tool_name: str, status: str = "completed") -> bool:
    """Send tool execution notification."""
    if _notification_manager:
        return await _notification_manager.notify_tool_execution(tool_name, status)
    return False


async def notify_error(error_message: str) -> bool:
    """Send error notification."""
    if _notification_manager:
        return await _notification_manager.notify_error(error_message)
    return False


async def notify_success(message: str) -> bool:
    """Send success notification."""
    if _notification_manager:
        return await _notification_manager.notify_success(message)
    return False
