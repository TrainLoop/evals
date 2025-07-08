"""
Buffer-then-flush exporter (same algorithm as TS).
Flushes every 10 s or when 5 calls buffered.
"""

from __future__ import annotations
import threading
from typing import List
import os
from .logger import exporter_logger as logger
from .store import save_samples, update_registry
from .types import CollectedSample, LLMCallData
from .instrumentation.utils import parse_request_body, parse_response_body, caller_site


class FileExporter:
    _interval_s = 10
    _batch_len = 5

    def __init__(
        self,
        interval: int | None = None,
        batch_len: int | None = None,
        flush_immediately: bool = False,
    ):
        self.buf: List[LLMCallData] = []
        self.lock = threading.Lock()
        self._interval_s = interval or self._interval_s
        self._batch_len = batch_len or self._batch_len
        self._flush_immediately = flush_immediately

        # Start periodic flush timer only when NOT in flush_immediately mode
        self.timer: threading.Timer | None = None
        if not self._flush_immediately:
            self.timer = threading.Timer(self._interval_s, self._flush_loop)
            self.timer.daemon = True
            self.timer.start()

    # ------------------------------------------------------------------ #

    def record_llm_call(self, call: LLMCallData) -> None:
        if not call.get("isLLMRequest"):
            return
        with self.lock:
            self.buf.append(call)
            if self._flush_immediately or len(self.buf) >= self._batch_len:
                self._export()

    # ------------------------------------------------------------------ #

    def _export(self) -> None:
        data_dir = os.getenv("TRAINLOOP_DATA_FOLDER")
        if not data_dir:
            logger.warning("TRAINLOOP_DATA_FOLDER not set, skipping export")
            self.buf.clear()
            return

        # Copy & clear buffer atomically to avoid writing duplicates if timer
        # fires while we are exporting (especially when flush_immediately=True).
        to_write, self.buf = self.buf, []

        samples: list[CollectedSample] = []
        for llm_call in to_write:
            parsed_request = parse_request_body(llm_call.get("requestBodyStr", ""))
            parsed_response = parse_response_body(llm_call.get("responseBodyStr", ""))

            if not parsed_request or not parsed_response:
                continue

            loc = llm_call.get("location") or caller_site()
            tag = llm_call.get("tag") or ""
            logger.info("Location: %s", loc)
            logger.info("Tag: %s", tag)
            update_registry(data_dir, loc, tag or "untagged")
            logger.info("Updated registry")

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

    # ------------------------------------------------------------------ #

    def _flush_loop(self):
        logger.info("Flushing %d calls", len(self.buf))
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
        if self.timer:
            self.timer.cancel()
        self.flush()
