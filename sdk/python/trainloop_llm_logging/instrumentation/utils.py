from __future__ import annotations
import inspect
import json
import os
import time
import re
import gzip
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse
from ..types import ParsedRequestBody, ParsedResponseBody, LLMCallLocation
from ..logger import instrumentation_utils_logger as logger

_MAX_BODY = 2 * 1024 * 1024  # 2 MB
DEFAULT_HOST_ALLOWLIST = ["api.openai.com", "api.anthropic.com"]
HEADER_NAME = "X-Trainloop-Tag"


def now_ms() -> int:
    return int(time.time() * 1000)


def cap(b: bytes) -> str:
    """Return the first `_MAX_BODY` bytes decoded to UTF-8 (best-effort)."""
    try:
        return b[:_MAX_BODY].decode("utf-8", errors="ignore")
    except Exception:
        # Ensure we always return a string even on decode failure
        return ""


def caller_site() -> LLMCallLocation:
    st = inspect.stack()
    for fr in st[3:]:
        fn = fr.filename
        if "site-packages" in fn or "/lib/" in fn:
            continue
        return {"file": fn, "lineNumber": str(fr.lineno)}
    return {"file": "unknown", "lineNumber": "0"}


def parse_request_body(s: str) -> Optional[ParsedRequestBody]:
    """Parse a request body string into a structured format with messages array.

    Returns:
        A ParsedRequestBody or None if parsing fails
    """
    try:
        body = json.loads(s)
    except Exception:
        return None

    # Handle case where messages are directly provided with model
    if "messages" in body and "model" in body:
        messages = body.get("messages") or []
        model = body.get("model")

        # Use dict comprehension to exclude messages and model
        model_params = {k: v for k, v in body.items() if k not in ["messages", "model"]}

        return {"messages": messages, "model": model, "modelParams": model_params}
    else:
        logger.warning(f"Skipping invalid request body: {s}")
        return None


def parse_response_body(s: Union[str, bytes]) -> Optional[ParsedResponseBody]:
    """Parse a response body string into a simplified format with just content.

    Returns:
        A ParsedResponseBody or None if parsing fails
    """
    # Handle bytes input
    if isinstance(s, bytes):
        try:
            s = s.decode("utf-8")
        except Exception:
            return None

    try:
        body = json.loads(s)
    except Exception:
        return None

    if not body:
        return None

    # If it already has content field, return that
    if "content" in body:
        # Just extract the string content regardless of nesting
        if isinstance(body["content"], dict) and "content" in body["content"]:
            return {"content": str(body["content"]["content"])}
        return {"content": str(body["content"])}

    logger.warning(f"Skipping invalid response body: {s}")
    return None


def build_call(**kw) -> Dict[str, Any]:
    """
    Build a call dictionary with the given keyword arguments.

    Args:
        **kw: Keyword arguments to include in the call dictionary

    Returns:
        A dictionary with the given keyword arguments and "isLLMRequest" set to True
    """
    kw.setdefault("isLLMRequest", True)
    return kw


def is_llm_call(url: str) -> bool:
    """True if the hostname is in the allow-list."""
    try:
        # Use environment variable if set, otherwise fall back to default
        host_allowlist_env = os.environ.get("TRAINLOOP_HOST_ALLOWLIST")
        if host_allowlist_env:
            host_allowlist = set(host_allowlist_env.split(","))
            logger.debug("Using custom host allowlist from TRAINLOOP_HOST_ALLOWLIST: %s", host_allowlist)
        else:
            host_allowlist = set(DEFAULT_HOST_ALLOWLIST)
            logger.debug("TRAINLOOP_HOST_ALLOWLIST not set, using default: %s", host_allowlist)

        return urlparse(url).hostname in host_allowlist
    except Exception:  # pragma: no cover
        return False


def pop_tag(headers: Any) -> Optional[str]:
    """Pop (case-insensitive) X-Trainloop-Tag from a mutable headers mapping."""
    for k in list(headers.keys()):
        if k.lower() == HEADER_NAME.lower():
            return headers.pop(k)
    return None


# --------------------------------------------------------------------------- #
#  Stream-response formatter (OpenAI / Anthropic)                              #
# --------------------------------------------------------------------------- #

_OPENAI_RE = re.compile(r'^data:\s*(\{.*?"choices".*?\})\s*$', re.M)
_ANTHROPIC_RE = re.compile(r'^data:\s*(\{.*?"content_block_delta".*?\})\s*$', re.M)


def format_streamed_content(raw: bytes) -> bytes:
    """
    Collapse an SSE chat stream into a single JSON blob with just the content.
    If parsing fails, return the original bytes.
    """
    # Check if the response is gzipped
    if raw.startswith(b"\x1f\x8b"):
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass  # If decompression fails, continue with original bytes

    text = raw.decode("utf8", errors="ignore")

    # ---- Handle HTTP chunked transfer encoding ----
    # Check if this looks like chunked encoding (starts with hex chunk size)
    if "\r\n" in text and text.split("\r\n")[0].strip():
        try:
            # Simple chunked decoding - extract content after chunk headers
            lines = text.split("\r\n")
            content_parts = []
            i = 0
            while i < len(lines):
                # Try to parse the line as a hex chunk size
                try:
                    chunk_size = int(lines[i].strip(), 16)
                    if chunk_size == 0:
                        break  # End of chunks
                    # Next line should be the chunk data
                    if i + 1 < len(lines):
                        content_parts.append(lines[i + 1])
                    i += 2  # Skip chunk size and chunk data lines
                except ValueError:
                    # Not a chunk size, might be chunk data or other content
                    content_parts.append(lines[i])
                    i += 1

            if content_parts:
                text = "".join(content_parts)
        except Exception:
            # If chunked decoding fails, continue with original text
            pass

    # ---- Regular JSON Response (non-streaming) ----
    try:
        js = json.loads(text)
        # Handle OpenAI chat completion response
        if "choices" in js and js["choices"]:
            choice = js["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                out = {"content": choice["message"]["content"]}
                return json.dumps(out, ensure_ascii=False).encode()
    except Exception:
        pass  # Not a regular JSON response, continue with streaming logic

    # ---- OpenAI ------------------------------------------------------------
    if '"chat.completion.chunk"' in text:
        parts: list[str] = []
        for m in _OPENAI_RE.finditer(text):
            try:
                js = json.loads(m.group(1))
                delta = js["choices"][0]["delta"]
                if "content" in delta:
                    parts.append(delta["content"])
            except Exception:
                pass
        if parts:
            out = {"content": "".join(parts)}
            return json.dumps(out, ensure_ascii=False).encode()

    # ---- Anthropic ---------------------------------------------------------
    if '"content_block_delta"' in text:
        parts: list[str] = []
        for m in _ANTHROPIC_RE.finditer(text):
            try:
                js = json.loads(m.group(1))
                if js["delta"].get("text"):
                    parts.append(js["delta"]["text"])
            except Exception:
                pass
        if parts:
            out = {"content": "".join(parts)}
            return json.dumps(out, ensure_ascii=False).encode()

    return raw  # fallback unchanged
