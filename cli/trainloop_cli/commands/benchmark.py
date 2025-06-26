"""TrainLoop CLI - `benchmark` command."""

from __future__ import annotations

import sys
import os
import json
import time
import importlib
import pkgutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
import litellm
from litellm.cost_calculator import completion_cost
from litellm import batch_completion
import yaml
from dotenv import load_dotenv

from .utils import find_root, load_config_for_cli
from ..eval_core.types import Result, Sample


# ANSI helpers for console output
OK = "\033[32m✓\033[0m"
BAD = "\033[31m✗\033[0m"
INFO_COLOR = "\033[94m"
HEADER_COLOR = "\033[95m"
EMPHASIS_COLOR = "\033[93m"
RESET_COLOR = "\033[0m"

EMOJI_ROCKET = "🚀"
EMOJI_GRAPH = "📊"
EMOJI_SAVE = "💾"
EMOJI_CHECK = "✅"
EMOJI_WARNING = "⚠️"


@dataclass
class BenchmarkResult:
    """Result of benchmarking a single evaluation result across providers."""

    original_result: Result
    provider_results: Dict[
        str, Dict[str, Any]
    ]  # provider -> {verdict, latency_ms, cost, error}
    timestamp: str


def _load_metrics(project_root: Path) -> Dict[str, Callable[[Sample], int]]:
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
                if callable(attr) and not attr_name.startswith('_'):
                    # Store the metric function
                    metrics_dict[attr_name] = attr
        except Exception as e:
            print(f"Warning: Could not load metric module {info.name}: {e}")
    
    return metrics_dict


def _load_latest_results(project_root: Path) -> Dict[str, List[Result]]:
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


def _load_benchmark_config(project_root: Path) -> Dict[str, Any]:
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


def _validate_provider_keys(providers: List[str]) -> List[str]:
    """Validate that API keys exist for each provider."""
    valid_providers = []
    missing_keys = []

    # Map of provider prefixes to environment variable names
    provider_key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "cohere": "COHERE_API_KEY",
        "google": "GEMINI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "together": "TOGETHER_API_KEY",
        "anyscale": "ANYSCALE_API_KEY",
        "perplexity": "PERPLEXITY_API_KEY",
        "deepinfra": "DEEPINFRA_API_KEY",
        "replicate": "REPLICATE_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
        "azure": "AZURE_API_KEY",
        "bedrock": "AWS_ACCESS_KEY_ID",  # Also needs AWS_SECRET_ACCESS_KEY
    }

    for provider in providers:
        # Extract provider name from model string (e.g., "openai/gpt-4" -> "openai")
        provider_prefix = provider.split("/")[0].lower()

        if provider_prefix in provider_key_map:
            env_var = provider_key_map[provider_prefix]
            if os.environ.get(env_var):
                valid_providers.append(provider)
            else:
                missing_keys.append(f"{provider} (missing {env_var})")
        else:
            # For unknown providers, assume they're valid and let LiteLLM handle it
            valid_providers.append(provider)

    if missing_keys:
        print(f"\n{EMOJI_WARNING} Missing API keys for providers:")
        for missing in missing_keys:
            print(f"  {BAD} {missing}")
        print(
            f"\n{INFO_COLOR}Please set the required environment variables or update your .env file.{RESET_COLOR}"
        )

    return valid_providers


def _run_benchmarks(
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


def _save_benchmark_results(
    benchmark_results: List[BenchmarkResult], project_root: Path, providers: List[str]
) -> Path:
    """Save benchmark results to a timestamped directory."""
    benchmark_dir = project_root / "data" / "benchmarks"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = benchmark_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

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

        with results_file.open("w") as f:
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
            f.write(json.dumps(metadata_record) + "\n")

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
                                if not metric_result.get("passed") and metric_result.get("error"):
                                    reason = f"Metric '{metric_name}' error: {metric_result['error']}"
                                    break
                            if not reason:
                                reason = f"Failed {result.original_result.metric} evaluation"
                    
                    result_record = {
                        "type": "result",
                        "metric": result.original_result.metric,
                        "sample": {
                            **asdict(result.original_result.sample),
                            "model": provider,  # Add provider to sample for UI compatibility
                            "output": {"content": provider_result.get("response", "")},  # Update output with benchmark response
                        },
                        "passed": passed,
                        "score": score,
                        "reason": reason,
                        "provider_result": provider_result,
                    }
                    f.write(json.dumps(result_record, default=str) + "\n")

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
            f.write(json.dumps(summary_record, default=str) + "\n")

    print(f"\n{EMOJI_SAVE} Benchmark results saved to:")
    print(f"  {output_dir}")

    return output_dir


def _print_benchmark_summary(
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


def benchmark_command() -> None:
    """
    Run benchmarks comparing multiple LLM providers on evaluation results.

    This command:
    1. Loads the latest evaluation results
    2. Reads benchmark configuration from trainloop.config.yaml
    3. Validates provider API keys
    4. Runs the same prompts through multiple providers
    5. Saves comparison results for analysis
    """
    litellm.suppress_debug_info = True
    # Disable async callbacks to prevent pending task warnings
    litellm.callbacks = []
    # Disable litellm's request timeout to prevent session issues
    os.environ["LITELLM_REQUEST_TIMEOUT"] = "600"
    os.environ["LITELLM_LOG"] = "ERROR"

    try:
        # Find project root
        project_root_path = find_root()
        if project_root_path is None:
            raise RuntimeError(
                "Project root could not be determined. Ensure 'trainloop.config.yaml' exists in the project hierarchy."
            )
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Ensure you are in a TrainLoop project directory (or a subdirectory).")
        sys.exit(1)

    # Load project configuration
    load_config_for_cli(project_root_path)

    print(
        f"{EMOJI_ROCKET} {HEADER_COLOR}TrainLoop Benchmark:{RESET_COLOR} Comparing LLM providers for project {project_root_path}"
    )
    print("-" * 40)

    # Load latest evaluation results
    results = _load_latest_results(project_root_path)
    if not results:
        print(
            f"\n{BAD} No evaluation results found. Run 'trainloop eval' first to generate results."
        )
        sys.exit(1)

    # Load benchmark configuration
    benchmark_config = _load_benchmark_config(project_root_path)

    # Get providers from config or use defaults
    provider_configs = benchmark_config.get("providers", [])

    # Convert provider configs to model strings
    providers = []
    if provider_configs:
        for provider_conf in provider_configs:
            if isinstance(provider_conf, dict):
                provider_name = provider_conf.get("name", "")
                models = provider_conf.get("models", [])
                for model in models:
                    providers.append(f"{provider_name}/{model}")
            elif isinstance(provider_conf, str):
                # Support simple string format as well
                providers.append(provider_conf)
    else:
        # Default providers if none configured
        providers = [
            "openai/gpt-4",
            "anthropic/claude-3-sonnet-20240229",
            "gemini/gemini-2.0-flash",
        ]

    max_samples = benchmark_config.get("max_samples", None)
    temperature = benchmark_config.get("temperature", 0.7)
    max_tokens = benchmark_config.get("max_tokens", 1000)

    print(f"\n{INFO_COLOR}Benchmark Configuration:{RESET_COLOR}")
    print(f"  Providers: {', '.join(providers)}")
    if max_samples:
        print(f"  Max samples: {max_samples}")
    print(f"  Temperature: {temperature}")
    print(f"  Max tokens: {max_tokens}")

    # Validate API keys
    valid_providers = _validate_provider_keys(providers)
    if not valid_providers:
        print(f"\n{BAD} No providers with valid API keys found. Cannot run benchmark.")
        sys.exit(1)

    if len(valid_providers) < len(providers):
        print(
            f"\n{EMOJI_WARNING} Running benchmark with {len(valid_providers)} out of {len(providers)} providers"
        )

    # Load metrics for evaluation
    print(f"\n{INFO_COLOR}Loading evaluation metrics...{RESET_COLOR}")
    metrics = _load_metrics(project_root_path)
    if metrics:
        print(f"  {OK} Loaded {len(metrics)} metric(s): {', '.join(metrics.keys())}")
    else:
        print(f"  {EMOJI_WARNING} No metrics found - results will use pass-through evaluation")

    # Run benchmarks
    print(
        f"\n{EMOJI_GRAPH} Starting benchmark across {len(valid_providers)} providers..."
    )

    try:
        benchmark_results = _run_benchmarks(
            results, valid_providers, metrics, max_samples, temperature, max_tokens
        )
    except Exception as e:
        print(f"\n{BAD} Error during benchmarking: {e}")
        sys.exit(1)

    if not benchmark_results:
        print(f"\n{BAD} No benchmark results generated.")
        sys.exit(1)

    # Save results (directory is printed by _save_benchmark_results)
    _ = _save_benchmark_results(benchmark_results, project_root_path, valid_providers)

    # Print summary
    _print_benchmark_summary(benchmark_results, valid_providers)

    print(f"\n{EMOJI_CHECK} Benchmark complete!")

    sys.exit(0)
