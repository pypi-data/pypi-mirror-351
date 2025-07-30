"""
File operations tool for Kritrima AI CLI.

This module provides comprehensive file manipulation capabilities including:
- Reading and writing files
- Directory operations
- File searching and filtering
- Backup and restore functionality
- Patch application and diff generation
"""

import difflib
import shutil
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, List, Optional

from kritrima_ai.agent.base_tool import (
    BaseTool,
    ToolExecutionResult,
    ToolMetadata,
    create_parameter_schema,
    create_tool_metadata,
)
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.security.sandbox import SandboxManager
from kritrima_ai.utils.file_utils import get_file_encoding, is_text_file, read_file_safe
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class FileOperationsTool(BaseTool):
    """
    Comprehensive file operations tool for the AI agent.

    Provides safe file manipulation capabilities with backup support,
    security checks, and comprehensive error handling.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the file operations tool.

        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.sandbox = SandboxManager(config)
        self._backup_dir = Path.home() / ".kritrima-ai" / "backups"
        self._backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info("File operations tool initialized")

    def get_metadata(self) -> ToolMetadata:
        """Get metadata for the file operations tool."""
        return create_tool_metadata(
            name="file_operations",
            description="Comprehensive file and directory operations including read, write, copy, move, delete, search, and diff operations",
            parameters=create_parameter_schema(
                properties={
                    "operation": {
                        "type": "string",
                        "enum": [
                            "read",
                            "write",
                            "append",
                            "delete",
                            "copy",
                            "move",
                            "list",
                            "create_dir",
                            "search",
                            "diff",
                            "patch",
                            "info",
                        ],
                        "description": "The file operation to perform",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file or directory",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write or append (for write/append operations)",
                    },
                    "destination_path": {
                        "type": "string",
                        "description": "Destination path (for copy/move operations)",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern (for search operations)",
                    },
                    "encoding": {
                        "type": "string",
                        "default": "utf-8",
                        "description": "File encoding",
                    },
                    "create_backup": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to create backup before modifying files",
                    },
                    "recursive": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to perform recursive operations",
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to show hidden files",
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File types to filter (e.g., ['.py', '.txt'])",
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of search results",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to overwrite existing files",
                    },
                },
                required=["operation", "file_path"],
            ),
            category="file_system",
            risk_level="medium",
            requires_approval=True,
            supports_streaming=True,
            examples=[
                {
                    "description": "Read a file",
                    "parameters": {"operation": "read", "file_path": "example.txt"},
                },
                {
                    "description": "Write content to a file",
                    "parameters": {
                        "operation": "write",
                        "file_path": "output.txt",
                        "content": "Hello, World!",
                    },
                },
                {
                    "description": "List directory contents",
                    "parameters": {
                        "operation": "list",
                        "file_path": ".",
                        "recursive": True,
                    },
                },
            ],
        )

    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute file operations based on the specified operation type.

        Args:
            **kwargs: Operation parameters

        Returns:
            Tool execution result
        """
        try:
            operation = kwargs.get("operation")
            if not operation:
                return ToolExecutionResult(
                    success=False, result=None, error="Operation parameter is required"
                )

            # Route to appropriate method based on operation
            if operation == "read":
                result = await self.read_file(
                    kwargs.get("file_path"), kwargs.get("encoding", "utf-8")
                )
            elif operation == "write":
                result = await self.write_file(
                    kwargs.get("file_path"),
                    kwargs.get("content", ""),
                    kwargs.get("encoding", "utf-8"),
                    kwargs.get("create_backup", True),
                )
            elif operation == "append":
                result = await self.append_to_file(
                    kwargs.get("file_path"),
                    kwargs.get("content", ""),
                    kwargs.get("encoding", "utf-8"),
                    kwargs.get("create_backup", True),
                )
            elif operation == "delete":
                result = await self.delete_file(
                    kwargs.get("file_path"), kwargs.get("create_backup", True)
                )
            elif operation == "copy":
                result = await self.copy_file(
                    kwargs.get("file_path"),
                    kwargs.get("destination_path"),
                    kwargs.get("overwrite", False),
                )
            elif operation == "move":
                result = await self.move_file(
                    kwargs.get("file_path"),
                    kwargs.get("destination_path"),
                    kwargs.get("create_backup", True),
                )
            elif operation == "list":
                result = await self.list_directory(
                    kwargs.get("file_path", "."),
                    kwargs.get("show_hidden", False),
                    kwargs.get("recursive", False),
                    kwargs.get("file_types"),
                )
            elif operation == "create_dir":
                result = await self.create_directory(
                    kwargs.get("file_path"), kwargs.get("parents", True)
                )
            elif operation == "search":
                result = await self.search_files(
                    kwargs.get("file_path", "."),
                    kwargs.get("pattern", "*"),
                    kwargs.get("content_search"),
                    kwargs.get("file_types"),
                    kwargs.get("max_results", 100),
                )
            elif operation == "diff":
                result = await self.create_diff(
                    kwargs.get("file_path"), kwargs.get("destination_path")
                )
            elif operation == "patch":
                result = await self.apply_patch(
                    kwargs.get("file_path"),
                    kwargs.get("content"),
                    kwargs.get("create_backup", True),
                )
            elif operation == "info":
                result = await self.get_file_info(kwargs.get("file_path"))
            else:
                return ToolExecutionResult(
                    success=False, result=None, error=f"Unknown operation: {operation}"
                )

            return ToolExecutionResult(
                success=True,
                result=result,
                metadata={"operation": operation, "file_path": kwargs.get("file_path")},
            )

        except Exception as e:
            logger.error(f"File operation failed: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute file operations with streaming output for large operations.

        Args:
            **kwargs: Operation parameters

        Yields:
            Streaming output chunks
        """
        operation = kwargs.get("operation")

        try:
            if operation in ["read", "list", "search"]:
                # For operations that can produce large output, stream the results
                result = await self.execute(**kwargs)
                if result.success:
                    # Split large results into chunks
                    content = str(result.result)
                    chunk_size = 1024  # 1KB chunks
                    for i in range(0, len(content), chunk_size):
                        yield content[i : i + chunk_size]
                else:
                    yield f"Error: {result.error}"
            else:
                # For other operations, just yield the final result
                result = await self.execute(**kwargs)
                if result.success:
                    yield str(result.result)
                else:
                    yield f"Error: {result.error}"

        except Exception as e:
            yield f"Error: {str(e)}"

    async def read_file(
        self,
        file_path: str,
        encoding: str = "utf-8",
        max_size: int = 10 * 1024 * 1024,  # 10MB default
    ) -> str:
        """
        Read a file safely with encoding detection and size limits.

        Args:
            file_path: Path to the file to read
            encoding: File encoding (auto-detected if not specified)
            max_size: Maximum file size in bytes

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
            ValueError: If file is too large or not text
        """
        try:
            path = Path(file_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "read"):
                raise PermissionError(f"Access denied to file: {path}")

            # Check if file exists
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            # Check file size
            file_size = path.stat().st_size
            if file_size > max_size:
                raise ValueError(f"File too large: {file_size} bytes (max: {max_size})")

            # Check if it's a text file
            if not is_text_file(path):
                raise ValueError(f"File is not a text file: {path}")

            # Auto-detect encoding if not specified
            if encoding == "utf-8":
                detected_encoding = get_file_encoding(path)
                if detected_encoding:
                    encoding = detected_encoding

            # Read file content
            content = read_file_safe(path, encoding)

            logger.info(f"Read file: {path} ({file_size} bytes)")
            return content

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    async def write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        create_backup: bool = True,
        create_dirs: bool = True,
    ) -> str:
        """
        Write content to a file with backup support.

        Args:
            file_path: Path to the file to write
            content: Content to write
            encoding: File encoding
            create_backup: Whether to create a backup of existing file
            create_dirs: Whether to create parent directories

        Returns:
            Success message with file info

        Raises:
            PermissionError: If file can't be written
            OSError: If directory creation fails
        """
        try:
            path = Path(file_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "write"):
                raise PermissionError(f"Access denied to file: {path}")

            # Create parent directories if needed
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directories: {path.parent}")

            # Create backup if file exists
            backup_path = None
            if create_backup and path.exists():
                backup_path = await self._create_backup(path)

            # Write content
            with open(path, "w", encoding=encoding) as f:
                f.write(content)

            file_size = path.stat().st_size
            result = f"File written: {path} ({file_size} bytes)"

            if backup_path:
                result += f"\nBackup created: {backup_path}"

            logger.info(f"Wrote file: {path} ({file_size} bytes)")
            return result

        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise

    async def append_to_file(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        create_backup: bool = True,
    ) -> str:
        """
        Append content to a file.

        Args:
            file_path: Path to the file
            content: Content to append
            encoding: File encoding
            create_backup: Whether to create a backup

        Returns:
            Success message
        """
        try:
            path = Path(file_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "write"):
                raise PermissionError(f"Access denied to file: {path}")

            # Create backup if file exists
            backup_path = None
            if create_backup and path.exists():
                backup_path = await self._create_backup(path)

            # Append content
            with open(path, "a", encoding=encoding) as f:
                f.write(content)

            file_size = path.stat().st_size
            result = f"Content appended to: {path} (new size: {file_size} bytes)"

            if backup_path:
                result += f"\nBackup created: {backup_path}"

            logger.info(f"Appended to file: {path}")
            return result

        except Exception as e:
            logger.error(f"Error appending to file {file_path}: {e}")
            raise

    async def delete_file(self, file_path: str, create_backup: bool = True) -> str:
        """
        Delete a file with optional backup.

        Args:
            file_path: Path to the file to delete
            create_backup: Whether to create a backup before deletion

        Returns:
            Success message
        """
        try:
            path = Path(file_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "write"):
                raise PermissionError(f"Access denied to file: {path}")

            if not path.exists():
                return f"File does not exist: {path}"

            # Create backup if requested
            backup_path = None
            if create_backup:
                backup_path = await self._create_backup(path)

            # Delete file
            path.unlink()

            result = f"File deleted: {path}"
            if backup_path:
                result += f"\nBackup created: {backup_path}"

            logger.info(f"Deleted file: {path}")
            return result

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise

    async def copy_file(
        self, source_path: str, destination_path: str, overwrite: bool = False
    ) -> str:
        """
        Copy a file to a new location.

        Args:
            source_path: Source file path
            destination_path: Destination file path
            overwrite: Whether to overwrite existing files

        Returns:
            Success message
        """
        try:
            src = Path(source_path).resolve()
            dst = Path(destination_path).resolve()

            # Security checks
            if not self.sandbox.is_path_allowed(src, "read"):
                raise PermissionError(f"Access denied to source: {src}")
            if not self.sandbox.is_path_allowed(dst, "write"):
                raise PermissionError(f"Access denied to destination: {dst}")

            if not src.exists():
                raise FileNotFoundError(f"Source file not found: {src}")

            if dst.exists() and not overwrite:
                raise FileExistsError(f"Destination exists: {dst}")

            # Create parent directories
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(src, dst)

            src_size = src.stat().st_size
            result = f"File copied: {src} -> {dst} ({src_size} bytes)"

            logger.info(f"Copied file: {src} -> {dst}")
            return result

        except Exception as e:
            logger.error(f"Error copying file {source_path} to {destination_path}: {e}")
            raise

    async def move_file(
        self, source_path: str, destination_path: str, create_backup: bool = True
    ) -> str:
        """
        Move a file to a new location.

        Args:
            source_path: Source file path
            destination_path: Destination file path
            create_backup: Whether to create a backup

        Returns:
            Success message
        """
        try:
            src = Path(source_path).resolve()
            dst = Path(destination_path).resolve()

            # Security checks
            if not self.sandbox.is_path_allowed(src, "write"):
                raise PermissionError(f"Access denied to source: {src}")
            if not self.sandbox.is_path_allowed(dst, "write"):
                raise PermissionError(f"Access denied to destination: {dst}")

            if not src.exists():
                raise FileNotFoundError(f"Source file not found: {src}")

            # Create backup if destination exists
            backup_path = None
            if create_backup and dst.exists():
                backup_path = await self._create_backup(dst)

            # Create parent directories
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(src), str(dst))

            result = f"File moved: {src} -> {dst}"
            if backup_path:
                result += f"\nBackup created: {backup_path}"

            logger.info(f"Moved file: {src} -> {dst}")
            return result

        except Exception as e:
            logger.error(f"Error moving file {source_path} to {destination_path}: {e}")
            raise

    async def list_directory(
        self,
        directory_path: str = ".",
        show_hidden: bool = False,
        recursive: bool = False,
        file_types: Optional[List[str]] = None,
    ) -> str:
        """
        List directory contents with filtering options.

        Args:
            directory_path: Directory to list
            show_hidden: Whether to show hidden files
            recursive: Whether to list recursively
            file_types: File extensions to filter by

        Returns:
            Formatted directory listing
        """
        try:
            path = Path(directory_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "read"):
                raise PermissionError(f"Access denied to directory: {path}")

            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")

            if not path.is_dir():
                raise NotADirectoryError(f"Not a directory: {path}")

            items = []

            if recursive:
                for item in path.rglob("*"):
                    if self._should_include_item(item, show_hidden, file_types):
                        items.append(item)
            else:
                for item in path.iterdir():
                    if self._should_include_item(item, show_hidden, file_types):
                        items.append(item)

            # Sort items
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))

            # Format output
            result = [f"Directory: {path}"]
            result.append(f"Items: {len(items)}")
            result.append("")

            for item in items:
                relative_path = item.relative_to(path) if recursive else item.name
                if item.is_dir():
                    result.append(f"📁 {relative_path}/")
                else:
                    size = item.stat().st_size
                    result.append(f"📄 {relative_path} ({size} bytes)")

            logger.info(f"Listed directory: {path} ({len(items)} items)")
            return "\n".join(result)

        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            raise

    async def create_directory(self, directory_path: str, parents: bool = True) -> str:
        """
        Create a directory.

        Args:
            directory_path: Directory path to create
            parents: Whether to create parent directories

        Returns:
            Success message
        """
        try:
            path = Path(directory_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "write"):
                raise PermissionError(f"Access denied to directory: {path}")

            if path.exists():
                return f"Directory already exists: {path}"

            # Create directory
            path.mkdir(parents=parents, exist_ok=True)

            result = f"Directory created: {path}"
            logger.info(f"Created directory: {path}")
            return result

        except Exception as e:
            logger.error(f"Error creating directory {directory_path}: {e}")
            raise

    async def search_files(
        self,
        directory_path: str = ".",
        pattern: str = "*",
        content_search: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        max_results: int = 100,
    ) -> str:
        """
        Search for files by name pattern and/or content.

        Args:
            directory_path: Directory to search in
            pattern: File name pattern (glob)
            content_search: Text to search for in file contents
            file_types: File extensions to include
            max_results: Maximum number of results

        Returns:
            Search results
        """
        try:
            path = Path(directory_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "read"):
                raise PermissionError(f"Access denied to directory: {path}")

            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")

            results = []

            # Search by pattern
            for item in path.rglob(pattern):
                if len(results) >= max_results:
                    break

                if not item.is_file():
                    continue

                if file_types and item.suffix.lower() not in file_types:
                    continue

                # Content search if specified
                if content_search:
                    try:
                        if is_text_file(item):
                            content = read_file_safe(item)
                            if content_search.lower() in content.lower():
                                results.append((item, True))
                        else:
                            continue
                    except Exception:
                        continue
                else:
                    results.append((item, False))

            # Format results
            result_lines = [f"Search results in: {path}"]
            result_lines.append(f"Pattern: {pattern}")
            if content_search:
                result_lines.append(f"Content search: {content_search}")
            result_lines.append(f"Found: {len(results)} files")
            result_lines.append("")

            for file_path, has_content in results:
                relative_path = file_path.relative_to(path)
                size = file_path.stat().st_size
                marker = "📄✨" if has_content else "📄"
                result_lines.append(f"{marker} {relative_path} ({size} bytes)")

            if len(results) >= max_results:
                result_lines.append(f"\n... (limited to {max_results} results)")

            logger.info(f"File search completed: {len(results)} results")
            return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error searching files in {directory_path}: {e}")
            raise

    async def create_diff(
        self, file1_path: str, file2_path: str, context_lines: int = 3
    ) -> str:
        """
        Create a diff between two files.

        Args:
            file1_path: First file path
            file2_path: Second file path
            context_lines: Number of context lines

        Returns:
            Unified diff output
        """
        try:
            path1 = Path(file1_path).resolve()
            path2 = Path(file2_path).resolve()

            # Security checks
            if not self.sandbox.is_path_allowed(path1, "read"):
                raise PermissionError(f"Access denied to file: {path1}")
            if not self.sandbox.is_path_allowed(path2, "read"):
                raise PermissionError(f"Access denied to file: {path2}")

            # Read files
            content1 = read_file_safe(path1).splitlines(keepends=True)
            content2 = read_file_safe(path2).splitlines(keepends=True)

            # Generate diff
            diff = difflib.unified_diff(
                content1,
                content2,
                fromfile=str(path1),
                tofile=str(path2),
                n=context_lines,
            )

            diff_text = "".join(diff)

            if not diff_text:
                return f"No differences found between {path1} and {path2}"

            logger.info(f"Created diff between {path1} and {path2}")
            return diff_text

        except Exception as e:
            logger.error(
                f"Error creating diff between {file1_path} and {file2_path}: {e}"
            )
            raise

    async def apply_patch(
        self, file_path: str, patch_content: str, create_backup: bool = True
    ) -> str:
        """
        Apply a patch to a file.

        Args:
            file_path: Target file path
            patch_content: Patch content in unified diff format
            create_backup: Whether to create a backup

        Returns:
            Success message
        """
        try:
            path = Path(file_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "write"):
                raise PermissionError(f"Access denied to file: {path}")

            # Create backup if requested
            backup_path = None
            if create_backup and path.exists():
                backup_path = await self._create_backup(path)

            # Read original content
            if path.exists():
                original_content = read_file_safe(path).splitlines(keepends=True)
            else:
                original_content = []

            # Parse and apply patch
            patch_lines = patch_content.splitlines()
            patched_content = self._apply_unified_diff(original_content, patch_lines)

            # Write patched content
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(patched_content)

            result = f"Patch applied to: {path}"
            if backup_path:
                result += f"\nBackup created: {backup_path}"

            logger.info(f"Applied patch to: {path}")
            return result

        except Exception as e:
            logger.error(f"Error applying patch to {file_path}: {e}")
            raise

    async def get_file_info(self, file_path: str) -> str:
        """
        Get detailed information about a file.

        Args:
            file_path: File path

        Returns:
            File information
        """
        try:
            path = Path(file_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "read"):
                raise PermissionError(f"Access denied to file: {path}")

            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            stat = path.stat()

            info = [
                f"File: {path}",
                f"Size: {stat.st_size} bytes",
                f"Type: {'Directory' if path.is_dir() else 'File'}",
                f"Modified: {datetime.fromtimestamp(stat.st_mtime)}",
                f"Created: {datetime.fromtimestamp(stat.st_ctime)}",
                f"Permissions: {oct(stat.st_mode)[-3:]}",
            ]

            if path.is_file():
                info.append(f"Extension: {path.suffix}")
                if is_text_file(path):
                    encoding = get_file_encoding(path)
                    info.append(f"Encoding: {encoding}")

                    # Line count for text files
                    try:
                        content = read_file_safe(path)
                        line_count = content.count("\n") + 1
                        info.append(f"Lines: {line_count}")
                    except Exception:
                        pass

            logger.info(f"Retrieved file info: {path}")
            return "\n".join(info)

        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            raise

    async def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{timestamp}"
        backup_path = self._backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path

    def _should_include_item(
        self, item: Path, show_hidden: bool, file_types: Optional[List[str]]
    ) -> bool:
        """Check if an item should be included in listings."""
        # Hidden files check
        if not show_hidden and item.name.startswith("."):
            return False

        # File type filter
        if file_types and item.is_file():
            if item.suffix.lower() not in file_types:
                return False

        return True

    def _apply_unified_diff(
        self, original_lines: List[str], patch_lines: List[str]
    ) -> List[str]:
        """Apply a unified diff patch to content."""
        # This is a simplified patch application
        # In a production system, you'd want a more robust implementation
        result_lines = original_lines.copy()

        # Parse patch and apply changes
        # This is a basic implementation - real patch application is more complex
        i = 0
        while i < len(patch_lines):
            line = patch_lines[i]
            if line.startswith("@@"):
                # Parse hunk header
                # Format: @@ -start,count +start,count @@
                parts = line.split()
                if len(parts) >= 3:
                    old_info = parts[1][1:]  # Remove '-'
                    new_info = parts[2][1:]  # Remove '+'

                    old_start = int(old_info.split(",")[0]) - 1  # Convert to 0-based

                    # Apply changes in this hunk
                    j = i + 1
                    line_offset = 0

                    while j < len(patch_lines) and not patch_lines[j].startswith("@@"):
                        patch_line = patch_lines[j]
                        if patch_line.startswith("-"):
                            # Remove line
                            if old_start + line_offset < len(result_lines):
                                result_lines.pop(old_start + line_offset)
                                line_offset -= 1
                        elif patch_line.startswith("+"):
                            # Add line
                            new_line = patch_line[1:]  # Remove '+'
                            result_lines.insert(old_start + line_offset + 1, new_line)
                            line_offset += 1
                        elif patch_line.startswith(" "):
                            # Context line - no change needed
                            pass
                        j += 1

                    i = j - 1
            i += 1

        return result_lines
