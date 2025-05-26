"""
Filesystem helpers - JSONL shards + _registry.json.

Path layout identical to the Node SDK.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .logger import create_logger
from .types import CollectedSample, LLMCallLocation, Registry, RegistryEntry

_log = create_logger("trainloop-store")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def update_registry(data_dir: str, loc: LLMCallLocation, tag: str) -> None:
    """
    Persist (file, line) → {tag, firstSeen, lastSeen, count}
    Never duplicates; tag can be overwritten in place.
    """
    path = Path(data_dir) / "_registry.json"
    _log.debug("Updating registry at %s", path)

    if path.exists():
        try:
            reg: Registry = json.loads(path.read_text())
            # If reg is an empty object, initialize it
            if reg == {}:
                reg = {"schema": 1, "files": {}}
        except Exception:
            _log.error("Corrupt registry - recreating")
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

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reg, indent=2))
    _log.debug(
        "Registry written - %s:%s = %s (count=%d)",
        loc["file"],
        loc["lineNumber"],
        entry["tag"],
        entry["count"],
    )


def save_samples(data_dir: str, samples: list[CollectedSample]) -> None:
    if not samples:
        return
    event_dir = Path(data_dir) / "events"
    event_dir.mkdir(parents=True, exist_ok=True)

    now = int(time.time() * 1000)
    window = 10 * 60 * 1000
    latest = max([int(f.stem) for f in event_dir.glob("*.jsonl")] + [0])
    ts = latest if now - latest < window else now

    with (event_dir / f"{ts}.jsonl").open("a", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
