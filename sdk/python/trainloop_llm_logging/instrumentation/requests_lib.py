"""
Instrumentation for the *requests* library to intercept and log HTTP calls for
TrainLoop evaluations.  Monkey-patches Session.request to capture data while
keeping requests' streaming semantics intact.
"""

from __future__ import annotations
import functools
import json

from .utils import (
    now_ms,
    cap,
    caller_site,
    is_llm_call,
    pop_tag,
    format_streamed_content,
)
from ..logger import requests_logger as logger
from ..exporter import FileExporter
from ..types import LLMCallData


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

        # Read the response content immediately and record the call
        try:
            # Access the content to read the full response body
            response_content = resp.content

            # Format the response content
            pretty = format_streamed_content(response_content)
            t1 = now_ms()

            call_data = LLMCallData(
                status=resp.status_code,
                method=method.upper(),
                url=url,
                startTimeMs=t0,
                endTimeMs=t1,
                durationMs=t1 - t0,
                tag=str(tag or ""),
                location=caller_site(),
                isLLMRequest=True,
                headers={},
                requestBodyStr=cap(
                    req_b
                    if isinstance(req_b, (bytes, bytearray))
                    else (
                        # If it's a dict (from json= parameter), serialize to JSON
                        json.dumps(req_b).encode()
                        if isinstance(req_b, dict)
                        else str(req_b).encode()
                    )
                ),
                responseBodyStr=cap(pretty),
            )
            exporter.record_llm_call(call_data)
        except Exception as e:
            logger.warning(f"Error during LLM call instrumentation: {e}")

        return resp

    # ---- global patch ------
    requests.sessions.Session.request = wrapper  # type: ignore[assignment]
