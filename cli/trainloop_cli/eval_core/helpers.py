"""
TrainLoop evaluation helpers - tiny DSL for defining metrics and suites.
"""

from __future__ import annotations
import os
import json
import concurrent.futures as cf
import traceback
from typing import Callable, List
from pathlib import Path

from .types import Sample, Result, CollectedSampleDict
from .runner import INFO_COLOR, EMPHASIS_COLOR, RESET_COLOR, EMOJI_INFO


# ---------------- tag() loader ---------------- #
def tag(name: str, raw: bool = False) -> "Tag":
    if raw:
        return _read(name)
    return Tag(_read(name))


def _read(tag_name: str) -> List[Sample]:
    data_folder = os.getenv("TRAINLOOP_DATA_FOLDER")
    if not data_folder:
        raise RuntimeError(
            "TRAINLOOP_DATA_FOLDER environment variable must be set to the absolute path of your data directory."
        )

    events_dir = Path(data_folder) / "events"
    if not events_dir.exists():
        raise FileNotFoundError(f"{events_dir} not found - sync your data.")

    out = []
    # Find all JSONL files in events directory
    jsonl_files = list(events_dir.glob("*.jsonl"))

    if not jsonl_files:
        print(f"Warning: No event files found in {events_dir}")
        return []

    print(f"  {EMOJI_INFO} Scanning {EMPHASIS_COLOR}{len(jsonl_files)}{RESET_COLOR} event file(s) for tag {EMPHASIS_COLOR}'{tag_name}'{RESET_COLOR}...")

    # Process each JSONL file
    for file_path in jsonl_files:
        try:
            content = file_path.read_text()
            for line in content.splitlines():
                if not line.strip():
                    continue

                try:
                    d: CollectedSampleDict = json.loads(line)
                    # Only process lines with matching tag
                    if d.get("tag", "") != tag_name:
                        continue

                    # Ensure input/output are properly formatted
                    input_list = d.get("input", [])
                    output_val = d.get("output", {})

                    sample = Sample(
                        duration_ms=d.get("durationMs", 0),
                        tag=d.get("tag", ""),
                        input=input_list,
                        output=output_val,
                        model=d.get("model", ""),
                        model_params=d.get("modelParams", {}),
                        start_time_ms=d.get("startTimeMs", 0),
                        end_time_ms=d.get("endTimeMs", 0),
                        url=d.get("url", ""),
                        location=d.get("location", {}),
                    )
                    out.append(sample)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON in file {file_path}")
                except Exception as e:
                    print(f"Error processing line in {file_path}: {e}")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    print(f"  {EMOJI_INFO} Found {EMPHASIS_COLOR}{len(out)}{RESET_COLOR} samples with tag {EMPHASIS_COLOR}'{tag_name}'{RESET_COLOR}")
    return out


class Tag(list[Sample]):
    """Fluent helper: `Tag("foo").check(metric_a, metric_b)`"""

    def check(
        self, *metrics: Callable[[Sample], int], workers: int | None = None
    ) -> List[Result]:
        workers = workers or os.cpu_count() or 4
        res: list[Result] = []
        with cf.ThreadPoolExecutor(workers) as ex:
            futs = [ex.submit(_run, m, s) for s in self for m in metrics]
            for f in cf.as_completed(futs):
                res.append(f.result())
        return res


def _run(metric: Callable[[Sample], int], sample: Sample) -> Result:
    try:
        val = metric(sample)
        assert val in (0, 1), "metric must return 0 or 1"
        return Result(metric.__name__, sample, val, None if val else "failed")
    except Exception as e:
        tb = "".join(traceback.format_exception_only(type(e), e)).strip()
        return Result(metric.__name__, sample, 0, tb)
