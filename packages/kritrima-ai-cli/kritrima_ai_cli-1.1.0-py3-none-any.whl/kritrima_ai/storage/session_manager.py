"""
Session management system for Kritrima AI CLI.

This module provides comprehensive session management with persistent storage,
automatic saving, compression, and recovery capabilities.
"""

import asyncio
import gzip
import json
import shutil
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from pydantic import BaseModel

from kritrima_ai.config.app_config import AppConfig, get_data_dir
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class MessageRole(BaseModel):
    """Message role in a conversation."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float
    metadata: Dict[str, Any] = {}


class ToolCall(BaseModel):
    """Tool call information."""

    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: float
    approved: bool = False


@dataclass
class Session:
    """Session data structure."""

    session_id: str
    created_at: float
    updated_at: float
    messages: List[MessageRole] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_temporary: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [msg.model_dump() for msg in self.messages],
            "tool_calls": [call.model_dump() for call in self.tool_calls],
            "context": self.context,
            "metadata": self.metadata,
            "is_temporary": self.is_temporary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary."""
        messages = [MessageRole(**msg) for msg in data.get("messages", [])]
        tool_calls = [ToolCall(**call) for call in data.get("tool_calls", [])]

        return cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages,
            tool_calls=tool_calls,
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
            is_temporary=data.get("is_temporary", False),
        )

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to the session."""
        message = MessageRole(
            role=role, content=content, timestamp=time.time(), metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = time.time()

    def add_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Optional[str] = None,
        execution_time: Optional[float] = None,
        approved: bool = False,
    ) -> None:
        """Add a tool call to the session."""
        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            execution_time=execution_time,
            timestamp=time.time(),
            approved=approved,
        )
        self.tool_calls.append(tool_call)
        self.updated_at = time.time()

    def get_size(self) -> int:
        """Get approximate size of session in bytes."""
        return len(json.dumps(self.to_dict(), default=str))


class SessionManager:
    """
    Comprehensive session management system.

    Features:
    - Persistent session storage
    - Automatic session saving and rollouts
    - Session compression for old sessions
    - Session recovery and restoration
    - Export/import capabilities
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize session manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.sessions_dir = get_data_dir() / "sessions"
        self.current_session: Optional[Session] = None

        # Auto-save settings
        self.auto_save_interval = config.session.auto_save_interval
        self.max_session_size = config.session.max_session_size
        self.compress_old_sessions = config.session.compress_old_sessions
        self.session_retention_days = config.session.session_retention_days

        # Auto-save task
        self._auto_save_task: Optional[asyncio.Task] = None
        self._shutdown = False

    async def initialize(self) -> None:
        """Initialize the session manager."""
        # Create sessions directory
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Clean up old sessions
        await self._cleanup_old_sessions()

        # Start auto-save task
        if self.config.ui.auto_save:
            self._auto_save_task = asyncio.create_task(self._auto_save_loop())

        logger.info("Session manager initialized")

    async def create_session(self, temporary: bool = False) -> str:
        """
        Create a new session.

        Args:
            temporary: Whether this is a temporary session

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        current_time = time.time()

        session = Session(
            session_id=session_id,
            created_at=current_time,
            updated_at=current_time,
            is_temporary=temporary,
        )

        # Add system context
        session.context = {
            "created_by": "kritrima-ai",
            "version": "1.0.0",
            "platform": self.config.debug,  # Add platform info
        }

        self.current_session = session

        # Save session immediately if not temporary
        if not temporary:
            await self.save_session(session)

        logger.info(f"Created {'temporary ' if temporary else ''}session: {session_id}")
        return session_id

    async def load_session(self, session_id: str) -> Optional[Session]:
        """
        Load a session by ID.

        Args:
            session_id: Session ID to load

        Returns:
            Session object if found, None otherwise
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        compressed_file = self.sessions_dir / f"{session_id}.json.gz"

        try:
            # Try regular file first
            if session_file.exists():
                async with aiofiles.open(session_file, "r", encoding="utf-8") as f:
                    data = json.loads(await f.read())
                    return Session.from_dict(data)

            # Try compressed file
            elif compressed_file.exists():
                with gzip.open(compressed_file, "rt", encoding="utf-8") as f:
                    data = json.load(f)
                    return Session.from_dict(data)

            else:
                logger.warning(f"Session file not found: {session_id}")
                return None

        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None

    async def save_session(self, session: Session) -> bool:
        """
        Save a session to storage.

        Args:
            session: Session to save

        Returns:
            True if save succeeded, False otherwise
        """
        if session.is_temporary:
            return True  # Don't save temporary sessions

        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"

            # Check if session is too large
            session_data = session.to_dict()
            if session.get_size() > self.max_session_size:
                logger.warning(f"Session {session.session_id} exceeds size limit")
                # Could implement session compaction here

            # Save session
            async with aiofiles.open(session_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(session_data, indent=2, default=str))

            # Create rollout file for backup
            await self._create_rollout(session)

            logger.debug(f"Saved session: {session.session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")
            return False

    async def save_current_session(self) -> bool:
        """Save the current session."""
        if self.current_session:
            return await self.save_session(self.current_session)
        return True

    async def list_sessions(
        self, include_temporary: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all available sessions.

        Args:
            include_temporary: Whether to include temporary sessions

        Returns:
            List of session metadata
        """
        sessions = []

        try:
            # List JSON files
            for session_file in self.sessions_dir.glob("*.json"):
                if session_file.name.startswith("rollout-"):
                    continue  # Skip rollout files

                try:
                    async with aiofiles.open(session_file, "r", encoding="utf-8") as f:
                        data = json.loads(await f.read())

                    if not include_temporary and data.get("is_temporary", False):
                        continue

                    sessions.append(
                        {
                            "session_id": data["session_id"],
                            "created_at": data["created_at"],
                            "updated_at": data["updated_at"],
                            "message_count": len(data.get("messages", [])),
                            "tool_call_count": len(data.get("tool_calls", [])),
                            "is_temporary": data.get("is_temporary", False),
                            "size": len(json.dumps(data, default=str)),
                        }
                    )

                except Exception as e:
                    logger.debug(f"Error reading session file {session_file}: {e}")

            # List compressed files
            for compressed_file in self.sessions_dir.glob("*.json.gz"):
                try:
                    with gzip.open(compressed_file, "rt", encoding="utf-8") as f:
                        data = json.load(f)

                    if not include_temporary and data.get("is_temporary", False):
                        continue

                    sessions.append(
                        {
                            "session_id": data["session_id"],
                            "created_at": data["created_at"],
                            "updated_at": data["updated_at"],
                            "message_count": len(data.get("messages", [])),
                            "tool_call_count": len(data.get("tool_calls", [])),
                            "is_temporary": data.get("is_temporary", False),
                            "size": compressed_file.stat().st_size,
                            "compressed": True,
                        }
                    )

                except Exception as e:
                    logger.debug(
                        f"Error reading compressed session file {compressed_file}: {e}"
                    )

            # Sort by updated_at descending
            sessions.sort(key=lambda s: s["updated_at"], reverse=True)
            return sessions

        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deletion succeeded, False otherwise
        """
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            compressed_file = self.sessions_dir / f"{session_id}.json.gz"

            deleted = False

            if session_file.exists():
                session_file.unlink()
                deleted = True

            if compressed_file.exists():
                compressed_file.unlink()
                deleted = True

            # Also delete rollout files
            for rollout_file in self.sessions_dir.glob(f"rollout-*-{session_id}.json"):
                rollout_file.unlink()

            if deleted:
                logger.info(f"Deleted session: {session_id}")
                return True
            else:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False

    async def export_session(self, session_id: str, output_path: Path) -> bool:
        """
        Export a session to a file.

        Args:
            session_id: Session ID to export
            output_path: Path to save the exported session

        Returns:
            True if export succeeded, False otherwise
        """
        try:
            session = await self.load_session(session_id)
            if not session:
                return False

            export_data = {
                "export_info": {
                    "exported_at": time.time(),
                    "exported_by": "kritrima-ai",
                    "version": "1.0.0",
                },
                "session": session.to_dict(),
            }

            async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(export_data, indent=2, default=str))

            logger.info(f"Exported session {session_id} to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting session {session_id}: {e}")
            return False

    async def import_session(self, input_path: Path) -> Optional[str]:
        """
        Import a session from a file.

        Args:
            input_path: Path to the session file to import

        Returns:
            Session ID if import succeeded, None otherwise
        """
        try:
            async with aiofiles.open(input_path, "r", encoding="utf-8") as f:
                data = json.loads(await f.read())

            session_data = data.get(
                "session", data
            )  # Support both export format and raw session
            session = Session.from_dict(session_data)

            # Generate new session ID to avoid conflicts
            session.session_id = str(uuid.uuid4())
            session.metadata["imported_from"] = str(input_path)
            session.metadata["imported_at"] = time.time()

            # Save imported session
            success = await self.save_session(session)
            if success:
                logger.info(
                    f"Imported session from {input_path} as {session.session_id}"
                )
                return session.session_id
            else:
                return None

        except Exception as e:
            logger.error(f"Error importing session from {input_path}: {e}")
            return None

    async def _create_rollout(self, session: Session) -> None:
        """Create a rollout backup file for the session."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            rollout_file = (
                self.sessions_dir / f"rollout-{timestamp}-{session.session_id}.json"
            )

            rollout_data = {
                "rollout_info": {
                    "created_at": time.time(),
                    "session_id": session.session_id,
                    "message_count": len(session.messages),
                    "tool_call_count": len(session.tool_calls),
                },
                "session": session.to_dict(),
            }

            async with aiofiles.open(rollout_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(rollout_data, indent=2, default=str))

            logger.debug(f"Created rollout: {rollout_file}")

        except Exception as e:
            logger.debug(
                f"Error creating rollout for session {session.session_id}: {e}"
            )

    async def _auto_save_loop(self) -> None:
        """Auto-save loop for periodic session saving."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.auto_save_interval)

                if self.current_session and not self.current_session.is_temporary:
                    await self.save_session(self.current_session)
                    logger.debug("Auto-saved current session")

            except Exception as e:
                logger.error(f"Error in auto-save loop: {e}")

    async def _cleanup_old_sessions(self) -> None:
        """Clean up old sessions based on retention policy."""
        try:
            cutoff_time = time.time() - (self.session_retention_days * 24 * 3600)
            cleaned_count = 0

            # Clean up old session files
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    if session_file.stat().st_mtime < cutoff_time:
                        # Compress before deletion if enabled
                        if (
                            self.compress_old_sessions
                            and not session_file.name.startswith("rollout-")
                        ):
                            await self._compress_session_file(session_file)
                        else:
                            session_file.unlink()
                        cleaned_count += 1
                except Exception as e:
                    logger.debug(f"Error cleaning session file {session_file}: {e}")

            # Clean up old rollout files
            for rollout_file in self.sessions_dir.glob("rollout-*.json"):
                try:
                    if rollout_file.stat().st_mtime < cutoff_time:
                        rollout_file.unlink()
                        cleaned_count += 1
                except Exception as e:
                    logger.debug(f"Error cleaning rollout file {rollout_file}: {e}")

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old session files")

        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")

    async def _compress_session_file(self, session_file: Path) -> None:
        """Compress a session file to save space."""
        try:
            compressed_file = session_file.with_suffix(".json.gz")

            with open(session_file, "rb") as f_in:
                with gzip.open(compressed_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove original file
            session_file.unlink()

            logger.debug(f"Compressed session file: {session_file}")

        except Exception as e:
            logger.error(f"Error compressing session file {session_file}: {e}")

    async def shutdown(self) -> None:
        """Shutdown the session manager."""
        self._shutdown = True

        # Cancel auto-save task
        if self._auto_save_task:
            self._auto_save_task.cancel()
            try:
                await self._auto_save_task
            except asyncio.CancelledError:
                pass

        # Save current session one last time
        await self.save_current_session()

        logger.info("Session manager shutdown completed")

    def get_current_session(self) -> Optional[Session]:
        """Get the current session."""
        return self.current_session

    def add_message_to_current(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to the current session."""
        if self.current_session:
            self.current_session.add_message(role, content, metadata)

    def add_tool_call_to_current(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Optional[str] = None,
        execution_time: Optional[float] = None,
        approved: bool = False,
    ) -> None:
        """Add a tool call to the current session."""
        if self.current_session:
            self.current_session.add_tool_call(
                tool_name, arguments, result, execution_time, approved
            )

    async def start_session(self, temporary: bool = False) -> str:
        """
        Start a new session.

        Args:
            temporary: Whether this is a temporary session

        Returns:
            Session ID
        """
        # Initialize if not already done
        if not self.sessions_dir.exists():
            await self.initialize()
        
        session_id = await self.create_session(temporary=temporary)
        
        # Log session start
        logger.info(f"Started new session: {session_id}")
        
        return session_id

    async def end_session(self, session_id: str) -> bool:
        """
        End a session and save it.

        Args:
            session_id: Session ID to end

        Returns:
            True if session was ended successfully
        """
        try:
            if self.current_session and self.current_session.session_id == session_id:
                # Save current session
                await self.save_current_session()
                
                # Clear current session
                self.current_session = None
                
                logger.info(f"Ended session: {session_id}")
                return True
            else:
                # Try to load and save the session
                session = await self.load_session(session_id)
                if session:
                    await self.save_session(session)
                    logger.info(f"Ended session: {session_id}")
                    return True
                else:
                    logger.warning(f"Session not found: {session_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False

    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session information
        """
        try:
            session = None
            
            # Check if it's the current session
            if self.current_session and self.current_session.session_id == session_id:
                session = self.current_session
            else:
                # Try to load the session
                session = await self.load_session(session_id)
            
            if session:
                return {
                    "session_id": session.session_id,
                    "start_time": datetime.fromtimestamp(session.created_at).isoformat(),
                    "last_updated": datetime.fromtimestamp(session.updated_at).isoformat(),
                    "message_count": len(session.messages),
                    "tool_call_count": len(session.tool_calls),
                    "command_count": len([msg for msg in session.messages if msg.role == "user"]),
                    "session_size": session.get_size(),
                    "is_temporary": session.is_temporary,
                    "is_active": session.session_id == (self.current_session.session_id if self.current_session else None),
                    "metadata": session.metadata,
                    "context_keys": list(session.context.keys())
                }
            else:
                logger.warning(f"Session not found: {session_id}")
                return {
                    "session_id": session_id,
                    "error": "Session not found",
                    "start_time": None,
                    "command_count": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting session info for {session_id}: {e}")
            return {
                "session_id": session_id,
                "error": str(e),
                "start_time": None,
                "command_count": 0
            }
