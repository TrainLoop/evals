"""Output and display functions for benchmark results."""

from __future__ import annotations

from typing import List

from .types import BenchmarkResult
from .constants import (
    OK,
    BAD,
    HEADER_COLOR,
    EMPHASIS_COLOR,
    RESET_COLOR,
)


def print_benchmark_summary(
    benchmark_results: List[BenchmarkResult], providers: List[str]
):
    """Print a summary of the benchmark results."""
    print(f"\n{HEADER_COLOR}--- Benchmark Summary ---{RESET_COLOR}")

    # Calculate statistics per provider
    provider_stats = {
        provider: {
            "total": 0,
            "success": 0,
            "errors": 0,
            "avg_latency_ms": 0,
            "total_cost": 0.0,
        }
        for provider in providers
    }

    for result in benchmark_results:
        for provider, provider_result in result.provider_results.items():
            stats = provider_stats[provider]
            stats["total"] += 1

            if provider_result["error"] is None:
                stats["success"] += 1
                if provider_result["latency_ms"]:
                    stats["avg_latency_ms"] += provider_result["latency_ms"]
                if provider_result["cost"]:
                    stats["total_cost"] += provider_result["cost"]
            else:
                stats["errors"] += 1

    # Calculate averages
    for provider, stats in provider_stats.items():
        if stats["success"] > 0:
            stats["avg_latency_ms"] = stats["avg_latency_ms"] / stats["success"]

    # Print provider statistics
    print(f"\n{EMPHASIS_COLOR}Provider Performance:{RESET_COLOR}")
    print(
        f"{'Provider':<30} {'Success Rate':<15} {'Avg Latency':<15} {'Total Cost':<15}"
    )
    print("-" * 75)

    for provider, stats in provider_stats.items():
        success_rate = f"{stats['success']}/{stats['total']}"
        avg_latency = (
            f"{stats['avg_latency_ms']:.0f}ms" if stats["avg_latency_ms"] > 0 else "N/A"
        )
        total_cost = f"${stats['total_cost']:.4f}" if stats["total_cost"] > 0 else "N/A"

        status = OK if stats["errors"] == 0 else BAD
        print(
            f"{provider:<30} {status} {success_rate:<13} {avg_latency:<15} {total_cost:<15}"
        )

    print("-" * 75)