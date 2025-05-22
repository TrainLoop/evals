"""TrainLoop Evaluations CLI default command (studio viewer)."""

import os
import subprocess
import sys
from pathlib import Path
import importlib.metadata

from .utils import load_config_for_cli, find_root, resolve_data_folder_path


def studio_command():
    """Launch local viewer (studio) for inspecting events and results."""
    print("Launching TrainLoop Evaluations Studio...")

    # Find the root directory containing trainloop.config.yaml
    # Try when the trainloop directory is in the current directory
    root_path = Path.cwd() / "trainloop"
    if not root_path.exists():
        # Try when the trainloop directory is in the parent directory
        root_path = find_root()
        if not root_path.exists():
            print(
                "Error: Could not find a trainloop folder in current directory or any parent directory."
            )
            sys.exit(1)

    # Load configuration to ensure TRAINLOOP_DATA_FOLDER is set
    load_config_for_cli(root_path)

    # Set up environment variables for the Next.js app
    env = os.environ.copy()
    # Set port for Next.js - using port 8888 as mentioned in the memory
    env["PORT"] = "8888"

    # Check if npx is available
    try:
        subprocess.run(
            ["npx", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: npx not found. Please install Node.js and npm to run the studio.")
        print("Visit https://nodejs.org/ for installation instructions.")
        sys.exit(1)

    # Resolve data folder path
    trainloop_data_folder = resolve_data_folder_path(
        os.environ.get("TRAINLOOP_DATA_FOLDER", ""), root_path / "trainloop.config.yaml"
    )

    env["TRAINLOOP_DATA_FOLDER"] = trainloop_data_folder

    # Launch the Next.js application using npx
    try:
        # Get the version from the parent directory's VERSION file
        try:
            # Get the version from current package
            version = importlib.metadata.version("trainloop-cli")
            print(f"Using TrainLoop Studio version {version}")
        except (ImportError, importlib.metadata.PackageNotFoundError):
            # Fallback to reading VERSION file if available
            try:
                version_result = subprocess.run(
                    [
                        "cat",
                        str(Path(__file__).parent.parent.parent.parent / "VERSION"),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                version = version_result.stdout.strip()
                print(f"Using TrainLoop Studio version {version}")
            except (subprocess.SubprocessError, FileNotFoundError):
                # Hardcoded fallback version
                version = "0.3.14"  # Update this when version changes
                print(f"Using TrainLoop Studio version {version} (fallback)")

        print(f"Starting studio viewer on http://localhost:{env['PORT']}")

        # Run using npx
        subprocess.Popen(
            [
                "npx",
                "--yes",
                f"https://github.com/trainloop/evals/releases/download/v{version}/trainloop-studio-runner-{version}.tgz",
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffered
        )
    except Exception as e:
        print(f"Failed to launch TrainLoop Studio using npx: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down TrainLoop Evaluations Studio...")
        sys.exit(0)
