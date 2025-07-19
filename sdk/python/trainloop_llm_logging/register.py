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
_LAST_DATA_FOLDER = None


def collect(
    trainloop_config_path: str | None = None, flush_immediately: bool = False
) -> None:
    """
    Initialize the SDK (idempotent per TRAINLOOP_DATA_FOLDER).

    If called multiple times with a *different* ``TRAINLOOP_DATA_FOLDER`` value we
    spin up a fresh exporter so that successive test runs (which each point the
    env-var at a brand-new temp directory) stay fully isolated.
    """
    global _IS_INIT, _EXPORTER, _LAST_DATA_FOLDER

    print("[TrainLoop] Loading config...")
    load_config_into_env(trainloop_config_path)

    data_folder = os.environ.get("TRAINLOOP_DATA_FOLDER")
    if not data_folder:
        logger_module.register_logger.warning(
            "TRAINLOOP_DATA_FOLDER not set - SDK disabled"
        )
        return

    # Re-initialise exporter if (a) we have never initialised OR (b) the data
    # folder changed since the last call (common in pytest where each test sets
    # a unique temp directory).
    should_reinit = (_EXPORTER is None) or (_LAST_DATA_FOLDER != data_folder)

    if should_reinit:
        _EXPORTER = FileExporter(flush_immediately=flush_immediately)
        install_patches(_EXPORTER)  # safe to call multiple times (idempotent)
        _LAST_DATA_FOLDER = data_folder
        _IS_INIT = True
        logger_module.register_logger.info(
            "TrainLoop Evals SDK initialized (data dir=%s)", data_folder
        )
    else:
        # Exporter is already pointing at the correct directory – optionally
        # update flush behaviour if the caller asks for immediate flushes.
        if flush_immediately and not _EXPORTER._flush_immediately:  # type: ignore[attr-defined]
            _EXPORTER._flush_immediately = True


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
