"""Type stubs for TrainLoop registry components."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Dict, Literal


@dataclass(slots=True, frozen=True)
class Sample:
    """Represents a sample for evaluation.
    
    This matches the actual Sample type from trainloop eval types.
    """
    duration_ms: int  # Duration of the request in milliseconds
    tag: str  # The tag of the event
    input: List[Dict[str, str]]  # Input(s) to the model
    output: Dict[Literal["content"], str]  # Output(s) from the model
    model: str  # The model used to generate the response
    model_params: Dict[str, Any]  # Model parameters
    start_time_ms: int  # Start time in milliseconds since epoch
    end_time_ms: int  # End time in milliseconds since epoch
    url: str  # The request URL
    location: Dict[Literal["tag", "lineNumber"], str]  # Location information


@dataclass(slots=True, frozen=False)
class Result:
    """Represents a metric evaluation result."""
    metric: str  # The name of the metric
    sample: Sample  # The sample that was evaluated
    passed: int  # 1 or 0
    reason: str | None = None  # The reason for the failure (if any)
