"""
Central patch installer.  Each sub-module exposes install(sink).
"""

from __future__ import annotations
from ..exporter import FileExporter

TRAINLOOP_INSTRUMENTATION_INSTALLED = False


def install_patches(exporter: FileExporter) -> None:
    global TRAINLOOP_INSTRUMENTATION_INSTALLED
    if TRAINLOOP_INSTRUMENTATION_INSTALLED:
        return
    TRAINLOOP_INSTRUMENTATION_INSTALLED = True

    # pylint: disable=import-outside-toplevel
    from . import (
        http_client_lib,
        requests_lib,
        httpx_lib,
    )

    http_client_lib.install(exporter)
    requests_lib.install(exporter)
    httpx_lib.install(exporter)
