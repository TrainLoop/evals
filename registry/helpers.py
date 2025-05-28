"""Helper stubs for TrainLoop registry components."""

from __future__ import annotations
from typing import Callable, List
from .types import Sample, Result


class Tag:
    """Stub for tag-based metric checking."""

    def __init__(self, samples: List[Sample]):
        self.samples = samples

    def check(
        self, *metrics: Callable[[Sample], int], workers: int | None = None
    ) -> List[Result]:
        """Apply metrics to samples matching the tag."""
        # This is a stub - actual implementation would run metrics
        _ = (metrics, workers)  # Mark as intentionally unused
        return []


def tag(name: str, raw: bool = False) -> Tag | List[Sample]:
    """Create a tag-based checker for applying metrics."""
    # This is a stub - actual implementation would load samples
    _ = (name, raw)  # Mark as intentionally unused
    return Tag([])
