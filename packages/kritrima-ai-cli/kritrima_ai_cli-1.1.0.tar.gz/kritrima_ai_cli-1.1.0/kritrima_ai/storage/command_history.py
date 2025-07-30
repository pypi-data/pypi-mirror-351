"""
Command history management for Kritrima AI CLI.

This module provides comprehensive command history management with:
- Persistent storage across sessions
- Sensitive data filtering and sanitization
- Search and navigation capabilities
- Configurable size limits and retention
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from pydantic import BaseModel

from kritrima_ai.config.app_config import AppConfig, get_data_dir
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryEntry(BaseModel):
    """Single command history entry."""

    command: str
    timestamp: float
    session_id: Optional[str] = None
    success: Optional[bool] = None
    metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "command": self.command,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "success": self.success,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoryEntry":
        """Create from dictionary."""
        return cls(
            command=data["command"],
            timestamp=data["timestamp"],
            session_id=data.get("session_id"),
            success=data.get("success"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class HistoryConfig:
    """Configuration for command history."""

    max_size: int = 1000
    save_history: bool = True
    sensitive_patterns: List[str] = field(
        default_factory=lambda: [
            r"api[_-]?key\s*[=:]\s*['\"]?([a-zA-Z0-9_-]+)['\"]?",
            r"password\s*[=:]\s*['\"]?([^'\"\s]+)['\"]?",
            r"token\s*[=:]\s*['\"]?([a-zA-Z0-9_.-]+)['\"]?",
            r"secret\s*[=:]\s*['\"]?([a-zA-Z0-9_.-]+)['\"]?",
            r"auth[_-]?key\s*[=:]\s*['\"]?([a-zA-Z0-9_-]+)['\"]?",
            r"bearer\s+([a-zA-Z0-9_.-]+)",
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI API keys
            r"pk-[a-zA-Z0-9]{48}",  # Public keys
        ]
    )
    auto_save_interval: int = 60  # seconds
    dedup_consecutive: bool = True
    filter_sensitive: bool = True


class CommandHistory:
    """
    Comprehensive command history management system.

    Features:
    - Persistent storage with JSON format
    - Automatic sensitive data filtering
    - Configurable size limits and retention
    - Search and navigation capabilities
    - Async loading and saving
    - Session-aware history tracking
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize command history manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.history_file = get_data_dir() / "history" / "command_history.json"
        self.backup_file = self.history_file.with_suffix(".json.backup")

        # History configuration
        self.history_config = HistoryConfig(
            max_size=config.ui.max_history_items,
            save_history=True,
            auto_save_interval=60,
            dedup_consecutive=True,
            filter_sensitive=True,
        )

        # In-memory history
        self.entries: List[HistoryEntry] = []
        self.current_index = 0

        # Sensitive patterns (compiled regex)
        self._sensitive_patterns: List[re.Pattern] = []
        self._compile_sensitive_patterns()

        # Auto-save task
        self._auto_save_task: Optional[asyncio.Task] = None
        self._shutdown = False
        self._dirty = False

    async def initialize(self) -> None:
        """Initialize the command history system."""
        # Create history directory
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing history
        await self.load()

        # Start auto-save task
        self._auto_save_task = asyncio.create_task(self._auto_save_loop())

        logger.info(f"Command history initialized with {len(self.entries)} entries")

    async def load(self) -> bool:
        """
        Load command history from storage.

        Returns:
            True if load succeeded, False otherwise
        """
        try:
            if self.history_file.exists():
                async with aiofiles.open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.loads(await f.read())

                self.entries = [
                    HistoryEntry.from_dict(entry) for entry in data.get("entries", [])
                ]
                self.current_index = len(self.entries)

                logger.debug(f"Loaded {len(self.entries)} history entries")
                return True
            else:
                logger.debug("No history file found, starting with empty history")
                return True

        except Exception as e:
            logger.error(f"Error loading command history: {e}")

            # Try to load from backup
            if self.backup_file.exists():
                try:
                    async with aiofiles.open(
                        self.backup_file, "r", encoding="utf-8"
                    ) as f:
                        data = json.loads(await f.read())

                    self.entries = [
                        HistoryEntry.from_dict(entry)
                        for entry in data.get("entries", [])
                    ]
                    self.current_index = len(self.entries)

                    logger.info(f"Recovered {len(self.entries)} entries from backup")
                    return True
                except Exception as backup_e:
                    logger.error(f"Error loading backup history: {backup_e}")

            return False

    async def save(self) -> bool:
        """
        Save command history to storage.

        Returns:
            True if save succeeded, False otherwise
        """
        if not self.history_config.save_history:
            return True

        try:
            # Create backup of existing history
            if self.history_file.exists():
                async with aiofiles.open(self.history_file, "r", encoding="utf-8") as f:
                    backup_data = await f.read()

                async with aiofiles.open(self.backup_file, "w", encoding="utf-8") as f:
                    await f.write(backup_data)

            # Save current history
            history_data = {
                "version": "1.0",
                "saved_at": time.time(),
                "entry_count": len(self.entries),
                "entries": [entry.to_dict() for entry in self.entries],
            }

            async with aiofiles.open(self.history_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(history_data, indent=2, default=str))

            self._dirty = False
            logger.debug(f"Saved {len(self.entries)} history entries")
            return True

        except Exception as e:
            logger.error(f"Error saving command history: {e}")
            return False

    async def add_command(
        self,
        command: str,
        session_id: Optional[str] = None,
        success: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a command to the history.

        Args:
            command: Command string
            session_id: Optional session ID
            success: Whether command succeeded
            metadata: Additional metadata
        """
        # Filter sensitive data
        if self.history_config.filter_sensitive:
            filtered_command = self._filter_sensitive_data(command)
        else:
            filtered_command = command

        # Check for consecutive duplicates
        if (
            self.history_config.dedup_consecutive
            and self.entries
            and self.entries[-1].command == filtered_command
        ):
            logger.debug("Skipping duplicate consecutive command")
            return

        # Create history entry
        entry = HistoryEntry(
            command=filtered_command,
            timestamp=time.time(),
            session_id=session_id,
            success=success,
            metadata=metadata or {},
        )

        # Add to entries
        self.entries.append(entry)

        # Maintain size limit
        if len(self.entries) > self.history_config.max_size:
            # Remove oldest entries
            removed_count = len(self.entries) - self.history_config.max_size
            self.entries = self.entries[removed_count:]
            logger.debug(f"Removed {removed_count} old history entries")

        # Reset navigation index
        self.current_index = len(self.entries)

        # Mark as dirty for auto-save
        self._dirty = True

        logger.debug(f"Added command to history: {filtered_command[:50]}...")

    async def get_history(self, session_id: Optional[str] = None, limit: Optional[int] = None) -> List[HistoryEntry]:
        """
        Get command history entries.

        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of entries to return

        Returns:
            List of history entries
        """
        entries = self.entries.copy()
        
        # Filter by session if provided
        if session_id:
            entries = [entry for entry in entries if entry.session_id == session_id]
        
        # Apply limit
        if limit and limit > 0:
            entries = entries[-limit:]
        
        return entries

    def search_history(
        self, query: str, case_sensitive: bool = False
    ) -> List[HistoryEntry]:
        """
        Search command history.

        Args:
            query: Search query
            case_sensitive: Whether search should be case sensitive

        Returns:
            List of matching history entries
        """
        if not query:
            return []

        matches = []
        search_query = query if case_sensitive else query.lower()

        for entry in reversed(self.entries):
            command = entry.command if case_sensitive else entry.command.lower()

            if search_query in command:
                matches.append(entry)

        return matches

    def get_previous_command(self) -> Optional[str]:
        """
        Get previous command in navigation.

        Returns:
            Previous command or None if at beginning
        """
        if self.current_index > 0:
            self.current_index -= 1
            return self.entries[self.current_index].command

        return None

    def get_next_command(self) -> Optional[str]:
        """
        Get next command in navigation.

        Returns:
            Next command or None if at end
        """
        if self.current_index < len(self.entries) - 1:
            self.current_index += 1
            return self.entries[self.current_index].command
        elif self.current_index == len(self.entries) - 1:
            self.current_index = len(self.entries)
            return ""  # Return empty string when at end

        return None

    def reset_navigation(self) -> None:
        """Reset navigation to the end of history."""
        self.current_index = len(self.entries)

    def get_recent_commands(self, count: int = 10) -> List[str]:
        """
        Get recent commands without navigation.

        Args:
            count: Number of recent commands to return

        Returns:
            List of recent command strings
        """
        recent_entries = self.entries[-count:] if count > 0 else self.entries
        return [entry.command for entry in reversed(recent_entries)]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get history statistics.

        Returns:
            Dictionary with history statistics
        """
        if not self.entries:
            return {"total_commands": 0}

        total_commands = len(self.entries)
        unique_commands = len(set(entry.command for entry in self.entries))

        # Calculate time range
        oldest_entry = min(self.entries, key=lambda e: e.timestamp)
        newest_entry = max(self.entries, key=lambda e: e.timestamp)
        time_range = newest_entry.timestamp - oldest_entry.timestamp

        # Calculate success rate
        success_entries = [e for e in self.entries if e.success is not None]
        if success_entries:
            success_rate = sum(1 for e in success_entries if e.success) / len(
                success_entries
            )
        else:
            success_rate = None

        return {
            "total_commands": total_commands,
            "unique_commands": unique_commands,
            "time_range_hours": time_range / 3600 if time_range > 0 else 0,
            "success_rate": success_rate,
            "oldest_command": oldest_entry.timestamp if oldest_entry else None,
            "newest_command": newest_entry.timestamp if newest_entry else None,
        }

    def clear_history(self) -> None:
        """Clear all command history."""
        self.entries.clear()
        self.current_index = 0
        self._dirty = True
        logger.info("Command history cleared")

    def remove_session_history(self, session_id: str) -> int:
        """
        Remove all commands from a specific session.

        Args:
            session_id: Session ID to remove

        Returns:
            Number of entries removed
        """
        original_count = len(self.entries)
        self.entries = [e for e in self.entries if e.session_id != session_id]
        removed_count = original_count - len(self.entries)

        if removed_count > 0:
            self.current_index = len(self.entries)
            self._dirty = True
            logger.info(f"Removed {removed_count} entries from session {session_id}")

        return removed_count

    def _filter_sensitive_data(self, command: str) -> str:
        """
        Filter sensitive data from command.

        Args:
            command: Original command string

        Returns:
            Command with sensitive data replaced
        """
        filtered_command = command

        for pattern in self._sensitive_patterns:
            # Replace sensitive data with placeholder
            filtered_command = pattern.sub(
                lambda m: (
                    m.group(0).replace(m.group(1), "[FILTERED]")
                    if m.lastindex
                    else "[FILTERED]"
                ),
                filtered_command,
            )

        return filtered_command

    def _compile_sensitive_patterns(self) -> None:
        """Compile sensitive data regex patterns."""
        self._sensitive_patterns = []

        for pattern_str in self.history_config.sensitive_patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                self._sensitive_patterns.append(pattern)
            except re.error as e:
                logger.warning(f"Invalid sensitive pattern '{pattern_str}': {e}")

    async def _auto_save_loop(self) -> None:
        """Auto-save loop for periodic history saving."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.history_config.auto_save_interval)

                if self._dirty:
                    await self.save()

            except Exception as e:
                logger.error(f"Error in auto-save loop: {e}")

    async def shutdown(self) -> None:
        """Shutdown the command history system."""
        self._shutdown = True

        # Cancel auto-save task
        if self._auto_save_task:
            self._auto_save_task.cancel()
            try:
                await self._auto_save_task
            except asyncio.CancelledError:
                pass

        # Save final state
        if self._dirty:
            await self.save()

        logger.info("Command history shutdown completed")

    def export_history(self, output_path: Path, format: str = "json") -> bool:
        """
        Export command history to a file.

        Args:
            output_path: Path to save exported history
            format: Export format ("json" or "text")

        Returns:
            True if export succeeded, False otherwise
        """
        try:
            if format == "json":
                export_data = {
                    "export_info": {
                        "exported_at": time.time(),
                        "total_entries": len(self.entries),
                        "format": "json",
                    },
                    "entries": [entry.to_dict() for entry in self.entries],
                }

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, default=str)

            elif format == "text":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"# Command History Export\n")
                    f.write(f"# Exported at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Total entries: {len(self.entries)}\n\n")

                    for entry in self.entries:
                        timestamp_str = time.strftime(
                            "%Y-%m-%d %H:%M:%S", time.localtime(entry.timestamp)
                        )
                        f.write(f"[{timestamp_str}] {entry.command}\n")

            logger.info(
                f"Exported {len(self.entries)} history entries to {output_path}"
            )
            return True

        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            return False
