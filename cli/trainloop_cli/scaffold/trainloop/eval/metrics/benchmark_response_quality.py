"""
Example metric that could be used for benchmarking response quality across providers.
"""

import json
from trainloop_cli.eval_core.types import Sample
from trainloop_cli.eval_core.judge import assert_true

# Define acceptable response time (e.g., under 5 seconds)
MAX_ACCEPTABLE_TIME_MS = 5000


def benchmark_response_quality(sample: Sample) -> int:
    """
    Evaluates if the response is helpful and accurate for benchmarking purposes.

    This metric can be used to compare response quality across different providers
    when running benchmarks.

    Args:
        sample: The sample containing the LLM response to evaluate

    Returns:
        1 if the response is helpful and accurate, 0 otherwise
    """
    response = sample.output.get("content", "")
    prompt = sample.input[-1].get("content", "") if sample.input else ""

    # Use LLM judge to evaluate response quality
    yes_claim = f"Given the prompt '{prompt}', the response '{response}' is helpful, accurate, and directly addresses the user's question."
    no_claim = f"Given the prompt '{prompt}', the response '{response}' is NOT helpful, accurate, or does NOT directly address the user's question."

    return assert_true(yes_claim, no_claim)


def benchmark_response_speed(sample: Sample) -> int:
    """
    Evaluates if the response was generated within acceptable time limits.

    This metric checks response metadata for timing information that might
    be captured during benchmarking.

    Args:
        sample: The sample containing response metadata

    Returns:
        1 if response time is acceptable, 0 otherwise
    """
    # Check if timing metadata exists
    response_time = sample.duration_ms

    return 1 if response_time <= MAX_ACCEPTABLE_TIME_MS else 0


def benchmark_follows_instructions(sample: Sample) -> int:
    """
    Evaluates if the model follows specific instructions in the prompt.

    Useful for benchmarking instruction-following capabilities across providers.

    Args:
        sample: The sample to evaluate

    Returns:
        1 if instructions were followed, 0 otherwise
    """
    response = sample.output.get("content", "")
    prompt = sample.input[-1].get("content", "") if sample.input else ""

    # Check for common instruction-following patterns
    if "json" in prompt.lower() and "format" in prompt.lower():
        # Check if response is valid JSON when JSON format was requested

        try:
            json.loads(response)
            return 1
        except Exception:
            return 0

    # For other cases, use the judge
    yes_claim = f"The response '{response}' correctly follows all instructions given in the prompt: '{prompt}'"
    no_claim = f"The response '{response}' does NOT follow the instructions given in the prompt: '{prompt}'"

    return assert_true(yes_claim, no_claim)
