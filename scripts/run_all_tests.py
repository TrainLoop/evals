#!/usr/bin/env python3
"""
Run all tests for the TrainLoop project.

This script runs tests for:
- CLI unit and integration tests
- Python SDK tests
- Checks for MagicMock directory creation
"""

import subprocess
import sys
import os
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def run_command(cmd, cwd, description):
    """Run a command and return whether it succeeded."""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{description}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"Command: {cmd}")
    print(f"Directory: {cwd}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✓ {description} - PASSED{RESET}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"{RED}✗ {description} - FAILED{RESET}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{RED}Error output:{RESET}")
                print(result.stderr)
            return False
    except Exception as e:
        print(f"{RED}✗ {description} - ERROR: {str(e)}{RESET}")
        return False


def check_magicmock_dirs():
    """Check for any MagicMock directories."""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}Checking for MagicMock directories{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}")
    
    try:
        result = subprocess.run(
            'find . -name "*MagicMock*" -type d 2>/dev/null | wc -l',
            shell=True,
            capture_output=True,
            text=True
        )
        
        count = int(result.stdout.strip())
        if count == 0:
            print(f"{GREEN}✓ No MagicMock directories found{RESET}")
            return True
        else:
            print(f"{RED}✗ Found {count} MagicMock directories{RESET}")
            # Show the directories
            result = subprocess.run(
                'find . -name "*MagicMock*" -type d 2>/dev/null',
                shell=True,
                capture_output=True,
                text=True
            )
            print(f"{RED}Directories:{RESET}")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"{RED}✗ Error checking for MagicMock directories: {str(e)}{RESET}")
        return False


def cleanup_pytest_temp():
    """Clean up pytest temporary directories."""
    try:
        subprocess.run(
            "rm -rf /tmp/pytest-of-* 2>/dev/null || true",
            shell=True,
            capture_output=True
        )
        print(f"{YELLOW}Cleaned up pytest temp directories{RESET}")
    except:
        pass


def main():
    """Run all tests."""
    workspace_dir = Path(__file__).parent.parent
    os.chdir(workspace_dir)
    
    print(f"{BOLD}TrainLoop Test Suite{RESET}")
    print(f"Running all tests from: {workspace_dir}")
    
    # Clean up pytest temp directories first
    cleanup_pytest_temp()
    
    # Track results
    results = []
    
    # 1. CLI FSSpec Integration Tests
    results.append(run_command(
        "poetry run pytest ../tests/unit/test_fsspec_integration.py -v",
        workspace_dir / "cli",
        "CLI FSSpec Integration Tests"
    ))
    
    # 2. SDK FSSpec Tests
    results.append(run_command(
        "poetry run pytest tests/unit/test_fsspec_store.py -v",
        workspace_dir / "sdk/python",
        "SDK FSSpec Tests"
    ))
    
    # 3. SDK Store Tests (including fixed MagicMock tests)
    results.append(run_command(
        "poetry run pytest tests/unit/test_store.py -v",
        workspace_dir / "sdk/python",
        "SDK Store Tests"
    ))
    
    # 4. Init Command Tests
    results.append(run_command(
        "poetry run pytest ../tests/integration/init_flow/test_init_command.py -v",
        workspace_dir / "cli",
        "Init Command Integration Tests"
    ))
    
    # 5. Run all CLI unit tests
    results.append(run_command(
        "poetry run pytest -m unit -v",
        workspace_dir / "cli",
        "All CLI Unit Tests"
    ))
    
    # 6. Run all SDK unit tests
    results.append(run_command(
        "poetry run pytest -m unit -v",
        workspace_dir / "sdk/python",
        "All SDK Unit Tests"
    ))
    
    # 7. Check for MagicMock directories
    results.append(check_magicmock_dirs())
    
    # Summary
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}Test Summary{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTotal: {total} test suites")
    print(f"{GREEN}Passed: {passed}{RESET}")
    if passed < total:
        print(f"{RED}Failed: {total - passed}{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{BOLD}✓ All tests passed!{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ Some tests failed!{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())