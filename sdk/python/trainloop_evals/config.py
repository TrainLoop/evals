"""
YAML/env loader from `trainloop.config.yaml`:

    trainloop:
      data_folder: "./trainloop/data"
      host_allowlist: ["api.openai.com", "api.anthropic.com"]
      log_level: "info"
"""

from __future__ import annotations

import os
from pathlib import Path
import yaml
from .logger import create_logger
from .types import TrainloopConfig
from .instrumentation.utils import DEFAULT_HOST_ALLOWLIST

_log = create_logger("trainloop-config")


def resolve_data_folder_path(
    data_folder: str, config_path: str | None, root_dir: Path
) -> str:
    """
    Resolves the data folder path based on whether it's absolute or relative.

    Args:
        data_folder: The data folder path from config
        config_path: The path to the config file, if provided
        root_dir: The current working directory

    Returns:
        The resolved data folder path as a string
    """
    if not data_folder:
        return ""

    data_folder_path = Path(data_folder)
    if data_folder_path.is_absolute():
        # If it's an absolute path, use it directly
        return str(data_folder_path)
    else:
        # If it's relative and config path was provided, make it relative to config directory
        if config_path:
            config_dir = Path(config_path).parent
            return str(config_dir / data_folder_path)
        else:
            # Otherwise, make it relative to current working directory
            return str(root_dir / data_folder_path)


def load_config_into_env(trainloop_config_path: str | None = None) -> None:
    root = Path.cwd()
    config_file = "trainloop.config.yaml"

    resolved_config_path = None
    if trainloop_config_path:
        # Path was provided - could be absolute or relative
        path = Path(trainloop_config_path)

        if path.is_absolute():
            # Use the absolute path directly
            if path.is_dir():
                # If it's a directory, look for config file inside it
                resolved_config_path = path / config_file
            else:
                # Assume it's pointing directly to the config file
                resolved_config_path = path
        else:
            # Relative path - resolve from current directory
            if path.is_dir():
                resolved_config_path = (root / path / config_file).resolve()
            else:
                resolved_config_path = (root / path).resolve()
    else:
        # No path provided - look for trainloop folder in current directory
        trainloop_dir = root / "trainloop"
        if trainloop_dir.exists() and trainloop_dir.is_dir():
            resolved_config_path = trainloop_dir / config_file
        else:
            # Fallback to looking in the current directory
            resolved_config_path = root / config_file

    if not resolved_config_path.exists():
        _log.warning("TrainLoop config file not found at %s!", resolved_config_path)
        return

    data: TrainloopConfig = yaml.safe_load(
        resolved_config_path.read_text(encoding="utf-8")
    )
    tl = data.get("trainloop", {})
    # Set data folder path in environment variables
    data_folder = tl.get("data_folder", "")
    resolved_path = resolve_data_folder_path(data_folder, resolved_config_path, root)
    os.environ.setdefault("TRAINLOOP_DATA_FOLDER", resolved_path)
    os.environ.setdefault(
        "TRAINLOOP_HOST_ALLOWLIST",
        ",".join(tl.get("host_allowlist", DEFAULT_HOST_ALLOWLIST)),
    )
    os.environ.setdefault(
        "TRAINLOOP_LOG_LEVEL", str(tl.get("log_level", "info")).upper()
    )
