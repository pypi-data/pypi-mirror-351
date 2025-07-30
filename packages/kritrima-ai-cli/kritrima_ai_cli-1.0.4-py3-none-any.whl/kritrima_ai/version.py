"""
Version information for Kritrima AI CLI.

This module provides dynamic version loading from package metadata,
ensuring consistency across the application.
"""

import importlib.metadata


def get_version() -> str:
    """
    Get the current version of Kritrima AI CLI.

    Returns:
        Version string from package metadata
    """
    try:
        return importlib.metadata.version("kritrima-ai")
    except importlib.metadata.PackageNotFoundError:
        # Fallback for development
        return "0.1.0-dev"


# Primary version export
__version__ = get_version()
CLI_VERSION = __version__


def get_version_info() -> dict:
    """
    Get detailed version information.

    Returns:
        Dictionary with version details
    """
    return {
        "version": __version__,
        "package": "kritrima-ai",
        "build": "python",
        "platform": "cross-platform",
    }
