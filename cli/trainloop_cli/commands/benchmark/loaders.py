"""Data loading functions for benchmark command."""

from __future__ import annotations

import json
import sys
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Any, Callable

import yaml
from dotenv import load_dotenv

from ...eval_core.types import Result, Sample
from .constants import OK, BAD, EMOJI_GRAPH, EMPHASIS_COLOR, RESET_COLOR


def load_metrics(project_root: Path) -> Dict[str, Callable[[Sample], int]]:
    """Load all available metrics from the project's eval/metrics directory."""
    metrics_dir = project_root / "eval" / "metrics"
    metrics_dict = {}

    if not metrics_dir.exists():
        print(f"{BAD} No metrics directory found at {metrics_dir}")
        return metrics_dict

    # Ensure project root is on Python path for imports
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    module_prefix = "eval.metrics."

    # Load all metric modules
    for info in pkgutil.walk_packages([str(metrics_dir)], module_prefix):
        try:
            module = importlib.import_module(info.name)
            # Look for functions that could be metrics
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                # Check if it's a callable that could be a metric
                if callable(attr) and not attr_name.startswith("_"):
                    # Store the metric function
                    metrics_dict[attr_name] = attr
        except Exception as e:
            print(f"Warning: Could not load metric module {info.name}: {e}")

    return metrics_dict


def load_latest_results(project_root: Path) -> Dict[str, List[Result]]:
    """Load the most recent evaluation results from data/results directory."""
    results_dir = project_root / "data" / "results"

    if not results_dir.exists():
        print(f"{BAD} No results directory found at {results_dir}")
        return {}

    # Find the most recent results directory (timestamp-based)
    result_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    if not result_dirs:
        print(f"{BAD} No result directories found in {results_dir}")
        return {}

    # Sort by directory name (timestamp format ensures chronological order)
    latest_dir = sorted(result_dirs)[-1]
    print(
        f"{EMOJI_GRAPH} Loading results from: {EMPHASIS_COLOR}{latest_dir.name}{RESET_COLOR}"
    )

    # Load all JSONL files from the latest directory
    all_results = {}
    for jsonl_file in latest_dir.glob("*.jsonl"):
        suite_name = jsonl_file.stem
        results = []

        with jsonl_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    result_data = json.loads(line)
                    # Reconstruct Result object from JSON
                    sample_data = result_data["sample"]
                    sample = Sample(
                        duration_ms=sample_data["duration_ms"],
                        tag=sample_data["tag"],
                        input=sample_data["input"],
                        output=sample_data["output"],
                        model=sample_data["model"],
                        model_params=sample_data["model_params"],
                        start_time_ms=sample_data["start_time_ms"],
                        end_time_ms=sample_data["end_time_ms"],
                        url=sample_data["url"],
                        location=sample_data["location"],
                    )
                    result = Result(
                        metric=result_data["metric"],
                        sample=sample,
                        passed=result_data["passed"],
                        reason=result_data.get("reason"),
                    )
                    results.append(result)

        if results:
            all_results[suite_name] = results
            print(f"  {OK} Loaded {len(results)} results from suite: {suite_name}")

    return all_results


def load_benchmark_config(project_root: Path) -> Dict[str, Any]:
    """Load benchmark configuration from trainloop.config.yaml."""
    config_path = project_root / "trainloop.config.yaml"

    # First, try to load default .env file from trainloop folder
    default_env_path = project_root / ".env"
    if default_env_path.exists():
        load_dotenv(default_env_path)
        print(f"{OK} Loaded environment from: {default_env_path}")

    if not config_path.exists():
        return {}

    with config_path.open("r") as f:
        config = yaml.safe_load(f) or {}

    trainloop_config = config.get("trainloop", {})
    benchmark_config = trainloop_config.get("benchmark", {})

    # Load benchmark-specific env file if specified (overrides default .env)
    if "env_path" in benchmark_config:
        env_path = config_path.parent / benchmark_config["env_path"]
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"{OK} Loaded benchmark environment from: {env_path}")

    return benchmark_config
