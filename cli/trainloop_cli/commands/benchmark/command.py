"""Main benchmark command implementation."""

from __future__ import annotations

import sys
import os
import litellm

from ..utils import find_root, load_config_for_cli
from .constants import (
    BAD,
    OK,
    INFO_COLOR,
    HEADER_COLOR,
    EMOJI_ROCKET,
    EMOJI_GRAPH,
    EMOJI_CHECK,
    EMOJI_WARNING,
    RESET_COLOR,
    DEFAULT_PROVIDERS,
)
from .loaders import load_latest_results, load_benchmark_config, load_metrics
from .validators import validate_provider_keys
from .runner import run_benchmarks
from .storage import save_benchmark_results
from .output import print_benchmark_summary


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
    results = load_latest_results(project_root_path)
    if not results:
        print(
            f"\n{BAD} No evaluation results found. Run 'trainloop eval' first to generate results."
        )
        sys.exit(1)

    # Load benchmark configuration
    benchmark_config = load_benchmark_config(project_root_path)

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
        providers = DEFAULT_PROVIDERS

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
    valid_providers = validate_provider_keys(providers)
    if not valid_providers:
        print(f"\n{BAD} No providers with valid API keys found. Cannot run benchmark.")
        sys.exit(1)

    if len(valid_providers) < len(providers):
        print(
            f"\n{EMOJI_WARNING} Running benchmark with {len(valid_providers)} out of {len(providers)} providers"
        )

    # Load metrics for evaluation
    print(f"\n{INFO_COLOR}Loading evaluation metrics...{RESET_COLOR}")
    metrics = load_metrics(project_root_path)
    if metrics:
        print(f"  {OK} Loaded {len(metrics)} metric(s): {', '.join(metrics.keys())}")
    else:
        print(f"  {EMOJI_WARNING} No metrics found - results will use pass-through evaluation")

    # Run benchmarks
    print(
        f"\n{EMOJI_GRAPH} Starting benchmark across {len(valid_providers)} providers..."
    )

    try:
        benchmark_results = run_benchmarks(
            results, valid_providers, metrics, max_samples, temperature, max_tokens
        )
    except Exception as e:
        print(f"\n{BAD} Error during benchmarking: {e}")
        sys.exit(1)

    if not benchmark_results:
        print(f"\n{BAD} No benchmark results generated.")
        sys.exit(1)

    # Save results (directory is printed by save_benchmark_results)
    _ = save_benchmark_results(benchmark_results, project_root_path, valid_providers)

    # Print summary
    print_benchmark_summary(benchmark_results, valid_providers)

    print(f"\n{EMOJI_CHECK} Benchmark complete!")

    sys.exit(0)