#!/usr/bin/env python3
"""
TrainLoop Evals - Master Build Script

This script coordinates the building of all TrainLoop Evals components.
Run with --help to see available options.
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def import_script(script_path):
    """Import a Python script as a module."""
    spec = importlib.util.spec_from_file_location("module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description="Build TrainLoop Evals components")
    parser.add_argument(
        "--skip-docker", action="store_true", help="Skip Docker image build"
    )
    parser.add_argument(
        "--skip-studio", action="store_true", help="Skip Studio package build"
    )
    parser.add_argument(
        "--push", action="store_true", help="Push Docker images after building"
    )
    parser.add_argument(
        "--update-pulumi",
        action="store_true",
        help="Update Pulumi config with new image IDs",
    )
    args = parser.parse_args()

    # Get script directory
    script_dir = Path(__file__).resolve().parent
    build_dir = script_dir / "build"

    # Check if build directory exists
    if not build_dir.is_dir():
        print(f"ERROR: build/ directory not found at {build_dir}")
        sys.exit(1)

    # Build Docker images
    if not args.skip_docker:
        print("\n==== Building Docker Images ====")
        docker_script = build_dir / "build_docker.py"

        if docker_script.exists():
            try:
                docker_module = import_script(docker_script)
                # Pass additional arguments if the script supports them
                docker_args = []
                if args.push:
                    docker_args.append("--push")
                if args.update_pulumi:
                    docker_args.append("--update-pulumi")

                # Reset sys.argv for the imported module
                saved_argv = sys.argv
                sys.argv = [str(docker_script)] + docker_args

                # Call the main function of the imported module
                if hasattr(docker_module, "main"):
                    docker_module.main()

                # Restore sys.argv
                sys.argv = saved_argv
            except (ImportError, AttributeError) as e:
                print(f"ERROR: Failed to import Docker build script: {e}")
                sys.exit(1)
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"ERROR: Failed to build Docker images: {e}")
                sys.exit(1)
        else:
            print(f"WARNING: Docker build script not found at {docker_script}")
    else:
        print("\n==== Skipping Docker Image Build ====")

    # Build Studio package
    if not args.skip_studio:
        print("\n==== Building Studio Package ====")
        studio_script = build_dir / "build_studio.py"

        if studio_script.exists():
            try:
                studio_module = import_script(studio_script)

                # Reset sys.argv for the imported module
                saved_argv = sys.argv
                sys.argv = [str(studio_script)]

                # Call the main function of the imported module
                if hasattr(studio_module, "main"):
                    studio_module.main()

                # Restore sys.argv
                sys.argv = saved_argv
            except (ImportError, AttributeError) as e:
                print(f"ERROR: Failed to import Studio build script: {e}")
                sys.exit(1)
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"ERROR: Failed to build Studio package: {e}")
                sys.exit(1)
        else:
            print(f"WARNING: Studio build script not found at {studio_script}")
    else:
        print("\n==== Skipping Studio Package Build ====")

    print("\n✅ Build process completed successfully!")


if __name__ == "__main__":
    main()
