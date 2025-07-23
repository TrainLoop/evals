"""
httpx instrumentation (sync + async) that:
 • keeps streaming 100 % intact for the caller
 • duplicates every byte into a buffer
 • emits ONE record to the exporter once the user has
   finished reading / closing the Response
"""

from __future__ import annotations
from typing import Any, List, Optional

from .utils import (
    now_ms,
    cap,
    caller_site,
    is_llm_call,
    pop_tag,
    format_streamed_content,
)
from ..exporter import FileExporter
from ..types import LLMCallData


def install(exporter: FileExporter) -> None:
    """
    Monkey-patch httpx.Client and httpx.AsyncClient to intercept all HTTP requests.
    Captures request/response data and timing, sending it to the provided exporter.
    """
    import httpx  # pylint: disable=import-outside-toplevel

    # ------------------------------------------------------------------ #
    #  Tiny helpers - tee wrappers that satisfy httpx' stream contracts   #
    # ------------------------------------------------------------------ #
    class _TeeSync(httpx.SyncByteStream):
        def __init__(self, inner: Any, buf: List[bytes], on_exhaust=None):
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
        def __init__(self, inner: Any, buf: List[bytes], on_exhaust=None):
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
    class SyncTap(httpx.BaseTransport):
        """
        Custom sync transport that wraps another httpx transport to intercept requests.
        """

        def __init__(self, inner: httpx.HTTPTransport):
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

            # Ensure we flush exactly once (either when stream exhausted OR when user accesses .content/.text/etc.)
            flushed = False

            def flush_once():
                nonlocal flushed
                if not flushed and captured:
                    flushed = True
                    _flush(captured, request.method, url, req_b, tag, t0, exporter)

            # Create exhaust callback
            def on_exhaust():
                flush_once()

            response = httpx.Response(
                status_code=original.status_code,
                headers=original.headers,
                stream=_TeeSync(original.stream, captured, on_exhaust),
                request=request,
                extensions=original.extensions,
            )

            # Patch content access methods to trigger recording when accessed
            _patch_content_access(
                response, captured, request.method, url, req_b, tag, t0, flush_once
            )

            return response

    class AsyncTap(httpx.AsyncBaseTransport):
        """
        Custom async transport that wraps another httpx transport to intercept requests.
        """

        def __init__(self, inner: httpx.AsyncHTTPTransport):
            self._inner = inner

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

            # Ensure we flush exactly once (either when stream exhausted OR when user accesses .content/.text/etc.)
            flushed = False

            def flush_once():
                nonlocal flushed
                if not flushed and captured:
                    flushed = True
                    _flush(captured, request.method, url, req_b, tag, t0, exporter)

            # Create exhaust callback
            def on_exhaust():
                flush_once()

            response = httpx.Response(
                status_code=original.status_code,
                headers=original.headers,
                stream=_TeeAsync(original.stream, captured, on_exhaust),
                request=request,  # <-- attach the real request
                extensions=original.extensions,
            )

            # Patch content access methods to trigger recording when accessed
            _patch_content_access(
                response, captured, request.method, url, req_b, tag, t0, flush_once
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
        tag: Optional[str],
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
                tag=str(tag or ""),
                location=caller_site(),
                isLLMRequest=True,
                headers={},
                requestBodyStr=cap(req_b),
                responseBodyStr=cap(pretty),
            )
            exporter.record_llm_call(call_data)

    def _patch_content_access(
        response,
        captured,
        method,
        url,
        req_b,
        tag,
        t0,
        flush_once,
    ):
        """Patch content access methods to trigger flush when content is read."""
        # Hook into the response class to intercept property/method access
        original_Response_class = type(response)

        class InstrumentedResponse(original_Response_class):
            @property
            def content(self):
                # Call parent to get content (this will read the stream via our tee)
                content_bytes = super().content
                flush_once()
                return content_bytes

            @property
            def text(self):
                text_str = super().text
                flush_once()
                return text_str

            def json(self, **kwargs):
                result = super().json(**kwargs)
                flush_once()
                return result

            async def aread(self):
                result = await super().aread()
                flush_once()
                return result

            def read(self):
                result = super().read()
                flush_once()
                return result

        # Replace the response class
        response.__class__ = InstrumentedResponse

    # ------------------------------------------------------------------ #
    #  Swap the public Client classes                                    #
    # ------------------------------------------------------------------ #
    def _wrap_sync(client_cls):
        class PatchedSync(client_cls):  # type: ignore[misc]
            def __init__(self, *a: Any, **kw: Any):
                # Handle parameter compatibility: some libraries pass 'proxies' but httpx expects 'proxy'
                if "proxies" in kw and "proxy" not in kw:
                    kw["proxy"] = kw.pop("proxies")

                inner_transport = kw.get("transport") or httpx.HTTPTransport()
                kw["transport"] = SyncTap(inner_transport)
                super().__init__(*a, **kw)

        return PatchedSync

    def _wrap_async(client_cls):
        class PatchedAsync(client_cls):  # type: ignore[misc]
            def __init__(self, *a: Any, **kw: Any):
                # Handle parameter compatibility: some libraries pass 'proxies' but httpx expects 'proxy'
                if "proxies" in kw and "proxy" not in kw:
                    kw["proxy"] = kw.pop("proxies")

                inner_transport = kw.get("transport") or httpx.AsyncHTTPTransport()
                kw["transport"] = AsyncTap(inner_transport)
                super().__init__(*a, **kw)

        return PatchedAsync

    httpx.Client = _wrap_sync(httpx.Client)  # type: ignore[assignment]
    httpx.AsyncClient = _wrap_async(httpx.AsyncClient)  # type: ignore[assignment]
