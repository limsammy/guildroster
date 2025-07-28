#!/usr/bin/env python3
"""
Version management script for GuildRoster.

This script updates the version across all relevant files in the project.
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Tuple


def get_current_version() -> str:
    """Get current version from app/config.py."""
    config_file = Path("app/config.py")
    if not config_file.exists():
        raise FileNotFoundError("app/config.py not found")

    with open(config_file, "r") as f:
        content = f.read()

    match = re.search(r'VERSION:\s*str\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("VERSION not found in app/config.py")

    return match.group(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch components."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    return tuple(int(part) for part in parts)


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version components into version string."""
    return f"{major}.{minor}.{patch}"


def update_backend_version(version: str) -> None:
    """Update version in app/config.py."""
    config_file = Path("app/config.py")

    with open(config_file, "r") as f:
        content = f.read()

    # Update VERSION line
    content = re.sub(
        r'(VERSION:\s*str\s*=\s*)"[^"]+"', rf'\1"{version}"', content
    )

    with open(config_file, "w") as f:
        f.write(content)

    print(f"✓ Updated backend version to {version}")


def update_frontend_version(version: str) -> None:
    """Update version in frontend/package.json."""
    package_file = Path("frontend/package.json")

    with open(package_file, "r") as f:
        content = f.read()

    # Update version field
    content = re.sub(r'("version":\s*)"[^"]+"', rf'\1"{version}"', content)

    with open(package_file, "w") as f:
        f.write(content)

    print(f"✓ Updated frontend version to {version}")


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)."""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return format_version(major, minor, patch)


def validate_version(version: str) -> None:
    """Validate version format."""
    try:
        parse_version(version)
    except ValueError as e:
        raise ValueError(f"Invalid version format: {version}") from e


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_version.py <command> [version]")
        print("Commands:")
        print("  patch                    - Bump patch version (0.1.0 → 0.1.1)")
        print("  minor                    - Bump minor version (0.1.0 → 0.2.0)")
        print("  major                    - Bump major version (0.1.0 → 1.0.0)")
        print("  set <version>            - Set specific version")
        print("  show                     - Show current version")
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "show":
            current_version = get_current_version()
            print(f"Current version: {current_version}")
            return

        if command == "set":
            if len(sys.argv) < 3:
                print("Error: Version required for 'set' command")
                sys.exit(1)
            new_version = sys.argv[2]
            validate_version(new_version)
        elif command in ["major", "minor", "patch"]:
            current_version = get_current_version()
            new_version = bump_version(current_version, command)
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)

        print(f"Updating version to {new_version}...")

        # Update versions in files
        update_backend_version(new_version)
        update_frontend_version(new_version)

        print(f"\n✓ Version updated to {new_version}")
        print("\nNext steps:")
        print("1. Review the changes")
        print("2. Commit the version bump:")
        print(
            f"   git add . && git commit -m 'chore: bump version to {new_version}'"
        )
        print("3. Tag the release:")
        print(f"   git tag v{new_version}")
        print("4. Push changes and tags:")
        print("   git push && git push --tags")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
