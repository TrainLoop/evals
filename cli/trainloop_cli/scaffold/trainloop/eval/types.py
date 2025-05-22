"""
TrainLoop evaluation types - core data classes for samples and results.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
from typing import TypedDict, List, Dict


class CollectedSampleDict(TypedDict, total=False):
    durationMs: int
    tag: str
    input: List[Dict[str, str]]
    output: Dict[Literal["content"], str]
    model: str
    modelParams: Dict[str, Any]
    startTimeMs: int
    endTimeMs: int
    url: str
    location: Dict[Literal["tag", "lineNumber"], str]


@dataclass(slots=True, frozen=True)
class Sample:
    duration_ms: int  # Duration of the request in milliseconds
    tag: str  # The tag of the event
    input: List[Dict[str, str]]  # Input(s) to the model
    output: Dict[Literal["content"], str]  # Output(s) from the model
    model: str  # The model used to generate the response
    model_params: Dict[str, Any]  # Model parameters
    start_time_ms: int  # Start time in milliseconds since epoch
    end_time_ms: int  # End time in milliseconds since epoch
    url: str  # The request URL
    location: Dict[
        Literal["tag", "lineNumber"], str
    ]  # Location information (tag, lineNumber)


@dataclass(slots=True, frozen=False)
class Result:
    metric: str  # The name of the metric
    sample: Sample  # The sample that was evaluated
    passed: int  # 1 or 0
    reason: str | None = None  # The reason for the failure (if any)
