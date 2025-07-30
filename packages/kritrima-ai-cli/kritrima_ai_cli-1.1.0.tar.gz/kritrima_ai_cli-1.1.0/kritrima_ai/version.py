"""
Version information for Kritrima AI CLI.

This module provides dynamic version loading from package metadata,
ensuring consistency across the application.
"""

import importlib.metadata

__version__ = "1.1.0"
__author__ = "Kritrima AI"
__email__ = "contact@kritrima.ai"
__license__ = "MIT"
__description__ = "Comprehensive AI-powered CLI assistant with autonomous agent capabilities"

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_BUILD = None

# Build version tuple
VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
if VERSION_BUILD is not None:
    VERSION_INFO += (VERSION_BUILD,)

def get_version():
    """Get the version string."""
    return __version__

def get_version_info():
    """
    Get detailed version information.

    Returns:
        Dictionary with version details
    """
    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": __description__,
        "version_info": VERSION_INFO,
        "package": "kritrima-ai",
        "build": "python",
        "platform": "cross-platform",
    }

# Primary version export
CLI_VERSION = __version__
