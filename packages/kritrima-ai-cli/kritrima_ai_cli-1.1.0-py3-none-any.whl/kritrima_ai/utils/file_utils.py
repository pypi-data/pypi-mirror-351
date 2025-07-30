"""
File utilities for Kritrima AI CLI.

This module provides safe file operations, content validation, and file
system utilities with proper error handling and security checks.
"""

import hashlib
import mimetypes
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import chardet

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


def read_file_safe(
    file_path: Path, encoding: str = "utf-8", max_size: int = 10_000_000  # 10MB default
) -> Optional[str]:
    """
    Safely read a file with size limits and error handling.

    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)
        max_size: Maximum file size in bytes

    Returns:
        File contents as string, or None if read failed.
    """
    try:
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            logger.warning(f"File too large ({file_size} bytes): {file_path}")
            return None

        # Auto-detect encoding if needed
        if encoding == "auto":
            detected_encoding = get_file_encoding(file_path)
            encoding = detected_encoding or "utf-8"

        # Read file content
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()

        logger.debug(f"Read file ({file_size} bytes): {file_path}")
        return content

    except UnicodeDecodeError as e:
        logger.warning(f"Encoding error reading {file_path}: {e}")
        # Try with auto-detection
        if encoding != "auto":
            return read_file_safe(file_path, "auto", max_size)
        return None
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def get_file_encoding(file_path: Path, sample_size: int = 8192) -> Optional[str]:
    """
    Detect file encoding using chardet.

    Args:
        file_path: Path to the file
        sample_size: Number of bytes to read for detection

    Returns:
        Detected encoding or None if detection failed.
    """
    try:
        with open(file_path, "rb") as f:
            sample = f.read(sample_size)

        if not sample:
            return None

        # Use chardet for detection
        try:
            result = chardet.detect(sample)
            if result and result["confidence"] > 0.7:
                return result["encoding"]
        except Exception:
            pass

        # Fallback to common encodings
        common_encodings = ["utf-8", "utf-16", "utf-32", "ascii", "latin1", "cp1252"]
        for encoding in common_encodings:
            try:
                sample.decode(encoding)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue

        return None

    except Exception as e:
        logger.error(f"Error detecting encoding for {file_path}: {e}")
        return None


def write_file_safe(
    file_path: Path,
    content: str,
    encoding: str = "utf-8",
    backup: bool = True,
    create_dirs: bool = True,
) -> bool:
    """
    Safely write content to a file with backup and error handling.

    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: File encoding (default: utf-8)
        backup: Create backup if file exists
        create_dirs: Create parent directories if needed

    Returns:
        True if write succeeded, False otherwise.
    """
    try:
        # Create parent directories if needed
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if file exists
        if backup and file_path.exists():
            backup_path = create_backup_file(file_path)
            if backup_path:
                logger.debug(f"Created backup: {backup_path}")

        # Write content to file
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)

        logger.debug(f"Wrote file ({len(content)} chars): {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return False


def create_backup_file(
    file_path: Path, backup_dir: Optional[Path] = None
) -> Optional[Path]:
    """
    Create a backup copy of a file.

    Args:
        file_path: Path to the file to backup
        backup_dir: Directory for backup (default: same as original)

    Returns:
        Path to backup file, or None if backup failed.
    """
    try:
        if not file_path.exists():
            return None

        # Determine backup location
        if backup_dir:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{file_path.name}.backup"
        else:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")

        # Copy file to backup location
        shutil.copy2(file_path, backup_path)

        return backup_path

    except Exception as e:
        logger.error(f"Error creating backup for {file_path}: {e}")
        return None


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get comprehensive information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information.
    """
    try:
        if not file_path.exists():
            return {"exists": False}

        stat = file_path.stat()

        info = {
            "exists": True,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "is_symlink": file_path.is_symlink(),
            "suffix": file_path.suffix,
            "stem": file_path.stem,
            "absolute_path": str(file_path.absolute()),
        }

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            info["mime_type"] = mime_type

        # Get file hash for regular files
        if file_path.is_file() and stat.st_size < 10_000_000:  # Only for files < 10MB
            info["md5"] = get_file_hash(file_path)

        return info

    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {"exists": False, "error": str(e)}


def get_file_hash(file_path: Path, algorithm: str = "md5") -> Optional[str]:
    """
    Calculate file hash.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        File hash as hex string, or None if failed.
    """
    try:
        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    except Exception as e:
        logger.error(f"Error calculating {algorithm} hash for {file_path}: {e}")
        return None


def is_text_file(file_path: Path, max_check_size: int = 1024) -> bool:
    """
    Check if a file appears to be a text file.

    Args:
        file_path: Path to the file
        max_check_size: Maximum bytes to check for text content

    Returns:
        True if file appears to be text, False otherwise.
    """
    try:
        if not file_path.is_file():
            return False

        # Check MIME type first
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith("text/"):
                return True
            if mime_type in [
                "application/json",
                "application/xml",
                "application/javascript",
            ]:
                return True

        # Check file extension
        text_extensions = {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".ts",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
            ".ps1",
            ".bat",
            ".cmd",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".java",
            ".cs",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".pl",
            ".swift",
            ".kt",
            ".scala",
            ".r",
            ".sql",
            ".dockerfile",
            ".makefile",
            ".cmake",
            ".gradle",
        }

        if file_path.suffix.lower() in text_extensions:
            return True

        # Check file content for binary data
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(max_check_size)

            # Check for null bytes (common in binary files)
            if b"\x00" in chunk:
                return False

            # Try to decode as UTF-8
            try:
                chunk.decode("utf-8")
                return True
            except UnicodeDecodeError:
                return False

        except Exception:
            return False

    except Exception as e:
        logger.debug(f"Error checking if {file_path} is text file: {e}")
        return False


def find_files(
    directory: Path,
    pattern: str = "*",
    recursive: bool = True,
    include_hidden: bool = False,
    max_files: int = 1000,
) -> List[Path]:
    """
    Find files matching a pattern in a directory.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        recursive: Search recursively
        include_hidden: Include hidden files/directories
        max_files: Maximum number of files to return

    Returns:
        List of matching file paths.
    """
    try:
        if not directory.exists() or not directory.is_dir():
            return []

        files = []

        if recursive:
            search_pattern = f"**/{pattern}"
        else:
            search_pattern = pattern

        for file_path in directory.glob(search_pattern):
            # Skip if we've reached the limit
            if len(files) >= max_files:
                logger.warning(f"Reached maximum file limit ({max_files})")
                break

            # Skip hidden files/directories if not requested
            if not include_hidden:
                if any(
                    part.startswith(".")
                    for part in file_path.parts[len(directory.parts) :]
                ):
                    continue

            # Only include files, not directories
            if file_path.is_file():
                files.append(file_path)

        return sorted(files)

    except Exception as e:
        logger.error(f"Error finding files in {directory}: {e}")
        return []


def get_directory_size(directory: Path) -> int:
    """
    Calculate total size of a directory and its contents.

    Args:
        directory: Directory to calculate size for

    Returns:
        Total size in bytes.
    """
    try:
        total_size = 0

        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                try:
                    total_size += file_path.stat().st_size
                except (OSError, FileNotFoundError):
                    # Skip files that can't be accessed
                    continue

        return total_size

    except Exception as e:
        logger.error(f"Error calculating directory size for {directory}: {e}")
        return 0


def clean_temp_files(temp_dir: Optional[Path] = None, max_age_hours: int = 24) -> int:
    """
    Clean up old temporary files.

    Args:
        temp_dir: Temporary directory to clean (default: system temp)
        max_age_hours: Maximum age of files to keep

    Returns:
        Number of files cleaned up.
    """
    try:
        if not temp_dir:
            temp_dir = Path(tempfile.gettempdir())

        if not temp_dir.exists():
            return 0

        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0

        # Look for kritrima-ai temp files
        for file_path in temp_dir.glob("kritrima-ai-*"):
            try:
                file_age = current_time - file_path.stat().st_mtime

                if file_age > max_age_seconds:
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        cleaned_count += 1

            except Exception as e:
                logger.debug(f"Error cleaning temp file {file_path}: {e}")

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} temporary files")

        return cleaned_count

    except Exception as e:
        logger.error(f"Error cleaning temp files: {e}")
        return 0


def resolve_path_safely(path: str, base_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Safely resolve a path, preventing directory traversal attacks.

    Args:
        path: Path string to resolve
        base_dir: Base directory to resolve against (default: current dir)

    Returns:
        Resolved Path object, or None if path is unsafe.
    """
    try:
        if not base_dir:
            base_dir = Path.cwd()

        # Convert to Path and resolve
        path_obj = Path(path)

        # Handle absolute paths
        if path_obj.is_absolute():
            resolved = path_obj.resolve()
        else:
            resolved = (base_dir / path_obj).resolve()

        # Check if resolved path is within base directory
        try:
            resolved.relative_to(base_dir.resolve())
        except ValueError:
            logger.warning(f"Path outside base directory: {path}")
            return None

        return resolved

    except Exception as e:
        logger.error(f"Error resolving path {path}: {e}")
        return None


def create_temp_file(
    content: str = "",
    suffix: str = ".tmp",
    prefix: str = "kritrima-ai-",
    encoding: str = "utf-8",
) -> Optional[Path]:
    """
    Create a temporary file with content.

    Args:
        content: Content to write to the file
        suffix: File suffix
        prefix: File prefix
        encoding: File encoding

    Returns:
        Path to created temporary file, or None if failed.
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, prefix=prefix, encoding=encoding, delete=False
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        logger.debug(f"Created temporary file: {temp_path}")
        return temp_path

    except Exception as e:
        logger.error(f"Error creating temporary file: {e}")
        return None


def validate_file_permissions(file_path: Path, required_permissions: str = "r") -> bool:
    """
    Validate file permissions.

    Args:
        file_path: Path to check
        required_permissions: Required permissions (r, w, x)

    Returns:
        True if permissions are sufficient, False otherwise.
    """
    try:
        if not file_path.exists():
            return False

        for perm in required_permissions:
            if perm == "r" and not os.access(file_path, os.R_OK):
                return False
            elif perm == "w" and not os.access(file_path, os.W_OK):
                return False
            elif perm == "x" and not os.access(file_path, os.X_OK):
                return False

        return True

    except Exception as e:
        logger.error(f"Error checking permissions for {file_path}: {e}")
        return False


def get_file_line_count(file_path: Path) -> int:
    """
    Get the number of lines in a file efficiently.

    Args:
        file_path: Path to the file

    Returns:
        Number of lines in the file.
    """
    try:
        with open(file_path, "rb") as f:
            line_count = sum(1 for _ in f)

        return line_count

    except Exception as e:
        logger.error(f"Error counting lines in {file_path}: {e}")
        return 0


def get_file_suggestions(
    directory: Path = None, pattern: str = "*", limit: int = 50
) -> List[str]:
    """
    Get file suggestions for auto-completion and commands.

    Args:
        directory: Directory to search in (default: current directory)
        pattern: File pattern to match
        limit: Maximum number of suggestions

    Returns:
        List of file path suggestions
    """
    try:
        if directory is None:
            directory = Path.cwd()

        if not directory.exists():
            return []

        suggestions = []

        # Get matching files
        files = find_files(
            directory=directory,
            pattern=pattern,
            recursive=False,  # Only immediate directory for suggestions
            max_files=limit,
        )

        # Convert to relative path strings
        for file_path in files[:limit]:
            try:
                rel_path = file_path.relative_to(directory)
                suggestions.append(str(rel_path))
            except ValueError:
                # If relative path fails, use absolute
                suggestions.append(str(file_path))

        # Sort suggestions
        suggestions.sort()

        return suggestions

    except Exception as e:
        logger.error(f"Error getting file suggestions: {e}")
        return []


class FileUtils:
    """
    Utility class for common file operations.

    Provides a convenient interface for file operations
    with error handling and logging.
    """

    def __init__(self, config):
        """
        Initialize FileUtils.

        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = get_logger(__name__)

    def read_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """Read file safely with error handling."""
        return read_file_safe(Path(file_path))

    def write_file(self, file_path: Union[str, Path], content: str) -> bool:
        """Write file safely with error handling."""
        return write_file_safe(Path(file_path), content)

    def backup_file(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Create backup of file."""
        return create_backup_file(Path(file_path))

    def get_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get file information."""
        return get_file_info(Path(file_path))

    def find_files_matching(
        self, pattern: str, directory: Union[str, Path] = None
    ) -> List[Path]:
        """Find files matching pattern."""
        if directory is None:
            directory = Path.cwd()
        return find_files(Path(directory), pattern)

    def is_text(self, file_path: Union[str, Path]) -> bool:
        """Check if file is text file."""
        return is_text_file(Path(file_path))

    def get_suggestions(
        self, pattern: str = "*", directory: Union[str, Path] = None
    ) -> List[str]:
        """Get file suggestions for auto-completion."""
        if directory is None:
            directory = Path.cwd()
        return get_file_suggestions(Path(directory), pattern)
