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
from .types import TrainloopConfig
from .instrumentation.utils import DEFAULT_HOST_ALLOWLIST
from .logger import config_logger as logger


def resolve_data_folder_path(
    data_folder: str | None, config_path: str | None, root_dir: Path
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
    """
    Load TrainLoop configuration into environment variables.

    Priority order:
    1. Existing environment variables (highest priority)
    2. Config file values (fallback)
    3. Fail if critical variables are missing from both sources

    Config path resolution:
    1. trainloop_config_path parameter
    2. TRAINLOOP_CONFIG_PATH environment variable
    3. Auto-discovery (trainloop/trainloop.config.yaml or ./trainloop.config.yaml)
    """
    root = Path.cwd()
    config_file = "trainloop.config.yaml"

    # Check which environment variables are already set
    data_folder_set = "TRAINLOOP_DATA_FOLDER" in os.environ
    host_allowlist_set = "TRAINLOOP_HOST_ALLOWLIST" in os.environ
    log_level_set = "TRAINLOOP_LOG_LEVEL" in os.environ

    logger.debug(
        "Environment variable check - TRAINLOOP_DATA_FOLDER: %s",
        "set" if data_folder_set else "not set",
    )
    logger.debug(
        "Environment variable check - TRAINLOOP_HOST_ALLOWLIST: %s",
        "set" if host_allowlist_set else "not set",
    )
    logger.debug(
        "Environment variable check - TRAINLOOP_LOG_LEVEL: %s",
        "set" if log_level_set else "not set",
    )
    logger.debug(
        "Environment variable check - TRAINLOOP_CONFIG_PATH: %s",
        "set" if trainloop_config_path else "not set",
    )

    # If all variables are already set, no need to load config
    if data_folder_set and host_allowlist_set and log_level_set:
        print(
            "[TrainLoop] All TrainLoop environment variables already set, skipping config file"
        )
        return

    # Determine config path - prioritize parameter, then env var, then auto-discovery
    config_path_source = trainloop_config_path or os.environ.get(
        "TRAINLOOP_CONFIG_PATH"
    )

    resolved_config_path = None
    if config_path_source:
        # Path was provided via parameter or environment variable
        path = Path(config_path_source)

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
        # No path provided - auto-discover config file
        trainloop_dir = root / "trainloop"
        if trainloop_dir.exists() and trainloop_dir.is_dir():
            resolved_config_path = trainloop_dir / config_file
        else:
            # Fallback to looking in the current directory
            resolved_config_path = root / config_file

    # Try to load config file
    config_data = None
    if resolved_config_path and resolved_config_path.exists():
        try:
            data: TrainloopConfig = yaml.safe_load(
                resolved_config_path.read_text(encoding="utf-8")
            )
            config_data = data.get("trainloop", {})
            print(f"[TrainLoop] Loaded TrainLoop config from {resolved_config_path}")
        except Exception as e:
            print(f"[TrainLoop] Failed to load config file {resolved_config_path}: {e}")
    else:
        print(f"[TrainLoop] TrainLoop config file not found at {resolved_config_path}")

    # Set environment variables, prioritizing existing values
    if not data_folder_set:
        if config_data and "data_folder" in config_data:
            data_folder = config_data["data_folder"]
            resolved_config_path = (
                str(resolved_config_path) if resolved_config_path else None
            )
            resolved_path = resolve_data_folder_path(
                data_folder, resolved_config_path, root
            )
            os.environ["TRAINLOOP_DATA_FOLDER"] = resolved_path
            logger.info("Set TRAINLOOP_DATA_FOLDER from config: %s", resolved_path)
        else:
            raise ValueError(
                "TRAINLOOP_DATA_FOLDER not set in environment and not found in config file. "
                "Please set the environment variable or provide a valid config file."
            )

    if not host_allowlist_set:
        if (
            config_data
            and "host_allowlist" in config_data
            and config_data["host_allowlist"]
        ):
            host_allowlist = ",".join(config_data["host_allowlist"])
            os.environ["TRAINLOOP_HOST_ALLOWLIST"] = host_allowlist
            logger.info("Set TRAINLOOP_HOST_ALLOWLIST from config: %s", host_allowlist)
        else:
            # Use default host allowlist if not set anywhere
            os.environ["TRAINLOOP_HOST_ALLOWLIST"] = ",".join(DEFAULT_HOST_ALLOWLIST)
            logger.info(
                "Set TRAINLOOP_HOST_ALLOWLIST to default: %s",
                ",".join(DEFAULT_HOST_ALLOWLIST),
            )

    if not log_level_set:
        if config_data and "log_level" in config_data:
            log_level = str(config_data["log_level"]).upper()
            os.environ["TRAINLOOP_LOG_LEVEL"] = log_level
            logger.info("Set TRAINLOOP_LOG_LEVEL from config: %s", log_level)
        else:
            # Use default log level if not set anywhere
            os.environ["TRAINLOOP_LOG_LEVEL"] = "WARN"
