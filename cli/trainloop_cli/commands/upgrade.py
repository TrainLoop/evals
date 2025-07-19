"""TrainLoop CLI 'upgrade' command."""

from __future__ import annotations

import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import click
import yaml

from .utils import find_root


FILES_TO_UPDATE = ["README.md", "trainloop.config.yaml", ".gitignore", ".env.example"]


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


def _update_config_version(trainloop_dir: Path, version: str) -> None:
    """Add or update CLI version metadata in trainloop.config.yaml."""
    config_path = trainloop_dir / "trainloop.config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    config.setdefault("trainloop", {})["version"] = version
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False)


def upgrade_command() -> None:
    """Upgrade TrainLoop project to the latest release."""
    click.echo("Updating trainloop-cli to latest version...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "trainloop-cli"],
        check=True,
    )

    root_path = find_root()
    trainloop_dir = root_path / "trainloop"
    scaffold_dir = Path(__file__).parent.parent / "scaffold" / "trainloop"

    click.echo("Updating project files...")
    for name in FILES_TO_UPDATE:
        src = scaffold_dir / name
        dest = trainloop_dir / name
        if src.exists():
            shutil.copy2(src, dest)

    _recreate_venv(trainloop_dir)

    import importlib
    importlib.invalidate_caches()
    version = metadata.version("trainloop-cli")
    _update_config_version(trainloop_dir, version)

    click.echo("✅ Upgrade complete!")
