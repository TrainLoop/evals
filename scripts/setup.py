#!/usr/bin/env python3
"""
TrainLoop Monorepo Setup Script

Installs all dependencies across the entire monorepo.
Perfect for Docker environments and fresh development setups.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
COLORS = {
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "BOLD": "\033[1m",
    "ENDC": "\033[0m",
}

# Set project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()


def colorize(text: str, color: str) -> str:
    """Apply color to text."""
    return f"{COLORS.get(color, '')}{text}{COLORS['ENDC']}"


def print_header(text: str):
    """Print a section header."""
    print(f"\n{colorize('=' * 60, 'BLUE')}")
    print(colorize(f"  {text}", "BLUE"))
    print(f"{colorize('=' * 60, 'BLUE')}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{colorize('✓', 'GREEN')} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{colorize('✗', 'RED')} {text}")


def print_info(text: str):
    """Print info message."""
    print(f"{colorize('→', 'CYAN')} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{colorize('⚠', 'YELLOW')} {text}")


def run_command(cmd: List[str], cwd: Path, description: str) -> bool:
    """Run a command and return success status."""
    print_info(f"{description} in {cwd.relative_to(PROJECT_ROOT)}")

    try:
        subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        print_success(f"Completed: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed: {description}")
        if e.stderr:
            print(f"  {colorize('Error:', 'RED')} {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {' '.join(cmd)}")
        return False


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_prerequisites() -> bool:
    """Check if required tools are installed."""
    print_header("Checking Prerequisites")

    all_good = True

    # Check Node.js and npm
    if check_command_exists("node"):
        print_success("Node.js is installed")
    else:
        print_error("Node.js is not installed")
        all_good = False

    if check_command_exists("npm"):
        print_success("npm is installed")
    else:
        print_error("npm is not installed")
        all_good = False

    # Check Poetry
    if check_command_exists("poetry"):
        print_success("Poetry is installed")
    else:
        print_error("Poetry is not installed")
        print_warning(
            "Install with: curl -sSL https://install.python-poetry.org | python3 -"
        )
        all_good = False

    # Check Python
    if check_command_exists("python3"):
        print_success("Python 3 is installed")
    else:
        print_error("Python 3 is not installed")
        all_good = False

    return all_good


def install_npm_dependencies() -> List[Tuple[Path, bool]]:
    """Install npm dependencies in all relevant directories."""
    print_header("Installing npm Dependencies")

    npm_dirs = [
        Path("docs"),
        Path("infra"),
        Path("runner"),
        Path("sdk/typescript"),
        Path("ui"),
    ]

    results = []

    for dir_path in npm_dirs:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists() and (full_path / "package.json").exists():
            success = run_command(
                ["npm", "install"], full_path, "Installing npm dependencies"
            )
            results.append((dir_path, success))
        else:
            print_warning(f"Skipping {dir_path} - directory or package.json not found")
            results.append((dir_path, False))

    return results


def install_poetry_dependencies() -> List[Tuple[Path, bool]]:
    """Install Poetry dependencies in all relevant directories."""
    print_header("Installing Poetry Dependencies")

    poetry_dirs = [
        Path("."),  # Root directory
        Path("cli"),
        Path("sdk/python"),
    ]

    results = []

    for dir_path in poetry_dirs:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists() and (full_path / "pyproject.toml").exists():
            success = run_command(
                ["poetry", "install"], full_path, "Installing Poetry dependencies"
            )
            results.append((dir_path, success))
        else:
            print_warning(
                f"Skipping {dir_path} - directory or pyproject.toml not found"
            )
            results.append((dir_path, False))

    return results


def print_summary(
    npm_results: List[Tuple[Path, bool]], poetry_results: List[Tuple[Path, bool]]
):
    """Print installation summary."""
    print_header("Installation Summary")

    total_success = 0
    total_failed = 0

    print(colorize("npm Dependencies:", "BOLD"))
    for path, success in npm_results:
        if success:
            print(f"  {colorize('✓', 'GREEN')} {path}")
            total_success += 1
        else:
            print(f"  {colorize('✗', 'RED')} {path}")
            total_failed += 1

    print(f"\n{colorize('Poetry Dependencies:', 'BOLD')}")
    for path, success in poetry_results:
        if success:
            print(f"  {colorize('✓', 'GREEN')} {path}")
            total_success += 1
        else:
            print(f"  {colorize('✗', 'RED')} {path}")
            total_failed += 1

    print(
        f"\n{colorize('Total:', 'BOLD')} {total_success} succeeded, {total_failed} failed"
    )

    if total_failed == 0:
        print(f"\n{colorize('✨ All dependencies installed successfully!', 'GREEN')}")
        return True
    else:
        print(
            f"\n{colorize('⚠ Some installations failed. Please check the errors above.', 'YELLOW')}"
        )
        return False


def main():
    """Main setup function."""
    print(colorize("\n🚀 TrainLoop Monorepo Setup", "BOLD"))
    print("This script will install all dependencies across the monorepo.\n")

    # Check prerequisites
    if not check_prerequisites():
        print_error("\nPlease install missing prerequisites before continuing.")
        sys.exit(1)

    start_time = time.time()

    # Install all dependencies
    npm_results = install_npm_dependencies()
    poetry_results = install_poetry_dependencies()

    # Print summary
    success = print_summary(npm_results, poetry_results)

    elapsed_time = time.time() - start_time
    print(f"\n{colorize('Setup completed in', 'CYAN')} {elapsed_time:.1f} seconds")

    if success:
        print(f"\n{colorize('Next steps:', 'BOLD')}")
        print("  1. Run 'npm run dev' to start the UI development server")
        print(
            "  2. Run 'poetry run trainloop --help' in the cli directory to use the CLI"
        )
        print("  3. Run 'npm run test' to run tests")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)

    main()
