"""
Filesystem helpers - JSONL shards + _registry.json.

Path layout identical to the Node SDK.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import cast
import fsspec
from fsspec.spec import AbstractFileSystem

from .logger import store_logger as logger
from .types import CollectedSample, LLMCallLocation, Registry, RegistryEntry


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def update_registry(data_dir: str, loc: LLMCallLocation, tag: str) -> None:
    """
    Persist (file, line) → {tag, firstSeen, lastSeen, count}
    Never duplicates; tag can be overwritten in place.
    """
    path = Path(data_dir) / "_registry.json"
    logger.debug("Updating registry at %s", path)

    # Use fsspec to check if file exists and read it
    path_str = str(path)
    fs_spec = fsspec.open(path_str, "r")
    fs = cast(AbstractFileSystem, fs_spec.fs)

    if fs and fs.exists(path_str):
        try:
            with fsspec.open(path_str, "r") as f:
                reg: Registry = json.loads(f.read())  # type: ignore
            # If reg is an empty object, initialize it
            if reg == {}:
                reg = {"schema": 1, "files": {}}
        except Exception:
            logger.error("Corrupt registry - recreating")
            reg = {"schema": 1, "files": {}}
    else:
        reg = {"schema": 1, "files": {}}

    files = reg["files"].setdefault(loc["file"], {})
    now = _now_iso()

    entry: RegistryEntry
    if loc["lineNumber"] in files:  # already seen this line
        entry = files[loc["lineNumber"]]
        if entry["tag"] != tag:  # tag changed in source
            entry["tag"] = tag
        entry["lastSeen"] = now
        entry["count"] += 1
    else:  # first time
        entry = files[loc["lineNumber"]] = RegistryEntry(
            lineNumber=loc["lineNumber"],
            tag=tag,
            firstSeen=now,
            lastSeen=now,
            count=1,
        )

    # Use fsspec to create directory and write file
    parent_str = str(path.parent)
    fs_spec_write = fsspec.open(path_str, "w")
    fs_write = cast(AbstractFileSystem, fs_spec_write.fs)

    if fs_write:
        fs_write.makedirs(parent_str, exist_ok=True)

    with fsspec.open(path_str, "w") as f:
        f.write(json.dumps(reg, indent=2))  # type: ignore
    logger.debug(
        "Registry written - %s:%s = %s (count=%d)",
        loc["file"],
        loc["lineNumber"],
        entry["tag"],
        entry["count"],
    )


def save_samples(data_dir: str, samples: list[CollectedSample]) -> None:
    if not samples:
        return

    # Handle both file paths and S3 URLs
    if (
        data_dir.startswith("s3://")
        or data_dir.startswith("gs://")
        or data_dir.startswith("az://")
    ):
        # Handle cloud storage paths directly
        event_dir_str = f"{data_dir}/events"
    else:
        # Local file system
        event_dir = Path(data_dir) / "events"
        event_dir_str = str(event_dir)

    # Use fsspec for directory creation
    file_path = f"{event_dir_str}/dummy.jsonl"
    fs_spec = fsspec.open(file_path, "w")
    fs = cast(AbstractFileSystem, fs_spec.fs)

    if fs:
        fs.makedirs(event_dir_str, exist_ok=True)
    else:
        raise ValueError(f"Failed to create directory {event_dir_str}")

    now = int(time.time() * 1000)
    window = 10 * 60 * 1000

    # For cloud storage, we can't use Path.glob, so we'll skip the window logic
    if data_dir.startswith(("s3://", "gs://", "az://")):
        ts = now
    else:
        event_dir = Path(event_dir_str)
        latest = max([int(f.stem) for f in event_dir.glob("*.jsonl")] + [0])
        ts = latest if now - latest < window else now

    # Use fsspec to write samples
    file_path = f"{event_dir_str}/{ts}.jsonl"
    with fsspec.open(file_path, "a", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")  # type: ignore
