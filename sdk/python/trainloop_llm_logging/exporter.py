"""
Buffer-then-flush exporter (same algorithm as TS).
Flushes every 10 s or when 5 calls buffered.
"""

from __future__ import annotations
import threading
from typing import List
import os
from .logger import create_logger
from .store import save_samples, update_registry
from .types import CollectedSample, LLMCallData
from .instrumentation.utils import parse_request_body, parse_response_body, caller_site

_log = create_logger("trainloop-exporter")


class FileExporter:
    _interval_s = 10
    _batch_len = 5

    def __init__(
        self,
        interval: int | None = None,
        batch_len: int | None = None,
        auto_flush: bool = False,
    ):
        self.buf: List[LLMCallData] = []
        self.lock = threading.Lock()
        self._interval_s = interval or self._interval_s
        self._batch_len = batch_len or self._batch_len
        self._auto_flush = auto_flush
        self.timer = threading.Timer(self._interval_s, self._flush_loop)
        self.timer.daemon = True
        self.timer.start()

    # ------------------------------------------------------------------ #

    def record_llm_call(self, call: LLMCallData) -> None:
        _log.info("Recording LLM call: %s", call)
        if not call.get("isLLMRequest"):
            return
        with self.lock:
            self.buf.append(call)
            if self._auto_flush or len(self.buf) >= self._batch_len:
                self._export()

    # ------------------------------------------------------------------ #

    def _export(self) -> None:
        _log.info("Exporting %d calls", len(self.buf))
        data_dir = os.getenv("TRAINLOOP_DATA_FOLDER")
        if not data_dir:
            _log.info("TRAINLOOP_DATA_FOLDER not set - export skipped")
            self.buf.clear()
            return

        samples: list[CollectedSample] = []
        for llm_call in self.buf:
            _log.info("Exporting LLM call: %s", llm_call)
            parsed_request = parse_request_body(llm_call.get("requestBodyStr", ""))
            parsed_response = parse_response_body(llm_call.get("responseBodyStr", ""))

            _log.info("Request: %s", parsed_request)
            _log.info("Response: %s", parsed_response)

            if not parsed_request or not parsed_response:
                _log.info("Invalid request or response - skipping")
                continue

            loc = llm_call.get("location") or caller_site()
            tag = llm_call.get("tag") or ""
            _log.info("Location: %s", loc)
            _log.info("Tag: %s", tag)
            update_registry(data_dir, loc, tag or "untagged")
            _log.info("Updated registry")

            sample = CollectedSample(
                durationMs=llm_call.get("durationMs", 0),
                tag=tag,
                input=parsed_request["messages"],
                output=parsed_response,
                model=parsed_request["model"],
                modelParams=parsed_request["modelParams"],
                startTimeMs=llm_call.get("startTimeMs", 0),
                endTimeMs=llm_call.get("endTimeMs", 0),
                url=llm_call.get("url", ""),
                location=loc,
            )

            samples.append(sample)

        save_samples(data_dir, samples)
        self.buf.clear()

    # ------------------------------------------------------------------ #

    def _flush_loop(self):
        _log.info("Flushing %d calls", len(self.buf))
        with self.lock:
            self._export()
        self.timer = threading.Timer(self._interval_s, self._flush_loop)
        self.timer.daemon = True
        self.timer.start()

    # ------------------------------------------------------------------ #

    def flush(self):
        with self.lock:
            self._export()

    def shutdown(self):
        self.timer.cancel()
        self.flush()
