"""TrainLoop Evaluations CLI 'init' command."""

import json
import shutil
import subprocess
import sys
from pathlib import Path


def init_command():
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
        print(
            f"Error: {trainloop_dir} already exists. Please remove it or use a different directory."
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
    data_dir.mkdir(exist_ok=True)
    events_dir = data_dir / "events"
    events_dir.mkdir(exist_ok=True)
    results_dir = data_dir / "results"
    results_dir.mkdir(exist_ok=True)
    registry_file = data_dir / "_registry.json"
    registry_file.write_text("{}")

    # Install appropriate SDK based on project type
    install_appropriate_sdk(dest_dir)

    # Print the directory tree structure dynamically
    print("\nCreated trainloop directory with the following structure:")
    print_directory_tree(trainloop_dir)

    print("\nInitialization complete!")
    print("\nFollow the instructions in trainloop/README.md to start collecting data.")


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
                with open(requirements_txt, "a", encoding="utf-8") as f:
                    f.write("\n# TrainLoop evaluation SDK\ntrainloop-llm-logging\n")
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


def print_directory_tree(directory, prefix="", is_last=True, is_root=True):
    """Print a directory tree structure.

    Args:
        directory: Path object of the directory to print
        prefix: Prefix to use for current line (used for recursion)
        is_last: Whether this is the last item in its parent directory
        is_root: Whether this is the root directory
    """
    # Define directory and file display names with special descriptions
    descriptions = {
        "data": "# git-ignored",
        "events": "# append-only *.jsonl shards of raw calls",
        "results": "# verdicts; one line per test per event",
        "_registry.json": "",
        "helpers.py": "# tiny DSL (tag, etc.)",
        "types.py": "# Sample / Result dataclasses",
        "runner.py": "# CLI engine",
        "metrics": "# user-defined primitives",
        "suites": "# user-defined test collections",
    }

    # Get path name for display
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

    # Get all items in the directory and sort them
    items = list(directory.iterdir())
    dirs = sorted([item for item in items if item.is_dir()])
    files = sorted([item for item in items if item.is_file()])

    # Process directories first
    for i, dir_path in enumerate(dirs):
        print_directory_tree(
            dir_path, new_prefix, i == len(dirs) - 1 and len(files) == 0, False
        )

    # Then process files
    for i, file_path in enumerate(files):
        connector = "└── " if i == len(files) - 1 else "├── "
        description = (
            f" {descriptions.get(file_path.name, '')}"
            if file_path.name in descriptions
            else ""
        )
        print(f"{new_prefix}{connector}{file_path.name}{description}")
