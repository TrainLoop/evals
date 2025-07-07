"""
Entry point - mirrors TS `src/index.ts`.

• Loads YAML / env config
• Spins up FileExporter
• Installs outbound-HTTP patches (requests, httpx, …)
"""

from __future__ import annotations

import os
import logging
from typing import cast

from .config import load_config_into_env
from .exporter import FileExporter
from .instrumentation import install_patches
from .logger import create_logger
from .instrumentation.utils import HEADER_NAME

# Global loggers for all modules
exporter_logger = cast(logging.Logger, None)
config_logger = cast(logging.Logger, None)
store_logger = cast(logging.Logger, None)
requests_logger = cast(logging.Logger, None)
httpx_logger = cast(logging.Logger, None)
http_client_logger = cast(logging.Logger, None)
instrumentation_utils_logger = cast(logging.Logger, None)
register_logger = cast(logging.Logger, None)


def create_loggers() -> None:
    global exporter_logger, config_logger, store_logger, requests_logger, httpx_logger, http_client_logger, instrumentation_utils_logger, register_logger
    exporter_logger = create_logger("trainloop-exporter")
    config_logger = create_logger("trainloop-config")
    store_logger = create_logger("trainloop-store")
    requests_logger = create_logger("trainloop-requests")
    httpx_logger = create_logger("trainloop-httpx")
    http_client_logger = create_logger("trainloop-http.client")
    instrumentation_utils_logger = create_logger("trainloop-instrumentation-utils")
    register_logger = create_logger("trainloop-register")


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

    create_loggers()
    print("[TrainLoop] Loading config...")
    load_config_into_env(trainloop_config_path)

    logger = register_logger
    if "TRAINLOOP_DATA_FOLDER" not in os.environ:
        logger.warning("TRAINLOOP_DATA_FOLDER not set - SDK disabled")
        return

    _EXPORTER = FileExporter(
        flush_immediately=flush_immediately
    )  # flushes every 10 s or 5 items (or immediately if flush_immediately=True)
    install_patches(_EXPORTER)  # monkey-patch outbound HTTP

    _IS_INIT = True
    logger.info("TrainLoop Evals SDK initialized")


def flush() -> None:
    """
    Manually flush any buffered LLM calls to disk.
    Useful for testing or when you want to ensure data is written immediately.
    """
    global _EXPORTER
    if _EXPORTER:
        _EXPORTER.flush()
    else:
        register_logger.warning("SDK not initialized - call collect() first")
