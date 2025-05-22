"""
Entry point - mirrors TS `src/index.ts`.

• Loads YAML / env config
• Spins up FileExporter
• Installs outbound-HTTP patches (requests, httpx, …)
"""

from __future__ import annotations

import os

from .config import load_config_into_env
from .exporter import FileExporter
from .instrumentation import install_patches
from .logger import create_logger
from .instrumentation.utils import HEADER_NAME

_log = create_logger("trainloop-register")


def trainloop_tag(tag: str) -> dict[str, str]:
    """Helper to merge into headers:  >>> headers |= trainloop_tag("checkout")"""
    return {HEADER_NAME: tag}


_IS_INIT = False


def collect(trainloop_config_path: str | None = None) -> None:
    """
    Initialize the SDK (idempotent).  Does nothing unless
    TRAINLOOP_DATA_FOLDER is set.
    """
    global _IS_INIT
    if _IS_INIT:
        return

    load_config_into_env(trainloop_config_path)
    if "TRAINLOOP_DATA_FOLDER" not in os.environ:
        _log.warning("TRAINLOOP_DATA_FOLDER not set - SDK disabled")
        return
    exporter = FileExporter()  # flushes every 10 s or 5 items
    install_patches(exporter)  # monkey-patch outbound HTTP

    _IS_INIT = True
    _log.info("TrainLoop Evals SDK initialized")
