#!/usr/bin/env python3
"""
TrainLoop Evals - Master Publish Script

This script coordinates the publishing of all TrainLoop Evals components.
Run with --help to see available options.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Publish TrainLoop Evals components")
    parser.add_argument("--skip-sdk", action="store_true", help="Skip SDK publishing")
    parser.add_argument("--skip-cli", action="store_true", help="Skip CLI publishing")
    parser.add_argument(
        "--skip-studio", action="store_true", help="Skip Studio publishing"
    )
    parser.add_argument(
        "--skip-github", action="store_true", help="Skip GitHub releases"
    )
    parser.add_argument("--skip-pypi", action="store_true", help="Skip PyPI publishing")
    args = parser.parse_args()

    # Get script directory
    script_dir = Path(__file__).resolve().parent
    publish_dir = script_dir / "publish"

    # Check if publish directory exists
    if not publish_dir.is_dir():
        print(f"ERROR: publish/ directory not found at {publish_dir}")
        sys.exit(1)

    # Publish SDK (Python and TypeScript)
    if not args.skip_sdk and not args.skip_pypi:
        print("\n==== Publishing SDK Packages ====")
        sdk_script = publish_dir / "publish_sdk.py"
        print(f"Using SDK script: {sdk_script}")
        if sdk_script.exists():
            try:
                # Build command with arguments
                cmd = [sys.executable, str(sdk_script)]
                if args.skip_github:
                    cmd.append("--skip-github")
                
                # Run the script directly
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, check=True)
                
                if result.returncode != 0:
                    print(f"ERROR: SDK publish script failed with code {result.returncode}")
                    sys.exit(1)
                    
            except subprocess.SubprocessError as e:
                print(f"ERROR: Failed to publish SDK: {e}")
                sys.exit(1)
        else:
            print(f"WARNING: SDK publish script not found at {sdk_script}")
    else:
        print("\n==== Skipping SDK Publishing ====")

    # Publish CLI
    if not args.skip_cli and not args.skip_pypi:
        print("\n==== Publishing CLI Package ====")
        cli_script = publish_dir / "publish_cli.py"

        if cli_script.exists():
            try:
                # Run the script directly
                cmd = [sys.executable, str(cli_script)]
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, check=True)
                
                if result.returncode != 0:
                    print(f"ERROR: CLI publish script failed with code {result.returncode}")
                    sys.exit(1)
                    
            except subprocess.SubprocessError as e:
                print(f"ERROR: Failed to publish CLI: {e}")
                sys.exit(1)
        else:
            print(f"WARNING: CLI publish script not found at {cli_script}")
    else:
        print("\n==== Skipping CLI Publishing ====")

    # Publish Studio
    if not args.skip_studio and not args.skip_github:
        print("\n==== Publishing Studio Runner ====")
        studio_script = publish_dir / "publish_studio.py"

        if studio_script.exists():
            try:
                # Run the script directly
                cmd = [sys.executable, str(studio_script)]
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, check=True)
                
                if result.returncode != 0:
                    print(f"ERROR: Studio publish script failed with code {result.returncode}")
                    sys.exit(1)
                    
            except subprocess.SubprocessError as e:
                print(f"ERROR: Failed to publish Studio: {e}")
                sys.exit(1)
        else:
            print(f"WARNING: Studio publish script not found at {studio_script}")
    else:
        print("\n==== Skipping Studio Publishing ====")

    print("\n✅ Publish process completed successfully!")


if __name__ == "__main__":
    main()
