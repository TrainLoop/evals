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
from . import logger as logger_module
from .instrumentation.utils import HEADER_NAME


def trainloop_tag(tag: str) -> dict[str, str]:
    """Helper to merge into headers:  >>> headers |= trainloop_tag("checkout")"""
    return {HEADER_NAME: tag}


_IS_INIT = False
_EXPORTER = None


def collect(
    trainloop_config_path: str | None = None, flush_immediately: bool = False
) -> None:
    """
    Initialize the SDK (idempotent).  Does nothing unless
    TRAINLOOP_DATA_FOLDER is set.

    Args:
        trainloop_config_path: Path to config file (optional)
        flush_immediately: If True, flush each LLM call immediately (useful for testing)
    """
    global _IS_INIT, _EXPORTER
    if _IS_INIT:
        return

    print("[TrainLoop] Loading config...")
    load_config_into_env(trainloop_config_path)
    if "TRAINLOOP_DATA_FOLDER" not in os.environ:
        logger_module.register_logger.warning(
            "TRAINLOOP_DATA_FOLDER not set - SDK disabled"
        )
        return

    _EXPORTER = FileExporter(
        flush_immediately=flush_immediately
    )  # flushes every 10 s or 5 items (or immediately if flush_immediately=True)
    install_patches(_EXPORTER)  # monkey-patch outbound HTTP

    _IS_INIT = True
    logger_module.register_logger.info("TrainLoop Evals SDK initialized")


def flush() -> None:
    """
    Manually flush any buffered LLM calls to disk.
    Useful for testing or when you want to ensure data is written immediately.
    """
    global _EXPORTER
    if _EXPORTER:
        _EXPORTER.flush()
    else:
        logger_module.register_logger.warning(
            "SDK not initialized - call collect() first"
        )
