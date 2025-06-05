"""
TrainLoop evaluation runner
───────────────────────────
CLI entry-point that

  1. Imports every module in `eval.suites`.
  2. Collects the `results` list each module produces.
  3. Writes one JSONL file per suite in `data/results/`.
  4. Prints a coloured pass/fail summary.

Usage from project root
───────────────────────
  # run all suites
  python -m eval.runner

  # run only one suite
  python -m eval.runner hyperscout_parsers
"""

from __future__ import annotations
import argparse
import importlib
import json
import pkgutil
import sys
import os
from dataclasses import asdict
from pathlib import Path
from typing import List
from datetime import datetime

from .types import Result

# --------------------------------------------------------------------------- #
# Config paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # .../trainloop/
SUITE_DIR = PROJECT_ROOT / "eval" / "suites"
RESULT_DIR = PROJECT_ROOT / "data" / "results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# ANSI helpers
OK = "\033[32m✓\033[0m"
BAD = "\033[31m✗\033[0m"


# --------------------------------------------------------------------------- #
# Suite discovery
# --------------------------------------------------------------------------- #
def _discover_suites(filter_names: set[str] | None = None):
    """
    Yields (suite_name, results_list) tuples.
    A suite is any module under eval.suites that defines `results`.
    """
    if not SUITE_DIR.exists():
        return

    # Ensure project root on path
    sys.path.insert(0, str(PROJECT_ROOT))

    prefix = "eval.suites."
    for info in pkgutil.walk_packages([str(SUITE_DIR)], prefix):
        name = info.name.split(".")[-1]
        if filter_names and name not in filter_names:
            continue
        module = importlib.import_module(info.name)
        if hasattr(module, "results"):
            results = getattr(module, "results")
            if isinstance(results, list) and all(
                isinstance(r, Result) for r in results
            ):
                yield name, results

    # Pop the path we inserted
    sys.path.pop(0)


# --------------------------------------------------------------------------- #
# Result writer
# --------------------------------------------------------------------------- #
def _write_results(suite: str, results: List[Result], timestamp: str):
    os.makedirs(RESULT_DIR / timestamp, exist_ok=True)
    out_file = RESULT_DIR / timestamp / f"{suite}.jsonl"
    with out_file.open("a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(asdict(r), default=str) + "\n")


# --------------------------------------------------------------------------- #
# Pretty printer
# --------------------------------------------------------------------------- #
def _print_summary(all_results: dict[str, List[Result]]):
    for suite, results in all_results.items():
        total = len(results)
        passed = sum(r.passed for r in results)
        status = OK if passed == total else BAD
        print(f"{suite:<30} {status} {passed}/{total}")

        if passed != total:  # print failures
            for r in results:
                if not r.passed:
                    print(f"  - {r.metric} on {r.sample.tag}: {r.reason}")


# --------------------------------------------------------------------------- #
# CLI main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(prog="trainloop eval")
    ap.add_argument("suite", nargs="*", help="suite names to run (default: all)")
    args = ap.parse_args()

    filter_set = set(args.suite) if args.suite else None
    collected: dict[str, List[Result]] = {}

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for suite_name, results in _discover_suites(filter_set):
        collected[suite_name] = results
        if not results:
            print(f"No results found for suite {suite_name}")
            continue
        _write_results(suite_name, results, timestamp)

    if not collected:
        print("No suites found. Add files to eval/suites/ with a `results` list.")
        sys.exit(1)

    _print_summary(collected)

    # exit code 0 = all pass
    all_pass = all(r.passed for rs in collected.values() for r in rs)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
