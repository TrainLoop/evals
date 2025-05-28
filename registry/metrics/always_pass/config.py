"""Configuration for the always_pass metric."""

from registry.config_types import MetricConfig

config = MetricConfig(
    name="always_pass",
    description="A simple metric that always returns a passing verdict",
    min_version="0.5.0",
    dependencies=[],
    author="TrainLoop Team",
    tags=["testing", "basic"],
)
