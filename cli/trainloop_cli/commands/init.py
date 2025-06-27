"""TrainLoop Evaluations CLI 'init' command."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import cast
import fsspec
from fsspec.spec import AbstractFileSystem


def init_command(force: bool = False):
    """Scaffold data/ and eval/ directories, create sample metrics and suites."""
    print("Initializing TrainLoop Evaluations...")

    # Get the path to the scaffold directory inside the package
    current_file = Path(__file__)
    # The scaffold is inside the trainloop_cli package
    scaffold_dir = current_file.parent.parent / "scaffold"

    # Get destination directory (current working directory)
    dest_dir = Path.cwd()
    trainloop_dir = dest_dir / "trainloop"

    # Check if trainloop directory already exists
    if trainloop_dir.exists():
        if force:
            print(
                f"Warning: {trainloop_dir} already exists. --force flag detected, removing existing directory."
            )
            try:
                shutil.rmtree(trainloop_dir)
            except OSError as e:
                print(
                    f"Error: Could not remove existing directory {trainloop_dir}. {e}"
                )
                sys.exit(1)
        else:
            print(
                f"Error: {trainloop_dir} already exists. Use --force to overwrite or remove it manually."
            )
            sys.exit(1)

    # Check if scaffold directory exists
    if not scaffold_dir.exists() or not (scaffold_dir / "trainloop").exists():
        print(f"Error: Could not find scaffold templates at {scaffold_dir}")
        sys.exit(1)

    # Copy the scaffold directory to the trainloop directory
    shutil.copytree(scaffold_dir / "trainloop", trainloop_dir)

    # Ensure the data folder exists
    data_dir = trainloop_dir / "data"
    events_dir = data_dir / "events"
    results_dir = data_dir / "results"
    registry_file = data_dir / "_registry.json"

    # Use fsspec to create directories and write registry file
    registry_file_str = str(registry_file)
    fs_spec = fsspec.open(registry_file_str, "w")
    fs = cast(AbstractFileSystem, fs_spec.fs)

    if fs:
        fs.makedirs(str(data_dir), exist_ok=True)
        fs.makedirs(str(events_dir), exist_ok=True)
        fs.makedirs(str(results_dir), exist_ok=True)

    # Use fsspec to write registry file
    with fsspec.open(registry_file_str, "w") as f:
        f.write("{}")  # type: ignore

    # Create a virtual environment inside the trainloop directory
    venv_path = trainloop_dir / ".venv"
    print(f"\nCreating virtual environment in {venv_path}...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Successfully created virtual environment at {venv_path}")

        # Determine pip executable path
        if sys.platform == "win32":
            pip_executable = venv_path / "Scripts" / "pip.exe"
        else:
            pip_executable = venv_path / "bin" / "pip"

        print(f"Installing trainloop-cli into {venv_path}...")
        subprocess.run(
            [str(pip_executable), "install", "trainloop-cli"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Successfully installed trainloop-cli in the virtual environment.")
    except subprocess.CalledProcessError as e:
        print(f"Error during virtual environment setup: {e.stderr}")
        print("Please ensure Python's venv module is available and try again.")
        # Optionally, you might want to exit or clean up here if this step is critical
    except FileNotFoundError:
        print(
            "Error: Python executable not found. Could not create virtual environment."
        )

    # Install appropriate SDK based on project type (for the main project, not the nested venv)
    install_appropriate_sdk(dest_dir)

    # Print the directory tree structure dynamically
    print("\nCreated trainloop directory with the following structure:")
    print_directory_tree(trainloop_dir, ignore_dirs={"__pycache__", ".venv"})

    print("\n✨ Initialization complete! ✨")
    print(f"\nTrainLoop project created at: {trainloop_dir}")
    print(f"A dedicated Python venv for evaluations is at: {venv_path}")
    print("   (trainloop-cli is installed there for custom metric/suite development)")

    print("\n🚀 Next Steps:")
    print("1. Start collecting data: See `trainloop/README.md`.")
    print(
        "2. For custom metric/suite development (IDE autocompletion & terminal work):"
    )
    print(
        r"   - In your terminal: `source trainloop/.venv/bin/activate` (or `.\trainloop\.venv\Scripts\activate` on Windows)"
    )
    print(
        "   - For IDEs (e.g., VS Code): Add `./trainloop/.venv/lib/pythonX.Y/site-packages` to your Python interpreter's extra paths."
    )
    print("     (Replace X.Y with your Python version, e.g., python3.11)")
    print(
        "3. Define custom logic: Edit files in `trainloop/eval/metrics/` and `trainloop/eval/suites/`."
    )


def install_appropriate_sdk(project_dir: Path):
    """Detect project type and install appropriate SDK."""
    # Check for TypeScript/JavaScript project
    package_json = project_dir / "package.json"
    requirements_txt = project_dir / "requirements.txt"

    if package_json.exists():
        # It's a Node.js project
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                package_data = json.load(f)

            # Check if the SDK is already installed
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})

            if (
                "trainloop-llm-logging" not in dependencies
                and "trainloop-llm-logging" not in dev_dependencies
            ):
                # Try to install the SDK using npm
                print(
                    "\nDetected Node.js project, installing trainloop-llm-logging package..."
                )
                try:
                    subprocess.run(
                        ["npm", "install", "trainloop-llm-logging@latest"],
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    print("Successfully installed trainloop-llm-logging package")
                except subprocess.CalledProcessError as e:
                    print(
                        f"Failed to install trainloop-llm-logging package: {e.stderr}"
                    )
                    print(
                        "Please manually install with: npm install trainloop-llm-logging"
                    )
            else:
                print(
                    "trainloop-llm-logging package is already installed in package.json"
                )

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading package.json: {e}")

    elif requirements_txt.exists():
        # It's a Python project
        try:
            with open(requirements_txt, "r", encoding="utf-8") as f:
                requirements = f.read()

            if "trainloop-llm-logging" not in requirements:
                # Add the SDK to requirements.txt
                print(
                    "\nDetected Python project, adding trainloop-llm-logging to requirements.txt..."
                )
                with fsspec.open(str(requirements_txt), "a", encoding="utf-8") as f:
                    f.write("\n# TrainLoop evaluation SDK\ntrainloop-llm-logging\n")  # type: ignore
                print("Added trainloop-llm-logging to requirements.txt")
                print("Please run: pip install -r requirements.txt")
            else:
                print("trainloop-llm-logging is already in requirements.txt")

        except IOError as e:
            print(f"Error reading/writing requirements.txt: {e}")

    else:
        # Create a new requirements.txt file if no project type detected
        print(
            "\nNo package.json or requirements.txt found. Please add trainloop-llm-logging to your project dependencies."
        )


def print_directory_tree(
    directory, prefix="", is_last=True, is_root=True, ignore_dirs=None
):
    """Print a directory tree structure.

    Args:
        directory: Path object of the directory to print
        prefix: Prefix to use for current line (used for recursion)
        is_last: Whether this is the last item in its parent directory
        is_root: Whether this is the root directory
        ignore_dirs: Set of directory names to ignore (optional)
    """
    if ignore_dirs is None:
        ignore_dirs = set()

    descriptions = {
        "data": "# git-ignored",
        "events": "# append-only *.jsonl shards of raw calls",
        "results": "# verdicts; one line per test per event",
        "_registry.json": "# Shows every model call in the system",
        "metrics": "# user-defined primitives",
        "suites": "# user-defined test collections",
    }

    path_name = directory.name
    if is_root:
        print(f"  {path_name}/")
        new_prefix = "  "
    else:
        connector = "└── " if is_last else "├── "
        description = (
            f" {descriptions.get(path_name, '')}" if path_name in descriptions else ""
        )
        print(f"{prefix}{connector}{path_name}/{description}")
        new_prefix = prefix + ("    " if is_last else "│   ")

    items = list(directory.iterdir())
    dirs = sorted(
        [item for item in items if item.is_dir() and item.name not in ignore_dirs]
    )
    files = sorted([item for item in items if item.is_file()])

    for i, dir_path in enumerate(dirs):
        print_directory_tree(
            dir_path,
            new_prefix,
            i == len(dirs) - 1 and len(files) == 0,
            False,
            ignore_dirs,
        )

    for i, file_path in enumerate(files):
        connector = "└── " if i == len(files) - 1 else "├── "
        description = (
            f" {descriptions.get(file_path.name, '')}"
            if file_path.name in descriptions
            else ""
        )
        print(f"{new_prefix}{connector}{file_path.name}{description}")
