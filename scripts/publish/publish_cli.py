#!/usr/bin/env python3
"""
TrainLoop Evals - CLI Publishing Script

This script publishes the TrainLoop CLI to PyPI.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path


def run_command(
    cmd, cwd=None, env=None, check=True, capture_output=False, interactive=False
):
    """Run a command with appropriate handling of output and input.

    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory
        env: Environment variables
        check: Whether to check the return code
        capture_output: Whether to capture and return output
        interactive: Whether to allow interactive input from the user
    """
    print(f"Running: {' '.join(cmd)}")

    if interactive:
        # For truly interactive commands, pass stdin/stdout/stderr directly
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            check=check,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        return None  # No output to return as it went directly to terminal
    elif capture_output:
        # For non-interactive commands where we need to capture output
        result = subprocess.run(
            cmd, cwd=cwd, env=env, check=check, capture_output=True, text=True
        )
        return result.stdout.strip()
    else:
        # For non-interactive commands where we want to show output
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffered
        )

        # Print output in real-time
        for line in process.stdout:
            print(line, end="")

        # Wait for the process to complete
        return_code = process.wait()
        if check and return_code != 0:
            print(f"Error: Command failed with exit code {return_code}")
            sys.exit(return_code)
        return None


def check_command(cmd):
    """Check if a command is available."""
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def main():
    # Get script directory and locate CLI directory
    script_dir = Path(__file__).resolve().parents[1]
    cli_dir = script_dir.parent / "cli"

    # Check if CLI directory exists
    if not cli_dir.is_dir():
        print(f"ERROR: cli/ directory not found at {cli_dir}")
        sys.exit(1)

    # Change to CLI directory
    os.chdir(cli_dir)
    print(f"📦 Publishing from {cli_dir}")

    # Ensure Poetry is installed
    if not check_command(["poetry", "--version"]):
        print("ERROR: poetry not found. Install it from https://python-poetry.org/")
        sys.exit(1)

    # Clean previous builds
    print("🧹 Cleaning old artifacts...")
    for item in ["dist", "build"]:
        path = cli_dir / item
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # Remove egg-info directories
    for item in cli_dir.glob("*.egg-info"):
        if item.is_dir():
            shutil.rmtree(item)

    # Publish to PyPI (includes build step)
    print("🚀 Publishing to PyPI...")
    run_command(
        ["poetry", "publish", "--build", "--skip-existing"],
        cwd=cli_dir,
        interactive=False,
    )

    # Get the version
    version = run_command(["poetry", "version", "-s"], cwd=cli_dir, capture_output=True)
    print(f"✅ Successfully published trainloop-cli v{version}")


if __name__ == "__main__":
    main()
