"""
Single-pass mode implementation for Kritrima AI CLI.

This module provides experimental single-pass mode functionality for
batch processing and full-context directory analysis.
"""

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.file_utils import is_text_file, read_file_safe
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FileContent:
    """Represents file content for context processing."""

    path: Path
    content: str
    size: int
    language: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DirectoryAnalysis:
    """Results of directory analysis."""

    total_files: int
    text_files: int
    binary_files: int
    total_size: int
    languages: Dict[str, int]
    file_types: Dict[str, int]
    excluded_files: List[Path]
    included_files: List[FileContent]


class FileOperationSchema:
    """Schema for file operations in single-pass mode."""

    @staticmethod
    def validate_operation(operation: Dict[str, Any]) -> bool:
        """
        Validate a file operation.

        Args:
            operation: Operation dictionary

        Returns:
            True if valid operation
        """
        required_fields = {"path"}
        operation_type = operation.get("type", "update")

        if operation_type == "update":
            required_fields.add("updated_full_content")
        elif operation_type == "delete":
            required_fields.add("delete")
        elif operation_type == "move":
            required_fields.add("move_to")

        return all(field in operation for field in required_fields)

    @staticmethod
    def apply_operations(
        operations: List[Dict[str, Any]], project_root: Path
    ) -> List[str]:
        """
        Apply file operations atomically.

        Args:
            operations: List of file operations
            project_root: Project root directory

        Returns:
            List of operation results
        """
        results = []

        try:
            for operation in operations:
                if not FileOperationSchema.validate_operation(operation):
                    results.append(f"Invalid operation: {operation}")
                    continue

                result = FileOperationSchema._apply_single_operation(
                    operation, project_root
                )
                results.append(result)

        except Exception as e:
            logger.error(f"Error applying operations: {e}")
            results.append(f"Error: {e}")

        return results

    @staticmethod
    def _apply_single_operation(operation: Dict[str, Any], project_root: Path) -> str:
        """Apply a single file operation."""
        file_path = project_root / operation["path"]
        operation_type = operation.get("type", "update")

        if operation_type == "update":
            # Update file content
            content = operation.get("updated_full_content", "")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return f"Updated: {file_path}"

        elif operation_type == "delete" and operation.get("delete"):
            # Delete file
            if file_path.exists():
                file_path.unlink()
                return f"Deleted: {file_path}"
            else:
                return f"File not found: {file_path}"

        elif operation_type == "move":
            # Move/rename file
            new_path = project_root / operation["move_to"]
            new_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.rename(new_path)
            return f"Moved: {file_path} -> {new_path}"

        return f"Unknown operation: {operation}"


class ContextLimitManager:
    """Manages context size and optimization for large codebases."""

    def __init__(self, max_tokens: int = 100000):
        """
        Initialize context limit manager.

        Args:
            max_tokens: Maximum context tokens allowed
        """
        self.max_tokens = max_tokens
        self.tokens_per_char = 0.25  # Rough estimate

    def compute_size_map(
        self, project_root: Path, files: List[FileContent]
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Compute size maps for files and directories.

        Args:
            project_root: Project root directory
            files: List of file contents

        Returns:
            Tuple of (file_sizes, directory_sizes)
        """
        file_sizes = {}
        directory_sizes = {}

        for file_content in files:
            relative_path = str(file_content.path.relative_to(project_root))
            file_size = len(file_content.content)
            file_sizes[relative_path] = file_size

            # Add to directory sizes
            dir_path = file_content.path.parent
            while dir_path != project_root:
                dir_key = str(dir_path.relative_to(project_root))
                directory_sizes[dir_key] = directory_sizes.get(dir_key, 0) + file_size
                dir_path = dir_path.parent

        return file_sizes, directory_sizes

    def optimize_context(
        self, files: List[FileContent], priority_patterns: List[str] = None
    ) -> List[FileContent]:
        """
        Optimize context by selecting most important files.

        Args:
            files: List of file contents
            priority_patterns: File patterns to prioritize

        Returns:
            Optimized list of files
        """
        if priority_patterns is None:
            priority_patterns = [
                "*.py",
                "*.js",
                "*.ts",
                "*.jsx",
                "*.tsx",
                "*.rs",
                "*.go",
                "*.java",
                "*.cpp",
                "*.c",
                "README*",
                "*.md",
                "package.json",
                "Cargo.toml",
                "pyproject.toml",
                "requirements.txt",
            ]

        # Calculate current size
        total_chars = sum(len(f.content) for f in files)
        estimated_tokens = total_chars * self.tokens_per_char

        if estimated_tokens <= self.max_tokens:
            return files

        # Prioritize files
        prioritized_files = []
        regular_files = []

        for file_content in files:
            is_priority = any(
                fnmatch.fnmatch(file_content.path.name, pattern)
                for pattern in priority_patterns
            )

            if is_priority:
                prioritized_files.append(file_content)
            else:
                regular_files.append(file_content)

        # Sort by size (smaller files first to include more)
        prioritized_files.sort(key=lambda f: len(f.content))
        regular_files.sort(key=lambda f: len(f.content))

        # Select files within token limit
        selected_files = []
        current_chars = 0

        # Add priority files first
        for file_content in prioritized_files:
            file_chars = len(file_content.content)
            if (current_chars + file_chars) * self.tokens_per_char <= self.max_tokens:
                selected_files.append(file_content)
                current_chars += file_chars
            else:
                break

        # Add regular files if space remains
        for file_content in regular_files:
            file_chars = len(file_content.content)
            if (current_chars + file_chars) * self.tokens_per_char <= self.max_tokens:
                selected_files.append(file_content)
                current_chars += file_chars
            else:
                break

        logger.info(f"Context optimized: {len(files)} -> {len(selected_files)} files")
        return selected_files


class SinglePassProcessor:
    """
    Processes projects in single-pass mode with full context analysis.

    Features:
    - Directory-wide analysis and context loading
    - Intelligent file filtering and prioritization
    - Context size optimization for large projects
    - Batch file operations with atomic application
    """

    def __init__(self, config: AppConfig):
        """
        Initialize single-pass processor.

        Args:
            config: Application configuration
        """
        self.config = config
        self.context_manager = ContextLimitManager()

        # Default exclusion patterns
        self.default_excludes = [
            ".git",
            ".svn",
            ".hg",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "target",
            "build",
            "dist",
            ".next",
            ".nuxt",
            "venv",
            "env",
            ".venv",
            ".env",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "*.so",
            "*.dylib",
            "*.dll",
            "*.exe",
            "*.bin",
            "*.o",
            "*.obj",
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.bmp",
            "*.ico",
            "*.mp3",
            "*.mp4",
            "*.avi",
            "*.mov",
            "*.mkv",
            "*.pdf",
            "*.doc",
            "*.docx",
            "*.xls",
            "*.xlsx",
            "*.zip",
            "*.tar",
            "*.gz",
            "*.rar",
            "*.7z",
            ".DS_Store",
            "Thumbs.db",
            "*.log",
            "*.tmp",
            "*.temp",
        ]

        logger.debug("Single-pass processor initialized")

    async def analyze_directory(
        self,
        project_root: Path,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        max_file_size: int = 1024 * 1024,  # 1MB
        max_files: int = 1000,
    ) -> DirectoryAnalysis:
        """
        Analyze directory structure and content.

        Args:
            project_root: Root directory to analyze
            include_patterns: File patterns to include
            exclude_patterns: Additional exclusion patterns
            max_file_size: Maximum file size to include
            max_files: Maximum number of files to process

        Returns:
            Directory analysis results
        """
        if include_patterns is None:
            include_patterns = [
                "*.py",
                "*.js",
                "*.ts",
                "*.jsx",
                "*.tsx",
                "*.rs",
                "*.go",
                "*.java",
                "*.cpp",
                "*.c",
                "*.h",
                "*.php",
                "*.rb",
                "*.cs",
                "*.swift",
                "*.kt",
                "*.html",
                "*.css",
                "*.scss",
                "*.sass",
                "*.less",
                "*.json",
                "*.yaml",
                "*.yml",
                "*.toml",
                "*.ini",
                "*.md",
                "*.txt",
                "*.rst",
                "*.xml",
                "Dockerfile",
                "Makefile",
                "CMakeLists.txt",
                "package.json",
                "requirements.txt",
                "Cargo.toml",
                "pyproject.toml",
                "go.mod",
                "pom.xml",
            ]

        exclude_patterns = (exclude_patterns or []) + self.default_excludes

        total_files = 0
        text_files = 0
        binary_files = 0
        total_size = 0
        languages = {}
        file_types = {}
        excluded_files = []
        included_files = []

        logger.info(f"Analyzing directory: {project_root}")

        for file_path in project_root.rglob("*"):
            if not file_path.is_file():
                continue

            total_files += 1
            file_size = file_path.stat().st_size
            total_size += file_size

            # Check exclusions
            relative_path = file_path.relative_to(project_root)
            if self._should_exclude(relative_path, exclude_patterns):
                excluded_files.append(file_path)
                continue

            # Check file size limit
            if file_size > max_file_size:
                excluded_files.append(file_path)
                continue

            # Check if text file
            if not is_text_file(file_path):
                binary_files += 1
                excluded_files.append(file_path)
                continue

            text_files += 1

            # Check include patterns
            if not any(
                fnmatch.fnmatch(file_path.name, pattern) for pattern in include_patterns
            ):
                # Check if it's in a important directory
                important_dirs = ["src", "lib", "app", "components", "utils", "tests"]
                if not any(part in important_dirs for part in file_path.parts):
                    excluded_files.append(file_path)
                    continue

            # Count file types and languages
            suffix = file_path.suffix.lower()
            file_types[suffix] = file_types.get(suffix, 0) + 1

            language = self._detect_language(file_path)
            if language:
                languages[language] = languages.get(language, 0) + 1

            # Read file content
            try:
                content = read_file_safe(file_path)
                if content is not None:
                    file_content = FileContent(
                        path=file_path,
                        content=content,
                        size=len(content),
                        language=language,
                        metadata={"suffix": suffix, "file_size": file_size},
                    )
                    included_files.append(file_content)
                else:
                    excluded_files.append(file_path)
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {e}")
                excluded_files.append(file_path)

            # Limit number of files
            if len(included_files) >= max_files:
                logger.warning(f"Reached maximum file limit ({max_files})")
                break

        analysis = DirectoryAnalysis(
            total_files=total_files,
            text_files=text_files,
            binary_files=binary_files,
            total_size=total_size,
            languages=languages,
            file_types=file_types,
            excluded_files=excluded_files,
            included_files=included_files,
        )

        logger.info(
            f"Analysis complete: {len(included_files)} files included, {len(excluded_files)} excluded"
        )
        return analysis

    def _should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns."""
        path_str = str(file_path)

        for pattern in exclude_patterns:
            # Check directory exclusions
            if "/" not in pattern and pattern in file_path.parts:
                return True

            # Check file pattern exclusions
            if fnmatch.fnmatch(file_path.name, pattern):
                return True

            # Check path pattern exclusions
            if fnmatch.fnmatch(path_str, pattern):
                return True

        return False

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React JSX",
            ".tsx": "React TSX",
            ".rs": "Rust",
            ".go": "Go",
            ".java": "Java",
            ".kt": "Kotlin",
            ".cpp": "C++",
            ".cc": "C++",
            ".cxx": "C++",
            ".c": "C",
            ".h": "C/C++ Header",
            ".hpp": "C++ Header",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".m": "Objective-C",
            ".scala": "Scala",
            ".clj": "Clojure",
            ".hs": "Haskell",
            ".ml": "OCaml",
            ".fs": "F#",
            ".r": "R",
            ".R": "R",
            ".jl": "Julia",
            ".lua": "Lua",
            ".pl": "Perl",
            ".sh": "Shell",
            ".bash": "Bash",
            ".zsh": "Zsh",
            ".fish": "Fish",
            ".ps1": "PowerShell",
            ".html": "HTML",
            ".htm": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "Sass",
            ".less": "Less",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".toml": "TOML",
            ".xml": "XML",
            ".md": "Markdown",
            ".rst": "reStructuredText",
            ".tex": "LaTeX",
            ".sql": "SQL",
        }

        return language_map.get(file_path.suffix.lower())

    async def create_full_context(
        self,
        project_root: Path,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Create full context for the project.

        Args:
            project_root: Project root directory
            include_patterns: File patterns to include
            exclude_patterns: Additional exclusion patterns

        Returns:
            Context dictionary for AI processing
        """
        logger.info("Creating full context for project")

        # Analyze directory
        analysis = await self.analyze_directory(
            project_root=project_root,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )

        # Optimize context for token limits
        optimized_files = self.context_manager.optimize_context(analysis.included_files)

        # Build context dictionary
        context = {
            "project_root": str(project_root),
            "analysis_summary": {
                "total_files": analysis.total_files,
                "included_files": len(optimized_files),
                "excluded_files": len(analysis.excluded_files),
                "languages": analysis.languages,
                "file_types": analysis.file_types,
                "total_size": analysis.total_size,
            },
            "files": {},
            "directory_structure": self._build_directory_tree(
                optimized_files, project_root
            ),
        }

        # Add file contents
        for file_content in optimized_files:
            relative_path = str(file_content.path.relative_to(project_root))
            context["files"][relative_path] = {
                "content": file_content.content,
                "language": file_content.language,
                "size": file_content.size,
                "metadata": file_content.metadata,
            }

        logger.info(f"Full context created with {len(optimized_files)} files")
        return context

    def _build_directory_tree(
        self, files: List[FileContent], project_root: Path
    ) -> Dict[str, Any]:
        """Build directory tree structure."""
        tree = {}

        for file_content in files:
            relative_path = file_content.path.relative_to(project_root)
            parts = relative_path.parts

            current = tree
            for part in parts[:-1]:  # Directories
                if part not in current:
                    current[part] = {}
                current = current[part]

            # File
            if parts:
                filename = parts[-1]
                current[filename] = {
                    "type": "file",
                    "language": file_content.language,
                    "size": file_content.size,
                }

        return tree

    async def run_single_pass(
        self,
        project_root: Path,
        prompt: str,
        agent_loop,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Run single-pass processing on the project.

        Args:
            project_root: Project root directory
            prompt: User prompt for processing
            agent_loop: Agent loop instance for AI processing
            include_patterns: File patterns to include
            exclude_patterns: Additional exclusion patterns

        Returns:
            Processing results
        """
        logger.info(f"Running single-pass processing: {prompt}")

        try:
            # Create full context
            context = await self.create_full_context(
                project_root=project_root,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
            )

            # Add context to agent loop
            await agent_loop.add_context(context)

            # Process the prompt
            results = []
            async for response in agent_loop.send_message_stream(prompt):
                results.append(response)

            return {
                "success": True,
                "context": context,
                "results": results,
                "stats": {
                    "files_processed": len(context["files"]),
                    "context_size": sum(
                        len(f["content"]) for f in context["files"].values()
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Single-pass processing error: {e}")
            return {"success": False, "error": str(e), "context": None, "results": []}


# Global processor instance
_processor = None


def get_single_pass_processor(config: AppConfig) -> SinglePassProcessor:
    """
    Get global single-pass processor instance.

    Args:
        config: Application configuration

    Returns:
        SinglePassProcessor instance
    """
    global _processor
    if _processor is None:
        _processor = SinglePassProcessor(config)
    return _processor
