"""
TrainLoop evaluation runner logic.
──────────────────────────────
This module contains the core logic for discovering and running evaluation suites.
It's designed to be called by the `trainloop eval` CLI command.
Functions:
  run_evaluations: Discovers suites, runs them, writes results, prints summary.
"""

from __future__ import annotations
import importlib
import json
import pkgutil
import sys
from collections import defaultdict, Counter
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Dict, Set, Iterator, Tuple, Union, cast
from datetime import datetime
import fsspec
from fsspec.spec import AbstractFileSystem

from .types import Result

# ANSI helpers for console output
OK = "\033[32m✓\033[0m"
BAD = "\033[31m✗\033[0m"  # Red X
INFO_COLOR = "\033[94m"  # Blue
HEADER_COLOR = "\033[95m"  # Magenta
EMPHASIS_COLOR = "\033[93m"  # Yellow
RESET_COLOR = "\033[0m"  # Reset

EMOJI_ROCKET = "🚀"
EMOJI_FOLDER = "📂"
EMOJI_PLAY = "▶️"
EMOJI_SAVE = "💾"
EMOJI_INFO = "ℹ️"


def _discover_suites(
    project_root_dir: Path,
    suite_dir: Path,
    filter_names: Optional[Set[str]] = None,
) -> Iterator[Tuple[str, List[Result]]]:
    """
    Yields (suite_name, results_list) tuples.
    A suite is any module under the project's eval/suites directory that defines `results`.
    """
    if not suite_dir.exists():
        print(f"Warning: Suite directory not found: {suite_dir}")
        return

    # Ensure project root is on Python path for imports within suites
    original_sys_path = list(sys.path)
    if str(project_root_dir) not in sys.path:
        sys.path.insert(0, str(project_root_dir))

    module_prefix = "eval.suites."

    try:
        for info in pkgutil.walk_packages([str(suite_dir)], module_prefix):
            suite_module_name = info.name
            # Extract the simple name for filtering (e.g., 'my_suite' from 'eval.suites.my_suite')
            simple_name = suite_module_name.split(".")[-1]

            if filter_names and simple_name not in filter_names:
                continue
            try:
                print(
                    f"\n{EMOJI_PLAY} Processing suite: {EMPHASIS_COLOR}{simple_name}{RESET_COLOR}..."
                )
                module = importlib.import_module(suite_module_name)
                if hasattr(module, "results"):
                    results = getattr(module, "results")
                    if isinstance(results, list) and all(
                        isinstance(r, Result) for r in results
                    ):
                        yield simple_name, results  # Use simple_name for reporting
                    else:
                        print(
                            f"Warning: 'results' in {suite_module_name} is not a list of Result objects."
                        )
                else:
                    print(
                        f"Warning: No 'results' attribute found in {suite_module_name}."
                    )
            except ImportError as e:
                print(f"Error importing suite {suite_module_name}: {e}")
            except Exception as e:
                print(f"Error processing suite {suite_module_name}: {e}")
    finally:
        # Restore original Python path
        sys.path = original_sys_path


def _write_results(
    suite_name: str, results: List[Result], result_dir_for_run: Union[Path, str]
):
    """Writes results for a single suite to a JSONL file in the run-specific directory."""
    # Convert Path to string for fsspec
    if isinstance(result_dir_for_run, Path):
        result_dir_str = str(result_dir_for_run)
        out_file_str = str(result_dir_for_run / f"{suite_name}.jsonl")
    else:
        # Handle string paths (e.g., S3 URLs)
        result_dir_str = result_dir_for_run
        out_file_str = f"{result_dir_for_run}/{suite_name}.jsonl"

    try:
        # Ensure the directory exists using fsspec
        fs_spec = fsspec.open(out_file_str, "a")
        fs = cast(AbstractFileSystem, fs_spec.fs)

        if fs:
            fs.makedirs(result_dir_str, exist_ok=True)

        # Write results using fsspec
        with fsspec.open(out_file_str, "a", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(asdict(r), default=str) + "\n")  # type: ignore
        print(f"  {EMOJI_SAVE} {out_file_str}")
    except IOError as e:
        print(f"Error writing results for suite '{suite_name}' to {out_file_str}: {e}")


def _print_summary(all_results: Dict[str, List[Result]]):
    """Prints a pass/fail summary to the console."""
    print(f"\n{HEADER_COLOR}--- Evaluation Summary ---{RESET_COLOR}")
    if not all_results:
        print("No results to summarize.")
        return

    for suite_name, results in all_results.items():
        total = len(results)
        if total == 0:
            print(
                f"{EMPHASIS_COLOR}{suite_name:<30}{RESET_COLOR} {BAD} 0/0 (No results collected)"
            )
            continue
        passed = sum(r.passed for r in results)
        status = OK if passed == total else BAD
        print(
            f"{EMPHASIS_COLOR}{suite_name:<30}{RESET_COLOR} {status} {passed}/{total}"
        )

        if passed != total:  # print grouped failures
            failure_details: Dict[str, List[str]] = defaultdict(list)
            for r in results:
                if not r.passed:
                    reason_str = r.reason if r.reason is not None else "Unknown reason"
                    sample_tag_info = (
                        getattr(r.sample, "tag", "N/A") if r.sample else "N/A"
                    )
                    source_description = (r.metric, sample_tag_info)
                    failure_details[reason_str].append(source_description)

            for reason, sources_list in failure_details.items():
                print(
                    f"  - {BAD}{reason}{RESET_COLOR}"
                )  # Print the unique error reason
                if not sources_list:
                    continue
                source_counts = Counter(sources_list)
                for source_desc, count in source_counts.items():
                    metric, tag = source_desc
                    if count > 1:
                        print(
                            f"    (for {metric} on {EMPHASIS_COLOR}{tag}{RESET_COLOR} [{count} instances])"
                        )
                    else:
                        print(
                            f"    (for {metric} on {EMPHASIS_COLOR}{tag}{RESET_COLOR})"
                        )
    print("------------------------")


def run_evaluations(
    project_root_dir: Path,
    suite_filter_names: Optional[List[str]] = None,
) -> int:
    """
    Main entry point for running evaluations.

    Args:
        project_root_dir: The absolute path to the root of the user's project.
        suite_filter_names: An optional list of suite names to run. If None, all suites are run.

    Returns:
        0 if all suites pass, 1 otherwise.
    """
    suite_dir = project_root_dir / "eval" / "suites"
    result_dir_base = project_root_dir / "data" / "results"

    # Create a timestamped directory for this specific run's results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_dir_for_this_run = result_dir_base / timestamp
    try:
        # Use fsspec to create directory
        result_dir_str = str(result_dir_for_this_run)
        fs_spec = fsspec.open(result_dir_str + "/.placeholder", "w")
        fs = cast(AbstractFileSystem, fs_spec.fs)

        if fs:
            fs.makedirs(result_dir_str, exist_ok=True)
    except OSError as e:
        print(f"Error creating results directory {result_dir_for_this_run}: {e}")
        return 1  # Indicate failure

    filter_set = set(suite_filter_names) if suite_filter_names else None
    collected_results: Dict[str, List[Result]] = {}

    any_suites_found = False

    print(
        f"\n{EMOJI_FOLDER} {HEADER_COLOR}--- Discovering Suites in {suite_dir} ---{RESET_COLOR}"
    )
    if filter_set:
        print(f"Filtering for suites: {', '.join(filter_set)}")

    for suite_name, results_list in _discover_suites(
        project_root_dir, suite_dir, filter_set
    ):
        any_suites_found = True
        collected_results[suite_name] = results_list
        if not results_list:
            print(
                f"No results collected for suite '{suite_name}'. It might be empty or misconfigured."
            )
            continue
        _write_results(suite_name, results_list, result_dir_for_this_run)

    if not any_suites_found:
        if filter_set:
            print(f"No suites found matching your filter: {', '.join(filter_set)}.")
            print(f"Please check the names and ensure they exist in {suite_dir}.")
        else:
            print(f"No suites found in {suite_dir}.")
            print(
                "To create a suite, add a Python file to this directory defining a 'results' list."
            )
            # Consider if this should be an error (return 1) or not.
            # For now, if no suites are found (e.g. new project), it's not an error itself.
            _print_summary(collected_results)  # Will print 'No results to summarize'
            return 0  # No suites run, so technically no failures.

    _print_summary(collected_results)

    # Determine overall exit code: 0 if all metrics in all run suites passed, 1 otherwise.
    if (
        not collected_results
    ):  # Should be caught by any_suites_found, but as a safeguard
        return 0

    all_passed_overall = True
    for suite_name, results_list in collected_results.items():
        if not results_list:  # Suite ran but had no results (e.g. empty `results` list)
            # This could be considered a partial failure or warning, but for now, doesn't make all_passed_overall false
            continue
        if not all(r.passed for r in results_list):
            all_passed_overall = False
            break

    return 0 if all_passed_overall else 1
