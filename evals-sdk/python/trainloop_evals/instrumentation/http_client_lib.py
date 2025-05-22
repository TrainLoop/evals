# trainloop_evals/instrumentation/http_client_lib.py
"""
Instrumentation for Python's http.client to intercept and log HTTP calls for
TrainLoop evaluations.  Monkey-patches HTTPConnection.request to capture
request/response data and timing - *without* breaking streaming.
"""

from __future__ import annotations
import functools
from typing import Any, List
import http.client as _http_client

from .utils import (
    now_ms,
    cap,
    caller_site,
    format_streamed_content,
    is_llm_call,
    pop_tag,
)
from ..exporter import FileExporter
from ..logger import create_logger
from ..types import LLMCallData

_LOG = create_logger("trainloop-http.client")


def install(exporter: FileExporter) -> None:
    """
    Monkey-patch http.client.HTTPConnection.request so every HTTP call made
    through the standard library is duplicated into the TrainLoop exporter,
    while the original streaming semantics stay intact.
    """
    orig = _http_client.HTTPConnection.request

    @functools.wraps(orig)
    def wrapper(
        self: _http_client.HTTPConnection,
        method: str,
        url: str,
        body: Any | None = None,
        headers: dict | None = None,
        *a,
        **kw,
    ):
        headers = headers or {}
        tag = pop_tag(headers)  # remove header early (case-insensitive)
        full_url = f"{self.scheme}://{self.host}{url}"

        if not (is_llm_call(full_url) or tag):
            # Not an LLM request - run as normal
            return orig(self, method, url, body, headers, *a, **kw)

        t0 = now_ms()
        req_b = (
            body if isinstance(body, (bytes, bytearray)) else str(body or "").encode()
        )

        # ----- fire the real request -------------------------------------
        orig(self, method, url, body, headers, *a, **kw)
        resp: _http_client.HTTPResponse = self.response

        # ----- tee the socket-file to capture every chunk ----------------
        captured: List[bytes] = []
        _real_fp = resp.fp  # original buffered reader

        class TeeFP:
            """File-like proxy that duplicates read data into *captured*."""

            def __init__(self, fp):
                self._fp = fp

            # The response uses read(), readline(), readinto() and iteration
            def read(self, *args, **kwargs):  # pylint: disable=invalid-name
                chunk = self._fp.read(*args, **kwargs)
                if chunk:
                    captured.append(chunk)
                return chunk

            def readline(self, *args, **kwargs):
                chunk = self._fp.readline(*args, **kwargs)
                if chunk:
                    captured.append(chunk)
                return chunk

            def readinto(self, b):
                n = self._fp.readinto(b)
                if n:
                    captured.append(memoryview(b)[:n])
                return n

            def __iter__(self):
                for chunk in self._fp:
                    captured.append(chunk)
                    yield chunk

            def __getattr__(self, item):
                return getattr(self._fp, item)

        resp.fp = TeeFP(_real_fp)  # type: ignore[assignment]

        # ----- emit to exporter once the user closes the response --------
        _orig_close = resp.close

        def _on_close():
            try:
                body_bytes = b"".join(captured)
                pretty = format_streamed_content(body_bytes)
                t1 = now_ms()

                call_data = LLMCallData(
                    status=resp.status,
                    method=method.upper(),
                    url=full_url,
                    startTimeMs=t0,
                    endTimeMs=t1,
                    durationMs=t1 - t0,
                    tag=tag,
                    location=caller_site(),
                    isLLMRequest=True,
                    headers={},
                    requestBodyStr=cap(req_b),
                    responseBodyStr=cap(pretty),
                )
                exporter.record_llm_call(call_data)
            finally:
                _orig_close()

        resp.close = _on_close

    # ---- global patch -------
    _http_client.HTTPConnection.request = wrapper
