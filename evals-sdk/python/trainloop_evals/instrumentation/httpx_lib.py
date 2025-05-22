# trainloop_evals/instrumentation/httpx_lib.py
"""
httpx instrumentation (sync + async) that:
 • keeps streaming 100 % intact for the caller
 • duplicates every byte into a buffer
 • emits ONE record to the exporter once the user has
   finished reading / closing the Response
"""

from __future__ import annotations
from typing import Any, List

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

_LOG = create_logger("trainloop-httpx")


def install(exporter: FileExporter) -> None:
    """
    Monkey-patch httpx.Client and httpx.AsyncClient to intercept all HTTP requests.
    Captures request/response data and timing, sending it to the provided exporter.
    """
    import httpx  # pylint: disable=import-outside-toplevel

    # ------------------------------------------------------------------ #
    #  Tiny helpers - tee wrappers that satisfy httpx’ stream contracts   #
    # ------------------------------------------------------------------ #
    class _TeeSync(httpx.SyncByteStream):
        def __init__(self, inner: httpx.SyncByteStream, buf: List[bytes]):
            self._inner = inner
            self._buf = buf

        def __iter__(self):
            for chunk in self._inner:
                self._buf.append(chunk)
                yield chunk

        def close(self):
            self._inner.close()

    class _TeeAsync(httpx.AsyncByteStream):
        def __init__(self, inner: httpx.AsyncByteStream, buf: List[bytes]):
            self._inner = inner
            self._buf = buf

        async def __aiter__(self):
            async for chunk in self._inner:
                self._buf.append(chunk)
                yield chunk

        async def aclose(self) -> None:  # noqa: D401
            await self._inner.aclose()

    # ------------------------------------------------------------------ #
    #  Transport that swaps in the tee-stream                             #
    # ------------------------------------------------------------------ #
    class Tap(httpx.BaseTransport, httpx.AsyncBaseTransport):
        """
        Custom transport that wraps another httpx transport to intercept requests.
        Handles both sync and async requests, capturing timing and payloads.
        """

        def __init__(self, inner: httpx.HTTPTransport | httpx.AsyncHTTPTransport):
            self._inner = inner

        # ---------- sync ----------
        def handle_request(self, request: httpx.Request):
            """
            Intercept synchronous HTTP requests, measure timing, and capture data.
            """
            tag = pop_tag(request.headers)
            url = str(request.url)

            if not (is_llm_call(url) or tag):
                return self._inner.handle_request(request)

            t0 = now_ms()
            req_b = request.read()

            original = self._inner.handle_request(request)
            captured: List[bytes] = []

            response = httpx.Response(
                status_code=original.status_code,
                headers=original.headers,
                stream=_TeeSync(original.stream, captured),
                request=request,
                extensions=original.extensions,
            )

            _patch_close(
                response,
                captured,
                request.method,
                url,
                req_b,
                tag,
                t0,
                exporter,
            )
            return response

        # ---------- async ----------
        async def handle_async_request(self, request: httpx.Request):
            """
            Intercept asynchronous HTTP requests, measure timing, and capture data.
            """
            tag = pop_tag(request.headers)
            url = str(request.url)

            if not (is_llm_call(url) or tag):
                return await self._inner.handle_async_request(request)

            t0 = now_ms()
            req_b = await request.aread()

            original = await self._inner.handle_async_request(request)
            captured: List[bytes] = []

            response = httpx.Response(
                status_code=original.status_code,
                headers=original.headers,
                stream=_TeeAsync(original.stream, captured),
                request=request,  # <-- attach the real request
                extensions=original.extensions,
            )

            _patch_aclose(
                response,
                captured,
                request.method,
                url,
                req_b,
                tag,
                t0,
                exporter,
            )
            return response

    # ------------------------------------------------------------------ #
    #  Helper to add our exporter hook                                    #
    # ------------------------------------------------------------------ #
    def _flush(
        captured: List[bytes],
        method: str,
        url: str,
        req_b: bytes,
        tag: str | None,
        t0: int,
        exporter: FileExporter,
    ):
        body = b"".join(captured)
        pretty = format_streamed_content(body)
        t1 = now_ms()
        if exporter:
            call_data = LLMCallData(
                status=200,  # will be overwritten by exporter if needed
                method=method,
                url=url,
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

    def _patch_close(
        response: httpx.Response,
        captured: List[bytes],
        method: str,
        url: str,
        req_b: bytes,
        tag: str | None,
        t0: int,
        exporter: FileExporter,
    ):
        orig_close = response.close

        def _on_close():
            _flush(captured, method, url, req_b, tag, t0, exporter)
            orig_close()

        response.close = _on_close  # type: ignore[attr-defined]

    def _patch_aclose(
        response: httpx.Response,
        captured: List[bytes],
        method: str,
        url: str,
        req_b: bytes,
        tag: str | None,
        t0: int,
        exporter: FileExporter,
    ):
        orig_aclose = response.aclose

        async def _on_aclose():
            _flush(captured, method, url, req_b, tag, t0, exporter)
            await orig_aclose()

        response.aclose = _on_aclose

    # ------------------------------------------------------------------ #
    #  Swap the public Client classes                                    #
    # ------------------------------------------------------------------ #
    def _wrap(client_cls):
        class Patched(client_cls):  # type: ignore[misc]
            def __init__(self, *a: Any, **kw: Any):
                kw["transport"] = Tap(
                    kw.get("transport")
                    or (
                        httpx.HTTPTransport()
                        if client_cls is httpx.Client
                        else httpx.AsyncHTTPTransport()
                    )
                )
                super().__init__(*a, **kw)

        return Patched

    httpx.Client = _wrap(httpx.Client)  # type: ignore[assignment]
    httpx.AsyncClient = _wrap(httpx.AsyncClient)  # type: ignore[assignment]
