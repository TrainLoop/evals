"""
Helper functions for LLM Judge tracing.
"""

from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, cast
import fsspec
from fsspec.spec import AbstractFileSystem

logger = logging.getLogger(__name__)


def ensure_trace_dir() -> Optional[Path]:
    """
    Ensure the judge_traces directory exists inside the TRAINLOOP_DATA_FOLDER
    and return its path. Returns None if TRAINLOOP_DATA_FOLDER is not set.
    """
    data_folder_path_str = os.getenv("TRAINLOOP_DATA_FOLDER")

    if not data_folder_path_str:
        logger.error(
            "TRAINLOOP_DATA_FOLDER environment variable is not set. "
            "Cannot save judge traces."
        )
        return None

    data_folder_path = Path(data_folder_path_str)
    if not data_folder_path.is_dir():
        logger.error(
            f"TRAINLOOP_DATA_FOLDER ('{data_folder_path_str}') does not exist or is not a directory. "
            "Cannot save judge traces."
        )
        return None

    trace_dir = data_folder_path / "judge_traces"

    try:
        # Use fsspec to create directory
        trace_dir_str = str(trace_dir)
        fs_spec = fsspec.open(trace_dir_str + "/.placeholder", "w")
        fs = cast(AbstractFileSystem, fs_spec.fs)

        if fs:
            fs.makedirs(trace_dir_str, exist_ok=True)
        else:
            raise ValueError(f"Failed to create directory {trace_dir_str}")

        return trace_dir
    except OSError as e:
        logger.error(f"Could not create trace directory {trace_dir}: {e}")
        return None


def write_trace_log(
    trace_id: str, trace_events: List[Dict[str, Any]], trace_dir: Optional[Path]
):
    """Write the trace events to a .jsonl file."""
    if not trace_dir:
        logger.info(
            "Trace directory not available (TRAINLOOP_DATA_FOLDER likely not set). Skipping writing trace log."
        )
        return

    if not trace_events:
        logger.info(f"No trace events to write for trace_id {trace_id}.")
        return

    trace_file_path = trace_dir / f"{trace_id}.jsonl"
    try:
        # Use fsspec to write trace log
        with fsspec.open(str(trace_file_path), "w", encoding="utf-8") as f:
            for event in trace_events:
                json.dump(event, f)  # type: ignore
                f.write("\n")  # type: ignore
        logger.info(f"Judge trace written to: {trace_file_path}")
    except IOError as e:
        logger.error(f"Failed to write trace log to {trace_file_path}: {e}")
