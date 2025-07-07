"""
Instrumentation for Python's http.client to intercept and log HTTP calls for
TrainLoop evaluations.  Monkey-patches HTTPConnection.request to capture
request/response data and timing - *without* breaking streaming.
"""

from __future__ import annotations
import functools
from typing import Any, List, Optional, Dict
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
from ..types import LLMCallData


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
        body: Optional[Any] = None,
        headers: Optional[Dict] = None,
        *a,
        **kw,
    ):
        headers = headers or {}
        tag = pop_tag(headers)  # remove header early (case-insensitive)

        # Determine scheme from connection type
        scheme = "https" if isinstance(self, _http_client.HTTPSConnection) else "http"
        full_url = f"{scheme}://{self.host}{url}"

        if not (is_llm_call(full_url) or tag):
            # Not an LLM request - run as normal
            return orig(self, method, url, body, headers, *a, **kw)

        t0 = now_ms()
        req_b = (
            body if isinstance(body, (bytes, bytearray)) else str(body or "").encode()
        )

        # ----- fire the real request -------------------------------------
        orig(self, method, url, body, headers, *a, **kw)

        # Store info for later when getresponse() is called
        self._tl_request_info = {  # type: ignore[attr-defined]
            "method": method,
            "url": full_url,
            "req_b": req_b,
            "tag": tag,
            "t0": t0,
            "exporter": exporter,
        }

    # ---- patch getresponse() to handle instrumentation ----
    orig_getresponse = _http_client.HTTPConnection.getresponse

    @functools.wraps(orig_getresponse)
    def getresponse_wrapper(self, *args, **kwargs):
        resp = orig_getresponse(self, *args, **kwargs)

        # Check if this connection has request info stored
        if not hasattr(self, "_tl_request_info"):
            return resp

        info = self._tl_request_info
        exporter = info["exporter"]

        # Set up response instrumentation
        captured: List[bytes] = []
        _real_fp = resp.fp
        _recorded = False

        def _record_call():
            """Record the LLM call data once response is read."""
            nonlocal _recorded
            if _recorded:
                return
            _recorded = True

            body_bytes = b"".join(captured)
            pretty = format_streamed_content(body_bytes)
            t1 = now_ms()

            call_data = LLMCallData(
                status=resp.status,
                method=info["method"].upper(),
                url=info["url"],
                startTimeMs=info["t0"],
                endTimeMs=t1,
                durationMs=t1 - info["t0"],
                tag=str(info["tag"] or ""),
                location=caller_site(),
                isLLMRequest=True,
                headers={},
                requestBodyStr=cap(info["req_b"]),
                responseBodyStr=cap(pretty),
            )
            exporter.record_llm_call(call_data)

        class TeeFP:
            """File-like proxy that duplicates read data into *captured*."""

            def __init__(self, fp):
                self._fp = fp

            def read(self, *args, **kwargs):
                chunk = self._fp.read(*args, **kwargs)
                if chunk:
                    captured.append(chunk)
                # If read() returns empty/None, stream is exhausted - record the call
                if not chunk:
                    _record_call()
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
                # Iterator exhausted - record the call
                _record_call()

            def __getattr__(self, item):
                return getattr(self._fp, item)

        resp.fp = TeeFP(_real_fp)  # type: ignore[assignment]

        # Hook into response.read() method to trigger recording
        _orig_read = resp.read

        def _read_with_recording(*args, **kwargs):
            result = _orig_read(*args, **kwargs)
            # For http.client, reading the full response means we're done
            # Trigger recording after any successful read
            _record_call()
            return result

        resp.read = _read_with_recording

        # Clean up stored info
        delattr(self, "_tl_request_info")

        return resp

    # ---- global patch -------
    _http_client.HTTPConnection.request = wrapper  # type: ignore[assignment]
    _http_client.HTTPConnection.getresponse = getresponse_wrapper  # type: ignore[assignment]
