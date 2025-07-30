#!/usr/bin/env python3
"""
Kritrima AI CLI - Main entry point for package execution.

This module provides the main entry point when the package is run as:
python -m kritrima_ai
"""

import sys

from kritrima_ai.cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
