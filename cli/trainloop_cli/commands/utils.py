from pathlib import Path
import os
import yaml


def find_root() -> Path:
    """Walk upward until we hit trainloop.config.yaml; error if missing."""
    cur = Path.cwd()
    for p in [cur, *cur.parents]:
        if (p / "trainloop.config.yaml").exists():
            return p
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
