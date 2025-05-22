#!/usr/bin/env python3
"""
TrainLoop Evals - Docker Build Script

This script builds Docker images for the TrainLoop Evals UI application
with proper versioning and tagging.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


# Color output helpers
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def log_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def log_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def log_warn(message):
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")


def log_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    sys.exit(1)


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
            log_error(f"Command failed with exit code {return_code}")
        return None


def main():
    # Configuration
    script_dir = Path(__file__).resolve().parents[1]
    project_root = script_dir.parent
    version_file = project_root / "VERSION"
    image_name = os.environ.get("IMAGE_NAME", "evals")
    pulumi_config_path = project_root / "infra" / "Pulumi.trainloop.yaml"
    dockerfile_path = project_root / "ui" / "Dockerfile"

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Build Docker images for TrainLoop Evals"
    )
    parser.add_argument(
        "--push", action="store_true", help="Push to container registry"
    )
    parser.add_argument(
        "--update-pulumi",
        action="store_true",
        help="Update Pulumi config with new image tag",
    )
    parser.add_argument(
        "--env", default="dev", help="Environment (dev/prod), default: dev"
    )
    parser.add_argument(
        "--registry",
        help="Container registry to use, can also be set with REGISTRY environment variable",
    )
    args = parser.parse_args()

    # Check if VERSION file exists
    if not version_file.exists():
        log_warn(
            f"VERSION file not found at {version_file}, using package.json version"
        )
        package_json_path = project_root / "package.json"
        if not package_json_path.exists():
            log_error("Neither VERSION file nor package.json found")

        try:
            import json

            with open(package_json_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)
            version = package_data.get("version")
            if not version:
                log_error("No version found in package.json")
        except Exception as e:
            log_error(f"Error reading package.json: {e}")
    else:
        with open(version_file, "r", encoding="utf-8") as f:
            version = f.read().strip()

    # Check if we're in a git repository
    try:
        git_commit_hash = run_command(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True
        )
        git_branch = (
            run_command(
                ["git", "symbolic-ref", "--short", "HEAD"],
                capture_output=True,
                check=False,
            )
            or "detached"
        )
    except subprocess.CalledProcessError:
        log_warn("Not in a git repository, using only semantic version for tagging")
        git_commit_hash = "nogit"
        git_branch = "nogit"

    # Generate version tag based on semantic version and git info
    version_tag = f"{version}-{git_commit_hash}"

    # Default registry if not provided
    default_registry = "ghcr.io/trainloop"
    registry = args.registry or os.environ.get("REGISTRY", default_registry)

    # Full image name with various tags
    semver_image_name = f"{registry}/{image_name}:{version}"
    full_image_name = f"{registry}/{image_name}:{version_tag}"
    latest_image_name = f"{registry}/{image_name}:latest"
    channel_image_name = f"{registry}/{image_name}:{git_branch}"

    # Build the Docker image
    log_info(f"Building Docker image: {full_image_name}")
    log_info(f"Environment: {args.env}")
    log_info(f"Version: {version} ({version_tag})")
    log_info(f"Registry: {registry}")

    # Set build args based on environment
    build_args = ["--build-arg", f"VERSION={version}", "--platform=linux/amd64"]

    if args.env == "prod":
        build_args.extend(["--build-arg", "NODE_ENV=production"])

    # Log the platform information
    log_info("Building for platform: linux/amd64")

    # Build the Docker image with multiple tags
    docker_build_cmd = [
        "docker",
        "build",
        *build_args,
        "-t",
        full_image_name,
        "-t",
        semver_image_name,
        "-t",
        latest_image_name,
        "-t",
        channel_image_name,
        "-f",
        str(dockerfile_path),
        str(project_root / "ui"),
    ]

    run_command(docker_build_cmd)

    # Push if requested
    if args.push:
        if not registry:
            log_error(
                "Cannot push without a registry. Set REGISTRY environment variable."
            )

        log_info("Pushing Docker image to registry with all tags")

        for image in [
            full_image_name,
            semver_image_name,
            latest_image_name,
            channel_image_name,
        ]:
            run_command(["docker", "push", image])

        log_success("Images pushed successfully to registry")
        log_success(f"  - {full_image_name} (specific version+commit)")
        log_success(f"  - {semver_image_name} (semantic version only)")
        log_success(f"  - {latest_image_name} (latest)")
        log_success(f"  - {channel_image_name} (branch/channel)")

    # Update Pulumi config if requested
    if args.update_pulumi:
        if not pulumi_config_path.exists():
            log_error(f"Pulumi config not found at: {pulumi_config_path}")

        log_info("Updating Pulumi config with new image tag")

        # Extract image name without the tag (everything before the colon)
        image_without_tag = f"{registry}/{image_name}"

        # Read the Pulumi config file
        with open(pulumi_config_path, "r") as f:
            config_lines = f.readlines()

        # Update the relevant lines
        for i, line in enumerate(config_lines):
            if line.strip().startswith("appImage:"):
                config_lines[i] = f"  appImage: {image_without_tag}\n"
            elif line.strip().startswith("appVersion:"):
                config_lines[i] = f"  appVersion: {version}\n"

        # Write the updated config back
        with open(pulumi_config_path, "w") as f:
            f.writelines(config_lines)

        log_success("Updated Pulumi config with:")
        log_success(f"  - Image: {full_image_name}")
        log_success(f"  - Version: {version}")

    log_success("Build completed successfully!")
    log_info("Image tags created:")
    log_info(f"  - {full_image_name} (specific version+commit)")
    log_info(f"  - {semver_image_name} (semantic version only)")
    log_info(f"  - {latest_image_name} (latest)")
    log_info(f"  - {channel_image_name} (branch/channel)")
    log_info(
        f"Run with: open http://localhost:3000 && docker run -p 3000:3000 --rm {full_image_name}"
    )


if __name__ == "__main__":
    main()
