#!/usr/bin/env python3
"""
Lint script for HF MCP Server Python code.

Usage:
    python scripts/lint.py [--fix]

This script runs ruff for linting and formatting checks on Python code
in the packages/e2e-python directory.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run linting checks on Python code."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    python_dir = project_root / "packages" / "e2e-python"

    if not python_dir.exists():
        print(f"Error: Python directory not found: {python_dir}")
        sys.exit(1)

    # Check if --fix flag is passed
    fix_mode = "--fix" in sys.argv

    # Build ruff command
    ruff_check_cmd = ["ruff", "check", str(python_dir)]
    ruff_format_cmd = ["ruff", "format", "--check", str(python_dir)]

    if fix_mode:
        ruff_check_cmd.append("--fix")
        ruff_format_cmd = ["ruff", "format", str(python_dir)]

    exit_code = 0

    # Run ruff check
    print("Running ruff check...")
    result = subprocess.run(ruff_check_cmd, cwd=project_root)
    if result.returncode != 0:
        exit_code = 1

    # Run ruff format check
    print("\nRunning ruff format check...")
    result = subprocess.run(ruff_format_cmd, cwd=project_root)
    if result.returncode != 0:
        exit_code = 1

    if exit_code == 0:
        print("\nAll linting checks passed!")
    else:
        print("\nLinting checks failed.")
        if not fix_mode:
            print("Run 'python scripts/lint.py --fix' to automatically fix issues.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
