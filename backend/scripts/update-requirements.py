#!/usr/bin/env python3
"""
Update requirements files for the project.
This script updates both requirements-dev.txt and requirements-prod.txt
with the latest compatible versions of packages.

Usage:
    ./update_requirements.py

The script will:
1. Create a temporary virtual environment
2. Install existing requirements
3. Update all packages to their latest compatible versions
4. Generate new requirements files
"""

import os
import subprocess
import sys
import venv
from pathlib import Path
from tempfile import TemporaryDirectory


def create_venv(venv_path):
    """Create a virtual environment."""
    print(f"Creating virtual environment at {venv_path}...")
    venv.create(venv_path, with_pip=True)


def get_venv_python(venv_path):
    """Get the python executable path for the virtual environment."""
    if sys.platform == "win32":
        return os.path.join(venv_path, "Scripts", "python.exe")
    return os.path.join(venv_path, "bin", "python")


def get_package_versions(requirements_file):
    """Parse requirements file and return dict of package versions."""
    versions = {}
    with open(requirements_file) as f:
        for line in f:
            if "==" in line:
                package, version = line.strip().split("==")
                versions[package] = version
    return versions


def check_major_version_updates(venv_python, current_versions):
    """Check for available major version updates."""
    major_updates = []

    for package, current_version in current_versions.items():
        # Get latest version information
        result = subprocess.run(
            [venv_python, "-m", "pip", "index", "versions", package],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            latest_version = result.stdout.split("\n")[0].split()[-1]
            current_major = current_version.split(".")[0]
            latest_major = latest_version.split(".")[0]

            if current_major != latest_major:
                major_updates.append((package, current_version, latest_version))

    return major_updates


def update_requirements(
    venv_python, requirements_file, output_file, force_latest=False
):
    """Update requirements to their latest versions."""
    print(f"\nProcessing {requirements_file}...")

    # Get base package names without version constraints
    base_packages = []
    with open(requirements_file) as f:
        for line in f:
            if "==" in line:
                package = line.split("==")[0].strip()
                base_packages.append(package)

    if force_latest:
        # Install latest version of each package
        for package in base_packages:
            print(f"Updating {package} to latest version...")
            subprocess.run(
                [venv_python, "-m", "pip", "install", "--upgrade", package], check=True
            )

        # Generate new requirements file with _latest suffix
        latest_output = (
            output_file.parent / f"{output_file.stem}_latest{output_file.suffix}"
        )
        with open(latest_output, "w") as f:
            subprocess.run([venv_python, "-m", "pip", "freeze"], stdout=f, check=True)
        print(f"Latest versions written to {latest_output}")
    else:
        # Original update behavior
        current_versions = get_package_versions(requirements_file)
        subprocess.run(
            [venv_python, "-m", "pip", "install", "-r", requirements_file], check=True
        )
        major_updates = check_major_version_updates(venv_python, current_versions)

        if major_updates:
            print("\nMajor version updates available:")
            for package, current, latest in major_updates:
                print(f"  • {package}: {current} -> {latest}")
            print("\nConsider testing these updates carefully!")

        subprocess.run(
            [venv_python, "-m", "pip", "install", "--upgrade", "-r", requirements_file],
            check=True,
        )
        with open(output_file, "w") as f:
            subprocess.run([venv_python, "-m", "pip", "freeze"], stdout=f, check=True)
        print(f"Updated requirements written to {output_file}")


def main():
    # Get project root directory (assuming script is in backend/scripts)
    project_root = Path(__file__).resolve().parent.parent.parent

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Update Python requirements files.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Update all packages to their latest versions",
    )
    args = parser.parse_args()

    # Define requirements files
    dev_requirements = project_root / "requirements-dev.txt"
    prod_requirements = project_root / "requirements-prod.txt"

    if not dev_requirements.exists() or not prod_requirements.exists():
        print("Error: Could not find requirements files!")
        sys.exit(1)

    with TemporaryDirectory() as temp_dir:
        print("Starting requirements update process...")

        # Create and activate virtual environment
        create_venv(temp_dir)
        venv_python = get_venv_python(temp_dir)

        # Update development requirements
        update_requirements(
            venv_python, dev_requirements, dev_requirements, args.latest
        )

        # Update production requirements
        update_requirements(
            venv_python, prod_requirements, prod_requirements, args.latest
        )

        print("\nRequirements update completed successfully!")
        if args.latest:
            print("\nLatest versions have been written to *_latest.txt files.")
            print("To test these versions:")
            print("1. Review the changes in the _latest files")
            print("2. Test in a new branch before applying")
            print("3. Run your test suite")
        print("\nPlease review the changes before committing.")


if __name__ == "__main__":
    main()
