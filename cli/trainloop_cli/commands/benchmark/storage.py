"""Storage and output functions for benchmark results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, cast
from datetime import datetime
from dataclasses import asdict
import fsspec
from fsspec.spec import AbstractFileSystem

from .types import BenchmarkResult
from .constants import EMOJI_SAVE


def save_benchmark_results(
    benchmark_results: List[BenchmarkResult], project_root: Path, providers: List[str]
) -> Path:
    """Save benchmark results to a timestamped directory."""
    benchmark_dir = project_root / "data" / "benchmarks"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = benchmark_dir / timestamp

    # Use fsspec to create directory
    output_dir_str = str(output_dir)
    fs_spec = fsspec.open(output_dir_str + "/.placeholder", "w")
    fs = cast(AbstractFileSystem, fs_spec.fs)

    if fs:
        fs.makedirs(output_dir_str, exist_ok=True)
    else:
        raise ValueError(f"Failed to create directory {output_dir_str}")

    # Group results by suite
    results_by_suite = {}
    for result in benchmark_results:
        # Extract suite name from the original eval result
        suite_name = "default"  # fallback
        if hasattr(result.original_result, "sample") and hasattr(
            result.original_result.sample, "tag"
        ):
            # Try to extract suite from tag or use metric as suite name
            suite_name = result.original_result.metric

        if suite_name not in results_by_suite:
            results_by_suite[suite_name] = []
        results_by_suite[suite_name].append(result)

    # Save results for each suite
    for suite_name, suite_results in results_by_suite.items():
        results_file = output_dir / f"{suite_name}.jsonl"

        with fsspec.open(str(results_file), "w") as f:
            # Write metadata record (first line)
            metadata_record = {
                "type": "metadata",
                "data": {
                    "benchmark_id": f"bench_{timestamp}_{suite_name}",
                    "timestamp": datetime.now().isoformat(),
                    "suite_name": suite_name,
                    "providers": [
                        {"provider": p.split("/")[0], "model": p.split("/")[-1]}
                        for p in providers
                    ],
                    "total_samples": len(suite_results),
                },
            }
            f.write(json.dumps(metadata_record) + "\n")  # type: ignore

            # Write result records
            provider_summaries = {
                p: {
                    "total": 0,
                    "passed": 0,
                    "errors": 0,
                    "latency_sum": 0,
                    "cost_sum": 0,
                }
                for p in providers
            }

            for result in suite_results:
                # For each provider result
                for provider, provider_result in result.provider_results.items():
                    # Update summaries
                    provider_summaries[provider]["total"] += 1

                    # Determine if passed based on metric evaluation
                    passed = 0
                    score = 0.0
                    if provider_result["error"] is None:
                        # Use the verdict from the metric evaluation
                        passed = provider_result.get("verdict", 0)
                        score = float(passed)  # Convert to score
                        if provider_result["latency_ms"]:
                            provider_summaries[provider][
                                "latency_sum"
                            ] += provider_result["latency_ms"]
                        if provider_result["cost"]:
                            provider_summaries[provider]["cost_sum"] += provider_result[
                                "cost"
                            ]
                    else:
                        provider_summaries[provider]["errors"] += 1

                    if passed:
                        provider_summaries[provider]["passed"] += 1

                    # Create result record matching expected schema
                    # Determine reason for failure
                    reason = None
                    if not passed:
                        if provider_result["error"]:
                            reason = f"Provider error: {provider_result['error']}"
                        else:
                            # Check metric results for failure reason
                            metric_results = provider_result.get("metric_results", {})
                            for metric_name, metric_result in metric_results.items():
                                if not metric_result.get(
                                    "passed"
                                ) and metric_result.get("error"):
                                    reason = f"Metric '{metric_name}' error: {metric_result['error']}"
                                    break
                            if not reason:
                                reason = (
                                    f"Failed {result.original_result.metric} evaluation"
                                )

                    result_record = {
                        "type": "result",
                        "metric": result.original_result.metric,
                        "sample": {
                            **asdict(result.original_result.sample),
                            "model": provider,  # Add provider to sample for UI compatibility
                            "output": {
                                "content": provider_result.get("response", "")
                            },  # Update output with benchmark response
                        },
                        "passed": passed,
                        "score": score,
                        "reason": reason,
                        "provider_result": provider_result,
                    }
                    f.write(json.dumps(result_record, default=str) + "\n")  # type: ignore

            # Write summary record (last line)
            summary_data = {}
            for provider, stats in provider_summaries.items():
                avg_latency = (
                    stats["latency_sum"] / stats["total"] if stats["total"] > 0 else 0
                )
                pass_rate = (
                    stats["passed"] / stats["total"] if stats["total"] > 0 else 0
                )
                summary_data[provider] = {
                    "total_evaluations": stats["total"],
                    "passed": stats["passed"],
                    "errors": stats["errors"],
                    "pass_rate": pass_rate,
                    "avg_latency_ms": avg_latency,
                    "total_cost": stats["cost_sum"],
                }

            summary_record = {
                "type": "summary",
                "data": {
                    "benchmark_id": f"bench_{timestamp}_{suite_name}",
                    "timestamp": datetime.now().isoformat(),
                    "suite_name": suite_name,
                    "total_samples": len(suite_results),
                    "total_providers": len(providers),
                    "provider_summaries": summary_data,
                },
            }
            f.write(json.dumps(summary_record, default=str) + "\n")  # type: ignore

    print(f"\n{EMOJI_SAVE} Benchmark results saved to:")
    print(f"  {output_dir}")

    return output_dir
