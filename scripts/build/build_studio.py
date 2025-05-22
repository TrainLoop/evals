#!/usr/bin/env python3
"""
TrainLoop Evals - Studio Build Script

This script builds the TrainLoop Studio package for distribution.
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


def rsync(src, dest):
    """
    Emulate rsync -a using Python's shutil
    """
    print(f"Copying {src} to {dest}")
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest), exist_ok=True)

    if os.path.isdir(src):
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dest)


def main():
    # Get script directory and project root
    script_dir = Path(__file__).resolve().parents[1]
    project_root = script_dir.parent

    # Check VERSION file
    version_file = project_root / "VERSION"
    if not version_file.exists():
        print("Error: VERSION file not found")
        sys.exit(1)

    # Read version
    with open(version_file, "r", encoding="utf-8") as f:
        version = f.read().strip()

    # Build UI
    ui_dir = project_root / "ui"
    runner_dir = project_root / "runner"
    bundle_dir = runner_dir / "_bundle"

    # Build the UI
    print(f"Building UI in {ui_dir}")
    run_command(["npm", "install", "--omit=dev"], cwd=ui_dir)
    run_command(["npm", "run", "build"], cwd=ui_dir)

    # Clean existing bundle directory
    if bundle_dir.exists():
        print(f"Removing existing bundle directory: {bundle_dir}")
        shutil.rmtree(bundle_dir)

    # Create bundle directories
    bundle_dir.mkdir(parents=True, exist_ok=True)
    next_static_dir = bundle_dir / ".next" / "static"
    next_static_dir.mkdir(parents=True, exist_ok=True)
    legacy_static_dir = bundle_dir / "static"
    legacy_static_dir.mkdir(parents=True, exist_ok=True)

    # Copy the standalone bundle
    standalone_dir = ui_dir / ".next" / "standalone"
    static_dir = ui_dir / ".next" / "static"

    print("Copying standalone bundle")
    rsync(standalone_dir, bundle_dir)

    # Copy static files to both locations
    print("Copying static files to .next/static")
    rsync(static_dir, bundle_dir / ".next" / "static")

    print("Copying static files to static (for backward compatibility)")
    rsync(static_dir, bundle_dir / "static")

    # Copy public directory if it exists
    public_dir = ui_dir / "public"
    if public_dir.exists():
        print("Copying public directory")
        rsync(public_dir, bundle_dir / "public")

    # Create dist directory
    dist_dir = project_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Clean dist directory
    for item in dist_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    # Create package (version already set by bump_version.py)
    print(f"Creating npm package with version {version}")
    run_command(["npm", "pack", "--pack-destination", f"{dist_dir}"], cwd=runner_dir)

    package_file = dist_dir / f"trainloop-studio-runner-{version}.tgz"
    if package_file.exists():
        print(f"✅ Successfully built package: {package_file}")
    else:
        print(f"Error: Package file not found at {package_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
