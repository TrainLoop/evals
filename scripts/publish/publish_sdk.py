#!/usr/bin/env python3
"""
TrainLoop Evals - SDK Publishing Script
--------------------------------------------------------------------------
This script publishes the TrainLoop Evals SDK packages to PyPI and npm.
It handles both the Python and TypeScript SDKs.
--------------------------------------------------------------------------
"""

import os
import sys
import subprocess
import shutil
import json
import argparse
from pathlib import Path
import re


# ANSI color codes for terminal output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def log_info(message):
    """Log an informational message"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def log_success(message):
    """Log a success message"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def log_warn(message):
    """Log a warning message"""
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")


def log_error(message):
    """Log an error message and exit"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    sys.exit(1)


class SdkPublisher:
    def __init__(self):
        # Set up paths
        self.script_dir = Path(__file__).resolve().parents[1]
        self.project_root = self.script_dir.parent
        self.sdk_dir = self.project_root / "sdk"
        self.python_sdk_dir = self.sdk_dir / "python"
        self.ts_sdk_dir = self.sdk_dir / "typescript"
        self.version_file = self.project_root / "VERSION"

    def get_version(self):
        """Get the current version from the VERSION file"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        else:
            log_error(f"VERSION file not found at {self.version_file}")
            return None

    def check_versions(self):
        """Check if versions match across packages"""
        root_version = self.get_version()

        # Check Python SDK version
        py_project_file = self.python_sdk_dir / "pyproject.toml"
        if py_project_file.exists():
            content = py_project_file.read_text()
            py_version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if py_version_match:
                py_version = py_version_match.group(1)
                if py_version != root_version:
                    log_warn(
                        f"Python SDK version ({py_version}) doesn't match root version ({root_version})"
                    )
                    log_warn(
                        "Consider running ./scripts/version.sh to synchronize versions"
                    )

        # Check TypeScript SDK version
        ts_package_file = self.ts_sdk_dir / "package.json"
        if ts_package_file.exists():
            with open(ts_package_file, encoding="utf-8") as f:
                package_json = json.load(f)
                ts_version = package_json.get("version")
                if ts_version != root_version:
                    log_warn(
                        f"TypeScript SDK version ({ts_version}) doesn't match root version ({root_version})"
                    )
                    log_warn(
                        "Consider running ./scripts/version.sh to synchronize versions"
                    )

    def publish_python_sdk(self):
        """Publish Python SDK to PyPI"""
        log_info("Publishing Python SDK to PyPI...")

        if not self.python_sdk_dir.exists():
            log_error(f"Python SDK directory not found at {self.python_sdk_dir}")

        # Change to the Python SDK directory
        os.chdir(self.python_sdk_dir)

        # Ensure Poetry is installed
        if shutil.which("poetry") is None:
            log_error("Poetry not found. Install it from https://python-poetry.org/")

        # Clean previous builds
        log_info("Cleaning old artifacts...")
        for path in ["dist/", "build/", "*.egg-info/"]:
            artifacts = list(Path().glob(path))
            for artifact in artifacts:
                if artifact.is_dir():
                    shutil.rmtree(artifact, ignore_errors=True)
                else:
                    artifact.unlink(missing_ok=True)

        # Publish to PyPI (includes build step)
        log_info("Publishing to PyPI...")
        subprocess.run(["poetry", "publish", "--build", "--skip-existing"], check=True)

        # Get the published version
        result = subprocess.run(
            ["poetry", "version", "-s"], capture_output=True, text=True, check=True
        )
        py_version = result.stdout.strip()
        log_success(
            f"Python SDK published to PyPI: trainloop-llm-logging v{py_version}"
        )

    def publish_typescript_sdk(self):
        """Publish TypeScript SDK to npm"""
        log_info("Publishing TypeScript SDK to npm...")

        if not self.ts_sdk_dir.exists():
            log_error(f"TypeScript SDK directory not found at {self.ts_sdk_dir}")

        # Change to the TypeScript SDK directory
        os.chdir(self.ts_sdk_dir)

        # Ensure npm is installed
        if shutil.which("npm") is None:
            log_error("npm not found. Install Node.js from https://nodejs.org/")

        # Clean previous builds
        log_info("Cleaning old artifacts...")
        if (self.ts_sdk_dir / "dist").exists():
            shutil.rmtree(self.ts_sdk_dir / "dist", ignore_errors=True)

        # Build the package
        log_info("Building package...")
        subprocess.run(["npm", "run", "build"], check=True)

        # Publish to npm
        log_info("Publishing to npm...")
        npm_token = os.environ.get("NPM_TOKEN")

        if npm_token:
            # Create temporary .npmrc file with token
            npmrc_path = self.ts_sdk_dir / ".npmrc"
            with open(npmrc_path, "w", encoding="utf-8") as f:
                f.write(f"//registry.npmjs.org/:_authToken={npm_token}")

            try:
                subprocess.run(
                    ["npm", "publish", "--access", "public", "--force"], check=True
                )
            finally:
                # Remove the .npmrc file
                if npmrc_path.exists():
                    npmrc_path.unlink()
        else:
            # If NPM_TOKEN is not set, assume user is already logged in
            subprocess.run(
                ["npm", "publish", "--access", "public", "--force"], check=False
            )

        # Get the published version
        with open(self.ts_sdk_dir / "package.json", encoding="utf-8") as f:
            package_json = json.load(f)
            ts_version = package_json.get("version")

        log_success(
            f"TypeScript SDK published to npm: trainloop-llm-logging v{ts_version}"
        )

    def main(self, args):
        """Main function"""
        log_info("Starting TrainLoop Evals SDK publishing process")

        # Check versions first
        self.check_versions()

        if not args.python_only and not args.typescript_only:
            # Publish both SDKs
            self.publish_python_sdk()
            self.publish_typescript_sdk()
        elif args.python_only:
            # Publish only Python SDK
            self.publish_python_sdk()
        elif args.typescript_only:
            # Publish only TypeScript SDK
            self.publish_typescript_sdk()

        log_success("SDK publishing completed successfully!")
        version = self.get_version()
        log_info(f"Python SDK: trainloop-llm-logging v{version}")
        log_info(f"TypeScript SDK: trainloop-llm-logging v{version}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Publish TrainLoop Evals SDK packages to PyPI and npm"
    )
    parser.add_argument(
        "--python-only", action="store_true", help="Only publish the Python SDK"
    )
    parser.add_argument(
        "--typescript-only",
        "--ts-only",
        action="store_true",
        help="Only publish the TypeScript SDK",
    )

    args = parser.parse_args()

    publisher = SdkPublisher()
    publisher.main(args)
