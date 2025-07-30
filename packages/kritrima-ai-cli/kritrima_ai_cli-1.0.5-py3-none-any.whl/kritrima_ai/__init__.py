"""
Kritrima AI CLI - Comprehensive AI-powered CLI assistant.

A sophisticated, multi-layered AI assistant with autonomous agent capabilities,
built with Python 3.8+.
"""

__version__ = "1.0.5"
__author__ = "Kritrima AI"
__email__ = "contact@kritrima.ai"
__license__ = "MIT"

# Version compatibility check
import sys

if sys.version_info < (3, 8):
    raise RuntimeError(
        f"Kritrima AI CLI requires Python 3.8 or later. "
        f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
    )

# Import main components for easy access
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.config.providers import get_provider_info, list_providers

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "AppConfig",
    "get_provider_info",
    "list_providers",
]
