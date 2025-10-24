"""
Version management utilities for SC Profile Viewer
"""

import os
import re
from typing import Tuple


def get_version_file_path() -> str:
    """Get the path to the VERSION.TXT file"""
    # Try to find VERSION.TXT in the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    version_file = os.path.join(project_root, 'VERSION.TXT')

    # If running from PyInstaller bundle, check the bundled path
    if not os.path.exists(version_file):
        import sys
        if hasattr(sys, '_MEIPASS'):
            version_file = os.path.join(sys._MEIPASS, 'VERSION.TXT')

    return version_file


def get_version() -> str:
    """
    Get the current version from VERSION.TXT

    Returns:
        Version string (e.g., "0.1.0")
    """
    version_file = get_version_file_path()

    try:
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                return version
        else:
            return "0.0.0"  # Default version if file not found
    except Exception:
        return "0.0.0"


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse a version string into (major, minor, patch) tuple

    Args:
        version_str: Version string like "0.1.0"

    Returns:
        Tuple of (major, minor, patch) integers
    """
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return (0, 0, 0)


def increment_version(current_version: str, increment_type: str = 'patch') -> str:
    """
    Increment the version number

    Args:
        current_version: Current version string (e.g., "0.1.0")
        increment_type: Type of increment ('major', 'minor', or 'patch')

    Returns:
        New version string
    """
    major, minor, patch = parse_version(current_version)

    if increment_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif increment_type == 'minor':
        minor += 1
        patch = 0
    elif increment_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid increment type: {increment_type}. Use 'major', 'minor', or 'patch'")

    return f"{major}.{minor}.{patch}"


def set_version(new_version: str) -> None:
    """
    Set a new version in VERSION.TXT

    Args:
        new_version: New version string to write
    """
    version_file = get_version_file_path()

    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        raise ValueError(f"Invalid version format: {new_version}. Use semantic versioning (e.g., 0.1.0)")

    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(new_version)

    print(f"Version updated to: {new_version}")


if __name__ == '__main__':
    # Test version utilities
    print(f"Current version: {get_version()}")
    print(f"Version file path: {get_version_file_path()}")
