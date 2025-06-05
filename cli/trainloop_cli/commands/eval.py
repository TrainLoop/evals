"""TrainLoop CLI - `eval` command."""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Optional, List
import litellm

from .utils import find_root, load_config_for_cli
from ..eval_core.runner import run_evaluations
from ..eval_core.runner import (
    EMOJI_ROCKET,
    HEADER_COLOR,
    RESET_COLOR,
)


def _check_and_reexecute_if_needed() -> None:
    """Checks for a nested venv and re-executes if necessary."""
    # Try to find project root silently for this initial check
    project_root_path_check = find_root(silent_on_error=True)
    if not project_root_path_check:
        # If root isn't found here, the main command logic will handle the error display later
        return

    trainloop_dir = project_root_path_check / "trainloop"
    nested_venv_path = trainloop_dir / ".venv"

    if not (nested_venv_path.exists() and nested_venv_path.is_dir()):
        return

    if sys.platform == "win32":
        venv_python_executable = nested_venv_path / "Scripts" / "python.exe"
    else:
        venv_python_executable = nested_venv_path / "bin" / "python"

    if not venv_python_executable.exists():
        # This case should ideally not happen if init command worked correctly,
        # but good to have a warning.
        print(
            f"Warning: Nested venv at {nested_venv_path} found, but its Python executable {venv_python_executable} is missing."
        )
        print("Proceeding with current environment.")
        return

    current_executable_resolved = Path(sys.executable).resolve()
    venv_python_executable_resolved = venv_python_executable.resolve()

    if current_executable_resolved != venv_python_executable_resolved:
        print(f"Re-executing 'trainloop eval' with Python from {nested_venv_path}...")
        # The first arg to execv is the python interpreter,
        # the second arg is a list where the first element is that same interpreter path,
        # followed by the original sys.argv (which includes the script path as its first element)
        args_for_exec = [str(venv_python_executable)] + sys.argv
        try:
            os.execv(str(venv_python_executable), args_for_exec)
            # os.execv replaces the current process, so this line should not be reached.
        except OSError as e:
            print(f"Error re-executing with venv Python: {e}")
            print(
                "Proceeding with current environment. Note: This might lead to import errors for suites if they rely on packages installed only in the nested venv."
            )
            # Unlike a successful execv, if it fails, the original process continues.
            # We might want to sys.exit(1) here if re-execution is critical.


# --------------------------------------------------------------------------- #
# Public entry-point (invoked by Click)
# --------------------------------------------------------------------------- #
def eval_command(suite: Optional[str] = None) -> None:
    """
    Run evaluation suites.

    Examples:
        trainloop eval                # Run every suite
        trainloop eval --suite foo    # Run only suite 'foo'
    """
    litellm.suppress_debug_info = True

    _check_and_reexecute_if_needed()

    try:
        # This call will now raise an error if root is not found (e.g., if silent_on_error was True above and returned None)
        project_root_path = find_root()
        if (
            project_root_path is None
        ):  # Defensive check, find_root should raise if not silent_on_error
            # This specific error message for clarity if find_root's behavior changes
            raise RuntimeError(
                "Project root could not be determined. Ensure 'trainloop.config.yaml' exists in the project hierarchy."
            )
    except RuntimeError as e:
        print(f"Error: {e}")
        # The error message from find_root is usually sufficient, but we add a general hint.
        print(
            "Ensure you are in a TrainLoop project directory (or a subdirectory). You can initialize one with 'trainloop init'."
        )
        sys.exit(1)

    # Load project configuration (e.g., .env files, trainloop.config.yaml)
    # This might set environment variables needed by suites or metrics.
    load_config_for_cli(project_root_path)

    suites_to_run: Optional[List[str]] = [suite] if suite else None

    target_description = (
        f"suite(s): {', '.join(suites_to_run)}"
        if suites_to_run
        else "all available suites"
    )
    print(
        f"{EMOJI_ROCKET} {HEADER_COLOR}TrainLoop Evals:{RESET_COLOR} Running {target_description} for project {project_root_path}"
    )
    print("-" * 40)  # Separator line

    exit_code = run_evaluations(project_root_path, suites_to_run)
    sys.exit(exit_code)
