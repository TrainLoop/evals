# logger.py
from __future__ import annotations

import logging
import os

_LEVELS = {"ERROR": 40, "WARN": 30, "INFO": 20, "DEBUG": 10}
_DEFAULT = "WARN"


class LazyLogger(logging.Logger):
    """Lazy logger that creates the actual logger on first access."""

    def __init__(self, name: str):
        self.name = name
        self._logger = None

    def __getattr__(self, attr):
        if self._logger is None:
            self._logger = create_logger(self.name)
        return getattr(self._logger, attr)

    def __bool__(self):
        # Always return True so `if logger:` checks work
        return True


# Global loggers with lazy initialization
exporter_logger = LazyLogger("trainloop-exporter")
config_logger = LazyLogger("trainloop-config")
store_logger = LazyLogger("trainloop-store")
requests_logger = LazyLogger("trainloop-requests")
httpx_logger = LazyLogger("trainloop-httpx")
http_client_logger = LazyLogger("trainloop-http.client")
instrumentation_utils_logger = LazyLogger("trainloop-instrumentation-utils")
register_logger = LazyLogger("trainloop-register")


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

    # Note: We can't use our own loggers here since they aren't created yet
    if "TRAINLOOP_LOG_LEVEL" in os.environ:
        print(f"[TrainLoop] Using log level from TRAINLOOP_LOG_LEVEL: {lvl_name}")
    else:
        print(f"[TrainLoop] TRAINLOOP_LOG_LEVEL not set, using default: {lvl_name}")

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
