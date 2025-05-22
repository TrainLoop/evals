# logger.py
from __future__ import annotations

import logging
import os

_LEVELS = {"ERROR": 40, "WARN": 30, "INFO": 20, "DEBUG": 10}
_DEFAULT = "WARN"


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
