"""Utilities for CLI commands."""

from pathlib import Path
from typing import Dict, Any, Optional
import os
import yaml


def find_root(silent_on_error: bool = False) -> Path | None:
    """Walk upward until we hit trainloop.config.yaml; error if missing."""
    cur = Path.cwd()
    for p in [cur, *cur.parents]:
        if (p / "trainloop.config.yaml").exists():
            return p

    if silent_on_error:
        return None

    raise RuntimeError(
        "❌  trainloop.config.yaml not found. "
        "Run this command inside the trainloop folder "
        "or create one with `trainloop init`."
    )


def resolve_data_folder_path(data_folder: str, config_path: Path) -> str:
    """
    Resolves the data folder path to an absolute path.

    Args:
        data_folder: The data folder path from config
        config_path: The path to the config file

    Returns:
        The resolved absolute data folder path as a string
    """
    if not data_folder:
        return ""

    data_folder_path = Path(data_folder)
    if data_folder_path.is_absolute():
        # If it's an absolute path, use it directly
        return str(data_folder_path.absolute())

    # If it's relative, make it relative to config directory and convert to absolute
    config_dir = Path(config_path).parent
    return str((config_dir / data_folder_path).absolute())


def load_config_for_cli(root_path: Path) -> None:
    """Parse YAML and export env-vars exactly like the JS SDK."""
    trainloop_config_path = root_path / "trainloop.config.yaml"
    if not trainloop_config_path.exists():
        return

    config = yaml.safe_load(trainloop_config_path.read_text()) or {}
    trainloop_config = config.get("trainloop", {})
    data_folder = trainloop_config.get("data_folder", "")
    resolved_path = resolve_data_folder_path(data_folder, trainloop_config_path)

    if "data_folder" in trainloop_config:  # required
        os.environ["TRAINLOOP_DATA_FOLDER"] = resolved_path
    if "log_level" in trainloop_config:  # optional
        os.environ["TRAINLOOP_LOG_LEVEL"] = str(
            trainloop_config.get("log_level", "info").upper()
        )


def load_benchmark_config(root_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load benchmark configuration from trainloop.config.yaml.

    Args:
        root_path: Path to the trainloop root directory. If None, will try to find it.

    Returns:
        Dictionary containing benchmark configuration with defaults applied.
    """
    # Default benchmark configuration
    default_config = {
        "providers": [],
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 60,
        "parallel_requests": 5,
        "env_path": None,
    }

    # Find root path if not provided
    if root_path is None:
        root_path = find_root(silent_on_error=True)
        if root_path is None:
            return default_config

    # Load config file
    config_path = root_path / "trainloop.config.yaml"
    if not config_path.exists():
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        # Extract benchmark config from trainloop section
        trainloop_config = config.get("trainloop", {})
        benchmark_config = trainloop_config.get("benchmark", {})

        # Merge with defaults
        merged_config = default_config.copy()
        merged_config.update(benchmark_config)

        return merged_config

    except Exception as e:
        # Log error but return defaults
        print(f"Warning: Failed to load benchmark config from {config_path}: {e}")
        return default_config
