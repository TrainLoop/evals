"""Benchmark runner logic."""

from __future__ import annotations

import time
from typing import List, Dict, Optional, Callable
from datetime import datetime

from litellm import batch_completion
from litellm.cost_calculator import completion_cost

from ...eval_core.types import Result, Sample
from .types import BenchmarkResult
from .constants import (
    OK,
    BAD,
    INFO_COLOR,
    EMOJI_GRAPH,
    EMOJI_WARNING,
    EMPHASIS_COLOR,
    RESET_COLOR,
)


def run_benchmarks(
    results: Dict[str, List[Result]],
    providers: List[str],
    metrics: Dict[str, Callable[[Sample], int]],
    max_samples: Optional[int] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> List[BenchmarkResult]:
    """Run benchmarks for all results across all providers using batching."""
    # 1. Collect all samples and create BenchmarkResult shells
    all_samples_with_results: List[Result] = []
    for suite_results in results.values():
        all_samples_with_results.extend(suite_results)

    if max_samples and len(all_samples_with_results) > max_samples:
        print(
            f"\n{INFO_COLOR}Limiting benchmark to {max_samples} samples (out of {len(all_samples_with_results)} total){RESET_COLOR}"
        )
        all_samples_with_results = all_samples_with_results[:max_samples]

    # Create a unique key for each result to map responses back
    benchmark_results_map = {
        f"{res.metric}-{res.sample.tag}-{i}": BenchmarkResult(
            original_result=res,
            provider_results={},
            timestamp=datetime.now().isoformat(),
        )
        for i, res in enumerate(all_samples_with_results)
    }

    prompts = [res.sample.input for res in all_samples_with_results]

    if not prompts:
        return []

    print(
        f"\n{EMOJI_GRAPH} Benchmarking {len(prompts)} samples across {len(providers)} providers..."
    )

    # 2. Iterate through each provider and run a batch job
    for provider in providers:
        print(
            f"  Processing provider: {EMPHASIS_COLOR}{provider}{RESET_COLOR}",
            end="",
            flush=True,
        )

        try:
            start_time = time.time()

            # Note: This uses a global max_tokens for the entire batch.
            # The per-sample model_params for max_tokens is not supported by batch_completion.
            provider_responses = batch_completion(
                model=provider,
                messages=prompts,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            end_time = time.time()
            total_latency_ms = (end_time - start_time) * 1000
            avg_latency_ms = total_latency_ms / len(prompts) if prompts else 0

            # 3. Process the batch of responses
            for i, response in enumerate(provider_responses):
                original_result = all_samples_with_results[i]
                result_key = (
                    f"{original_result.metric}-{original_result.sample.tag}-{i}"
                )

                # batch_completion can return Exceptions in the list for failed calls
                if isinstance(response, Exception):
                    provider_result_data = {
                        "response": None,
                        "latency_ms": None,
                        "cost": None,
                        "error": str(response),
                        "model_params": {
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                        "verdict": 0,  # Failed responses don't pass
                        "metric_results": {},
                    }
                else:
                    cost = completion_cost(completion_response=response, model=provider)
                    response_content = response.choices[0].message.content
                    
                    # Create a new Sample with the benchmark response
                    benchmark_sample = Sample(
                        duration_ms=int(avg_latency_ms),
                        tag=original_result.sample.tag,
                        input=original_result.sample.input,
                        output={"content": response_content},  # New response from benchmark
                        model=provider,
                        model_params={
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                        start_time_ms=int(start_time * 1000),
                        end_time_ms=int(end_time * 1000),
                        url=original_result.sample.url,
                        location=original_result.sample.location,
                    )
                    
                    # Evaluate the response using the original metric
                    metric_name = original_result.metric
                    metric_func = metrics.get(metric_name)
                    verdict = 0
                    metric_results = {}
                    
                    if metric_func:
                        try:
                            verdict = metric_func(benchmark_sample)
                            metric_results[metric_name] = {
                                "passed": verdict,
                                "error": None
                            }
                        except Exception as e:
                            verdict = 0
                            metric_results[metric_name] = {
                                "passed": 0,
                                "error": str(e)
                            }
                    else:
                        # If metric not found, log warning
                        print(f"    {EMOJI_WARNING} Metric '{metric_name}' not found in loaded metrics")
                    
                    provider_result_data = {
                        "response": response_content,
                        "latency_ms": int(avg_latency_ms),
                        "cost": cost,
                        "error": None,
                        "model_params": {
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                        "verdict": verdict,
                        "metric_results": metric_results,
                    }

                benchmark_results_map[result_key].provider_results[
                    provider
                ] = provider_result_data

            print(f" - {OK} Done")

        except Exception as e:
            print(f" - {BAD} Batch call failed: {e}")
            # Populate all results for this provider with the batch-level error
            for i, original_result in enumerate(all_samples_with_results):
                result_key = (
                    f"{original_result.metric}-{original_result.sample.tag}-{i}"
                )
                benchmark_results_map[result_key].provider_results[provider] = {
                    "response": None,
                    "latency_ms": None,
                    "cost": None,
                    "error": str(e),
                    "model_params": {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    "verdict": 0,
                    "metric_results": {},
                }

    return list(benchmark_results_map.values())