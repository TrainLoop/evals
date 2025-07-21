"""TrainLoop CLI 'upgrade' command."""

from __future__ import annotations

import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path
import importlib

import click
import yaml

from .utils import find_root


FILES_TO_UPDATE = ["README.md", ".gitignore", ".env.example"]


def _recreate_venv(trainloop_dir: Path) -> None:
    """Delete and recreate the nested .venv."""
    venv_path = trainloop_dir / ".venv"
    if venv_path.exists():
        shutil.rmtree(venv_path)
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    if sys.platform == "win32":
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_path / "bin" / "pip"
    subprocess.run([str(pip_exe), "install", "trainloop-cli"], check=True)


def _merge_configs(base_config: dict, user_config: dict) -> dict:
    """Merge user config with base config, preserving user values."""
    merged = base_config.copy()

    for key, value in user_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_configs(merged[key], value)
        else:
            merged[key] = value

    return merged


def _update_config_with_template(trainloop_dir: Path, version: str) -> None:
    """Update config file with new template while preserving user settings."""
    config_path = trainloop_dir / "trainloop.config.yaml"
    scaffold_config_path = (
        Path(__file__).parent.parent
        / "scaffold"
        / "trainloop"
        / "trainloop.config.yaml"
    )

    # Load existing user config
    user_config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}

    # Load template config
    template_config = {}
    if scaffold_config_path.exists():
        with open(scaffold_config_path, "r", encoding="utf-8") as f:
            template_config = yaml.safe_load(f) or {}

    # Merge configs (user values take precedence)
    merged_config = _merge_configs(template_config, user_config)

    # Always update version
    merged_config.setdefault("trainloop", {})["version"] = version

    # Write merged config
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(merged_config, f, sort_keys=False, default_flow_style=False)


def upgrade_command() -> None:
    """Upgrade TrainLoop project to the latest release."""
    click.echo("Updating trainloop-cli to latest version...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "trainloop-cli"],
        check=True,
    )

    root_path = find_root()
    if root_path is None:
        raise RuntimeError("Could not find root directory")
    trainloop_dir = root_path
    scaffold_dir = Path(__file__).parent.parent / "scaffold" / "trainloop"

    click.echo("Updating project files...")
    for name in FILES_TO_UPDATE:
        src = scaffold_dir / name
        dest = trainloop_dir / name
        if src.exists():
            shutil.copy2(src, dest)

    importlib.invalidate_caches()
    version = metadata.version("trainloop-cli")
    _update_config_with_template(trainloop_dir, version)

    _recreate_venv(trainloop_dir)

    click.echo("✅ Upgrade complete!")
