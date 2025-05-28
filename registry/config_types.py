"""Configuration types for registry components."""

from dataclasses import dataclass
from typing import List


@dataclass
class MetricConfig:
    """Configuration for a metric."""

    name: str
    description: str
    min_version: str
    dependencies: List[str] = None
    author: str = "TrainLoop Team"
    tags: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


@dataclass
class SuiteConfig:
    """Configuration for a suite."""

    name: str
    description: str
    min_version: str
    dependencies: List[str]  # Required for suites - these are metric names
    author: str = "TrainLoop Team"
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
