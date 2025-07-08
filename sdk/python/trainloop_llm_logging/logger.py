# logger.py
from __future__ import annotations

from typing import cast
import logging
import os

_LEVELS = {"ERROR": 40, "WARN": 30, "INFO": 20, "DEBUG": 10}
_DEFAULT = "WARN"


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


def _configure_root_once() -> None:
    """
    Initialise the *root* logger exactly once, replacing any handlers that
    Uvicorn or another library may have installed.

    Call this early (e.g. in `main.py` **before** you import code that logs).
    """
    if getattr(_configure_root_once, "_done", False):
        return

    lvl_name = os.getenv("TRAINLOOP_LOG_LEVEL", _DEFAULT).upper()
    lvl = _LEVELS.get(lvl_name, logging.INFO)

    # 'force=True' clears anything set up by uvicorn, avoiding duplicate handlers
    logging.basicConfig(
        level=lvl,
        format="[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s",
        force=True,
    )
    _configure_root_once._done = True


def create_logger(scope: str) -> logging.Logger:
    """
    Return a named logger that inherits the single root handler.

    >>> log = create_logger("trainloop-exporter")
    >>> log.info("hello")   # ➜ [INFO] [...] [trainloop-exporter] hello
    """
    _configure_root_once()  # make sure root is ready
    logger = logging.getLogger(scope)
    return logger
