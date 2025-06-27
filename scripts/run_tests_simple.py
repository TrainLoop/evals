#!/usr/bin/env python3
"""
Simple test runner for TrainLoop that focuses on key tests.
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


def main():
    """Run key tests to verify the FSSpec implementation."""
    workspace_dir = Path(__file__).parent.parent
    
    print(f"{BOLD}TrainLoop Test Runner (Simple){RESET}")
    print(f"Testing key FSSpec implementation changes...\n")
    
    # Test commands that should work
    test_commands = [
        {
            "name": "SDK FSSpec Store Tests",
            "dir": workspace_dir / "sdk/python", 
            "cmd": "poetry run pytest tests/unit/test_fsspec_store.py::test_save_samples_with_s3_path_mock -v"
        },
        {
            "name": "SDK Store Tests (MagicMock fix)",
            "dir": workspace_dir / "sdk/python",
            "cmd": "poetry run pytest tests/unit/test_store.py::TestStore::test_save_samples_creates_jsonl_file tests/unit/test_store.py::TestStore::test_save_samples_ensures_events_dir_exists -v"
        },
        {
            "name": "SDK Registry Tests",
            "dir": workspace_dir / "sdk/python",
            "cmd": "poetry run pytest tests/unit/test_store.py::TestStore::test_update_registry_creates_new_registry tests/unit/test_store.py::TestStore::test_update_registry_updates_existing_entry -v"
        },
        {
            "name": "Check for MagicMock Directories",
            "dir": workspace_dir,
            "cmd": 'find . -name "*MagicMock*" -type d 2>/dev/null | wc -l',
            "check": lambda output: int(output.strip()) == 0
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_commands:
        print(f"{BLUE}{BOLD}Running: {test['name']}{RESET}")
        print(f"Directory: {test['dir']}")
        print(f"Command: {test['cmd']}\n")
        
        try:
            result = subprocess.run(
                test['cmd'],
                shell=True,
                cwd=test['dir'],
                capture_output=True,
                text=True
            )
            
            # Custom check function or standard return code check
            if 'check' in test:
                success = test['check'](result.stdout)
            else:
                success = result.returncode == 0
            
            if success:
                print(f"{GREEN}✓ PASSED{RESET}\n")
                passed += 1
            else:
                print(f"{RED}✗ FAILED{RESET}")
                if result.stdout:
                    print("Output:", result.stdout)
                if result.stderr:
                    print("Error:", result.stderr)
                print()
                failed += 1
                
        except Exception as e:
            print(f"{RED}✗ ERROR: {str(e)}{RESET}\n")
            failed += 1
    
    # Summary
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"Total tests: {len(test_commands)}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{RESET}")
        return 1
    else:
        print(f"\n{GREEN}{BOLD}All tests passed!{RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(main())