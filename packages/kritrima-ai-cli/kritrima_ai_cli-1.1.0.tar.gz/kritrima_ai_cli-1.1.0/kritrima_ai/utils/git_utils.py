"""
Git integration utilities for Kritrima AI CLI.

This module provides Git repository detection, status checking, and integration
capabilities for better context awareness and change tracking.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class GitStatus(NamedTuple):
    """Git repository status information."""

    is_repo: bool
    branch: Optional[str]
    has_changes: bool
    untracked_files: List[str]
    modified_files: List[str]
    staged_files: List[str]
    commit_hash: Optional[str]
    remote_url: Optional[str]


def check_in_git(working_dir: Optional[str] = None) -> bool:
    """
    Check if the current directory is inside a Git repository.

    Args:
        working_dir: Directory to check (defaults to current directory)

    Returns:
        True if inside a Git repository, False otherwise.
    """
    if working_dir:
        original_dir = os.getcwd()
        os.chdir(working_dir)

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        is_git_repo = result.returncode == 0 and result.stdout.strip() == "true"

        if is_git_repo:
            logger.debug(f"Git repository detected in {working_dir or os.getcwd()}")

        return is_git_repo

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        logger.debug(f"Git check failed: {e}")
        return False

    finally:
        if working_dir:
            os.chdir(original_dir)


def get_git_status(working_dir: Optional[str] = None) -> GitStatus:
    """
    Get comprehensive Git repository status.

    Args:
        working_dir: Directory to check (defaults to current directory)

    Returns:
        GitStatus object with repository information.
    """
    if working_dir:
        original_dir = os.getcwd()
        os.chdir(working_dir)

    try:
        # Check if we're in a Git repository
        if not check_in_git():
            return GitStatus(
                is_repo=False,
                branch=None,
                has_changes=False,
                untracked_files=[],
                modified_files=[],
                staged_files=[],
                commit_hash=None,
                remote_url=None,
            )

        # Get branch name
        branch = _get_git_branch()

        # Get commit hash
        commit_hash = _get_git_commit_hash()

        # Get remote URL
        remote_url = _get_git_remote_url()

        # Get file status
        untracked_files, modified_files, staged_files = _get_git_file_status()

        has_changes = bool(untracked_files or modified_files or staged_files)

        return GitStatus(
            is_repo=True,
            branch=branch,
            has_changes=has_changes,
            untracked_files=untracked_files,
            modified_files=modified_files,
            staged_files=staged_files,
            commit_hash=commit_hash,
            remote_url=remote_url,
        )

    except Exception as e:
        logger.warning(f"Failed to get Git status: {e}")
        return GitStatus(
            is_repo=False,
            branch=None,
            has_changes=False,
            untracked_files=[],
            modified_files=[],
            staged_files=[],
            commit_hash=None,
            remote_url=None,
        )

    finally:
        if working_dir:
            os.chdir(original_dir)


def get_git_diff(
    working_dir: Optional[str] = None,
    staged: bool = False,
    file_path: Optional[str] = None,
) -> str:
    """
    Generate Git diff for current changes.

    Args:
        working_dir: Directory to check (defaults to current directory)
        staged: Get staged changes instead of working directory changes
        file_path: Specific file to diff (optional)

    Returns:
        Git diff output as string.
    """
    if working_dir:
        original_dir = os.getcwd()
        os.chdir(working_dir)

    try:
        cmd = ["git", "diff"]

        if staged:
            cmd.append("--staged")

        if file_path:
            cmd.append(file_path)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return result.stdout
        else:
            logger.warning(f"Git diff failed: {result.stderr}")
            return ""

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        logger.warning(f"Git diff failed: {e}")
        return ""

    finally:
        if working_dir:
            os.chdir(original_dir)


def get_git_log(
    working_dir: Optional[str] = None, max_count: int = 10, oneline: bool = True
) -> List[str]:
    """
    Get Git commit history.

    Args:
        working_dir: Directory to check (defaults to current directory)
        max_count: Maximum number of commits to retrieve
        oneline: Use oneline format

    Returns:
        List of commit messages/info.
    """
    if working_dir:
        original_dir = os.getcwd()
        os.chdir(working_dir)

    try:
        cmd = ["git", "log", f"--max-count={max_count}"]

        if oneline:
            cmd.append("--oneline")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        else:
            logger.warning(f"Git log failed: {result.stderr}")
            return []

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        logger.warning(f"Git log failed: {e}")
        return []

    finally:
        if working_dir:
            os.chdir(original_dir)


def is_file_tracked(file_path: str, working_dir: Optional[str] = None) -> bool:
    """
    Check if a file is tracked by Git.

    Args:
        file_path: Path to the file to check
        working_dir: Directory to check (defaults to current directory)

    Returns:
        True if file is tracked, False otherwise.
    """
    if working_dir:
        original_dir = os.getcwd()
        os.chdir(working_dir)

    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", file_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        return result.returncode == 0

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        logger.debug(f"Git ls-files failed: {e}")
        return False

    finally:
        if working_dir:
            os.chdir(original_dir)


def get_git_root(working_dir: Optional[str] = None) -> Optional[Path]:
    """
    Get the root directory of the Git repository.

    Args:
        working_dir: Directory to check (defaults to current directory)

    Returns:
        Path to Git repository root, or None if not in a repository.
    """
    if working_dir:
        original_dir = os.getcwd()
        os.chdir(working_dir)

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return Path(result.stdout.strip())
        else:
            return None

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        logger.debug(f"Git root detection failed: {e}")
        return None

    finally:
        if working_dir:
            os.chdir(original_dir)


def _get_git_branch() -> Optional[str]:
    """Get current Git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None

    except Exception as e:
        logger.debug(f"Git branch detection failed: {e}")
        return None


def _get_git_commit_hash() -> Optional[str]:
    """Get current Git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None

    except Exception as e:
        logger.debug(f"Git commit hash detection failed: {e}")
        return None


def _get_git_remote_url() -> Optional[str]:
    """Get Git remote URL."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None

    except Exception as e:
        logger.debug(f"Git remote URL detection failed: {e}")
        return None


def _get_git_file_status() -> Tuple[List[str], List[str], List[str]]:
    """Get Git file status (untracked, modified, staged)."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            return [], [], []

        untracked_files = []
        modified_files = []
        staged_files = []

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            status = line[:2]
            filename = line[3:]

            # Check staged status (first character)
            if status[0] in "MADRC":
                staged_files.append(filename)

            # Check working directory status (second character)
            if status[1] == "M":
                modified_files.append(filename)
            elif status[1] == "?":
                untracked_files.append(filename)

        return untracked_files, modified_files, staged_files

    except Exception as e:
        logger.debug(f"Git status parsing failed: {e}")
        return [], [], []


def create_git_context() -> Dict[str, str]:
    """
    Create a context dictionary with Git repository information.

    Returns:
        Dictionary with Git context information for AI prompts.
    """
    git_status = get_git_status()

    if not git_status.is_repo:
        return {"git_status": "Not in a Git repository"}

    context = {
        "git_status": "In Git repository",
        "branch": git_status.branch or "unknown",
    }

    if git_status.commit_hash:
        context["commit"] = git_status.commit_hash[:8]

    if git_status.remote_url:
        context["remote"] = git_status.remote_url

    if git_status.has_changes:
        changes = []
        if git_status.staged_files:
            changes.append(f"{len(git_status.staged_files)} staged")
        if git_status.modified_files:
            changes.append(f"{len(git_status.modified_files)} modified")
        if git_status.untracked_files:
            changes.append(f"{len(git_status.untracked_files)} untracked")

        context["changes"] = ", ".join(changes)
    else:
        context["changes"] = "No changes"

    return context


def validate_git_installation() -> bool:
    """
    Validate that Git is installed and accessible.

    Returns:
        True if Git is available, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, timeout=5
        )

        if result.returncode == 0:
            logger.debug(f"Git version: {result.stdout.strip()}")
            return True
        else:
            return False

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        logger.warning(f"Git not available: {e}")
        return False


def get_git_files(working_dir: Optional[str] = None) -> List[str]:
    """
    Get list of files tracked by Git.

    Args:
        working_dir: Directory to check (defaults to current directory)

    Returns:
        List of file paths relative to repository root.
    """
    if working_dir:
        original_dir = os.getcwd()
        os.chdir(working_dir)

    try:
        if not check_in_git():
            return []

        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            logger.debug(f"Found {len(files)} tracked files in git repository")
            return files
        else:
            logger.warning(f"Git ls-files failed: {result.stderr}")
            return []

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        logger.warning(f"Git ls-files failed: {e}")
        return []

    finally:
        if working_dir:
            os.chdir(original_dir)
