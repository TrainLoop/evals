"""
Entry point - mirrors TS `src/index.ts`.

• Loads YAML / env config
• Spins up FileExporter
• Installs outbound-HTTP patches (requests, httpx, …)
"""

from __future__ import annotations

import os
import sys
from .config import load_config_into_env
from .exporter import FileExporter
from .instrumentation import install_patches
from . import logger as logger_module
from .instrumentation.utils import HEADER_NAME


def trainloop_tag(tag: str) -> dict[str, str]:
    """Helper to merge into headers:  >>> headers |= trainloop_tag("checkout")"""
    return {HEADER_NAME: tag}


# SDK initialisation state (process-wide)
_IS_INIT = False
_EXPORTER = None


def collect(
    trainloop_config_path: str | None = None, flush_immediately: bool = False
) -> None:
    """Boot-strap the TrainLoop logging SDK (idempotent).

    Calling this function installs outbound-HTTP instrumentation and starts a
    background exporter that regularly writes captured LLM calls to disk.  If
    ``TRAINLOOP_DATA_FOLDER`` is not set the SDK remains disabled so the host
    application keeps running without side-effects.
    """
    global _IS_INIT, _EXPORTER

    if _IS_INIT:
        return

    patched_libs = ["openai", "requests", "httpx"]
    for lib in patched_libs:
        if lib in sys.modules:
            # TODO: find another way to do this later!
            # In pytest environment, allow pre-imported libraries
            if "PYTEST_CURRENT_TEST" in os.environ:
                logger_module.register_logger.warning(
                    f"Library '{lib}' was imported before TrainLoop SDK initialization. "
                    f"This may reduce instrumentation coverage in tests."
                )
                continue

            error_message = (
                f"TrainLoop SDK must be initialized before importing '{lib}'.\n\n"
                f"This prevents the SDK from capturing LLM calls correctly.\n\n"
                f"Fix: Move these lines to the very top of your entry point:\n"
                f"    from trainloop_llm_logging import collect\n"
                f'    collect("/path/to/trainloop.config.yaml")\n'
                f"    then import {lib} and other libraries\n\n"
                f"The SDK needs to patch HTTP libraries before they create client instances."
            )
            raise RuntimeError(error_message)

    print("[TrainLoop] Loading config...")
    load_config_into_env(trainloop_config_path)

    if "TRAINLOOP_DATA_FOLDER" not in os.environ:
        logger_module.register_logger.warning(
            "TRAINLOOP_DATA_FOLDER not set – SDK disabled"
        )
        return

    # Create exporter (flushes every 10 s / 5 calls by default, or immediately
    # when *flush_immediately* is True) and patch HTTP libraries.
    _EXPORTER = FileExporter(flush_immediately=flush_immediately)
    install_patches(_EXPORTER)

    _IS_INIT = True
    logger_module.register_logger.info("TrainLoop LLM logging initialized")


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
