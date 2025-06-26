"""Type definitions for benchmark command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from ...eval_core.types import Result


@dataclass
class BenchmarkResult:
    """Result of benchmarking a single evaluation result across providers."""

    original_result: Result
    provider_results: Dict[
        str, Dict[str, Any]
    ]  # provider -> {verdict, latency_ms, cost, error}
    timestamp: str