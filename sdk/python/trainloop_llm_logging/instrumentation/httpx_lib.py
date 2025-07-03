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
        def __init__(self, inner: httpx.SyncByteStream, buf: List[bytes], on_exhaust=None):
            self._inner = inner
            self._buf = buf
            self._on_exhaust = on_exhaust

        def __iter__(self):
            try:
                for chunk in self._inner:
                    self._buf.append(chunk)
                    yield chunk
            finally:
                # Call the exhaustion callback when iteration is complete
                if self._on_exhaust:
                    self._on_exhaust()

        def close(self):
            self._inner.close()

    class _TeeAsync(httpx.AsyncByteStream):
        def __init__(self, inner: httpx.AsyncByteStream, buf: List[bytes], on_exhaust=None):
            self._inner = inner
            self._buf = buf
            self._on_exhaust = on_exhaust

        async def __aiter__(self):
            try:
                async for chunk in self._inner:
                    self._buf.append(chunk)
                    yield chunk
            finally:
                # Call the exhaustion callback when iteration is complete
                if self._on_exhaust:
                    self._on_exhaust()

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
            
            # Create exhaust callback
            def on_exhaust():
                _flush(captured, request.method, url, req_b, tag, t0, exporter)

            response = httpx.Response(
                status_code=original.status_code,
                headers=original.headers,
                stream=_TeeSync(original.stream, captured, on_exhaust),
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
            
            # Create exhaust callback
            def on_exhaust():
                _flush(captured, request.method, url, req_b, tag, t0, exporter)

            response = httpx.Response(
                status_code=original.status_code,
                headers=original.headers,
                stream=_TeeAsync(original.stream, captured, on_exhaust),
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

    def _patch_content_methods(response, captured, method, url, req_b, tag, t0, exporter):
        """Patch content access methods to trigger flush when content is read."""
        _flushed = False
        
        def maybe_flush():
            nonlocal _flushed
            if not _flushed and captured:
                _flushed = True
                _flush(captured, method, url, req_b, tag, t0, exporter)
        
        # Patch response.content property
        if hasattr(response, '_content'):
            orig_content = response._content
            def get_content():
                maybe_flush()
                return orig_content
            response._content = property(get_content)
        
        # Patch response.text property
        if hasattr(response, 'text'):
            orig_text = response.text
            def get_text():
                maybe_flush()
                return orig_text
            response.text = property(get_text)
        
        # Patch response.json method
        if hasattr(response, 'json'):
            orig_json = response.json
            def patched_json(*args, **kwargs):
                maybe_flush()
                return orig_json(*args, **kwargs)
            response.json = patched_json
        
        # Patch response.aread method
        if hasattr(response, 'aread'):
            orig_aread = response.aread
            async def patched_aread(*args, **kwargs):
                result = await orig_aread(*args, **kwargs)
                maybe_flush()
                return result
            response.aread = patched_aread
        
        # Patch response.read method
        if hasattr(response, 'read'):
            orig_read = response.read
            def patched_read(*args, **kwargs):
                result = orig_read(*args, **kwargs)
                maybe_flush()
                return result
            response.read = patched_read
    
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
        
        # Add automatic flush triggers when content is accessed
        _patch_content_methods(response, captured, method, url, req_b, tag, t0, exporter)

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
        
        # Add automatic flush triggers when content is accessed
        _patch_content_methods(response, captured, method, url, req_b, tag, t0, exporter)

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
