#!/usr/bin/env python3
"""
Setup script for Kritrima AI CLI.

This provides basic setup capabilities beyond pyproject.toml.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Minimum Python version
MIN_PYTHON = (3, 8)

# Check Python version
if sys.version_info < MIN_PYTHON:
    sys.exit(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.")

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()


def get_long_description():
    """Get long description from README."""
    readme_path = PROJECT_ROOT / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "Kritrima AI CLI - Advanced AI-powered command-line assistant"


def get_version():
    """Get version from kritrima_ai/__init__.py."""
    init_file = PROJECT_ROOT / "kritrima_ai" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        for line in content.split("\n"):
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"


if __name__ == "__main__":
    setup(
        name="kritrima-ai-cli",
        version=get_version(),
        description="Advanced AI-powered command-line assistant with autonomous agent capabilities",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        author="Kritrima AI Team",
        author_email="contact@kritrima.ai",
        url="https://github.com/kritrima/kritrima-ai-cli",
        project_urls={
            "Documentation": "https://docs.kritrima.ai",
            "Source": "https://github.com/kritrima/kritrima-ai-cli",
            "Tracker": "https://github.com/kritrima/kritrima-ai-cli/issues",
        },
        packages=find_packages(),
        python_requires=f">={MIN_PYTHON[0]}.{MIN_PYTHON[1]}",
        entry_points={
            "console_scripts": [
                "kritrima-ai=kritrima_ai.cli:main",
                "kai=kritrima_ai.cli:main",
            ],
        },
        include_package_data=True,
        zip_safe=False,
        platforms="any",
    ) 