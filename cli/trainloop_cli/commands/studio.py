"""TrainLoop Evaluations CLI default command (studio viewer)."""

import os
import subprocess
import sys
from pathlib import Path
import importlib.metadata
import tempfile
import tarfile
import shutil

from .utils import load_config_for_cli, find_root, resolve_data_folder_path


def studio_command(config_path=None, local_tar_path=None):
    """Launch local viewer (studio) for inspecting events and results."""
    # Find the root directory containing trainloop.config.yaml
    if config_path:
        # Use provided config path
        config_file_path = Path(config_path)
        if not config_file_path.exists():
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
        root_path = config_file_path.parent
    else:
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
    config_file = config_path if config_path else root_path / "trainloop.config.yaml"
    trainloop_data_folder = resolve_data_folder_path(
        os.environ.get("TRAINLOOP_DATA_FOLDER", ""), config_file
    )

    env["TRAINLOOP_DATA_FOLDER"] = trainloop_data_folder

    # Launch the Next.js application using npx
    try:
        # Determine package source
        if local_tar_path:
            # Use provided local tar file - extract to temp dir
            local_tar = Path(local_tar_path)
            if not local_tar.exists():
                print(f"❌ Local tar file not found at {local_tar_path}")
                sys.exit(1)
            
            # Create temporary directory and extract tar file
            temp_dir = tempfile.mkdtemp(prefix="trainloop-studio-")
            try:
                with tarfile.open(local_tar, 'r:gz') as tar:
                    tar.extractall(temp_dir)
                
                # Find the package.json in the extracted directory
                extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
                if not extracted_dirs:
                    print(f"❌ No directory found in extracted tar file")
                    sys.exit(1)
                
                package_dir = extracted_dirs[0]  # Should be the main package directory
                package_source = str(package_dir)
                print(f"✨ Launching TrainLoop Evaluations Studio (local build)")
                print(f"📁 Extracted to: {package_dir}")
                
            except (tarfile.TarError, Exception) as e:
                print(f"❌ Failed to extract tar file: {e}")
                sys.exit(1)
        else:
            # Get the version and use remote package
            try:
                # Get the version from current package
                version = importlib.metadata.version("trainloop-cli")
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
                except (subprocess.SubprocessError, FileNotFoundError):
                    # Hardcoded fallback version
                    raise Exception("Could not determine version")

            package_source = f"https://github.com/trainloop/evals/releases/download/v{version}/trainloop-studio-runner-{version}.tgz"
            print(f"✨ Launching TrainLoop Evaluations Studio v{version}")
            temp_dir = None

        # Run using npx
        try:
            print(f"🔧 Executing `npx --yes {package_source}`")
            process = subprocess.Popen(
                [
                    "npx",
                    "--yes",
                    package_source,
                ],
                env=env,
                # Don't capture output - let it display in real-time
                universal_newlines=True,
            )

            # Keep the script running and let the process output directly to terminal
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down TrainLoop Evaluations Studio...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                # Cleanup temp directory if it exists
                if temp_dir and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                sys.exit(0)
            finally:
                # Cleanup temp directory if it exists
                if temp_dir and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)

        except Exception as e:
            print(f"❌ Failed to launch TrainLoop Studio using npx: {e}")
            # Cleanup temp directory if it exists
            if 'temp_dir' in locals() and temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down TrainLoop Evaluations Studio...")
        # Cleanup temp directory if it exists
        if 'temp_dir' in locals() and temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        sys.exit(0)
