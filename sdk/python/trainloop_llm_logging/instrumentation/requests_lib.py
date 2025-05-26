"""
Instrumentation for the *requests* library to intercept and log HTTP calls for
TrainLoop evaluations.  Monkey-patches Session.request to capture data while
keeping requests' streaming semantics intact.
"""

from __future__ import annotations
import functools
from typing import List
from urllib3.response import HTTPResponse as _Urllib3Resp

from .utils import (
    now_ms,
    cap,
    caller_site,
    is_llm_call,
    pop_tag,
    format_streamed_content,
)
from ..logger import create_logger
from ..exporter import FileExporter
from ..types import LLMCallData

_LOG = create_logger("trainloop-requests")


def install(exporter: FileExporter) -> None:
    """
    Monkey-patch requests.Session.request so every outbound HTTP call is
    duplicated into the TrainLoop exporter *without* interfering with normal
    streaming (iter_content, raw.read, etc.).
    """
    import requests  # pylint: disable=import-outside-toplevel

    orig = requests.sessions.Session.request

    @functools.wraps(orig)
    def wrapper(self, method: str, url: str, **kw):
        headers: dict = kw.setdefault("headers", {})
        tag = pop_tag(headers)

        if not (is_llm_call(url) or tag):
            return orig(self, method, url, **kw)

        t0 = now_ms()
        req_b = kw.get("data") or kw.get("json") or b""

        resp = orig(self, method, url, **kw)  # real network request

        # ------ tee raw HTTPResponse -------------------------------------
        captured: List[bytes] = []
        _raw: _Urllib3Resp = resp.raw  # requests' .raw is urllib3.HTTPResponse

        class TeeRaw(_Urllib3Resp):
            """Proxy around urllib3.HTTPResponse that duplicates every byte."""

            def __init__(self, inner: _Urllib3Resp):
                # We *must* call super().__init__ with the same constructor
                # signature urllib3 expects - easiest is to store and delegate.
                self._inner = inner

            # --------- I/O primitives that requests / urllib3 call --------
            def read(self, *args, **kwargs):  # noqa: D401
                chunk = self._inner.read(*args, **kwargs)
                if chunk:
                    captured.append(chunk)
                return chunk

            def readline(self, *args, **kwargs):
                chunk = self._inner.readline(*args, **kwargs)
                if chunk:
                    captured.append(chunk)
                return chunk

            def stream(self, *args, **kwargs):  # noqa: D401
                for chunk in self._inner.stream(*args, **kwargs):
                    captured.append(chunk)
                    yield chunk

            def __iter__(self):
                for chunk in self._inner:
                    captured.append(chunk)
                    yield chunk

            # Everything else → delegate
            def __getattr__(self, item):
                return getattr(self._inner, item)

        resp.raw = TeeRaw(_raw)

        # ------ fire exporter record on Response.close() -----------------
        _orig_close = resp.close

        def _on_close():
            try:
                body_bytes = b"".join(captured)
                pretty = format_streamed_content(body_bytes)
                t1 = now_ms()

                call_data = LLMCallData(
                    status=resp.status_code,
                    method=method.upper(),
                    url=url,
                    startTimeMs=t0,
                    endTimeMs=t1,
                    durationMs=t1 - t0,
                    tag=tag,
                    location=caller_site(),
                    isLLMRequest=True,
                    headers={},
                    requestBodyStr=cap(
                        req_b
                        if isinstance(req_b, (bytes, bytearray))
                        else str(req_b).encode()
                    ),
                    responseBodyStr=cap(pretty),
                )
                exporter.record_llm_call(call_data)
            finally:
                _orig_close()

        resp.close = _on_close
        return resp

    # ---- global patch ------
    requests.sessions.Session.request = wrapper
