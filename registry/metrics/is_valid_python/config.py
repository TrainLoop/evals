"""Configuration for the is_valid_python metric."""

from registry.config_types import MetricConfig

config = MetricConfig(
    name="is_valid_python",
    description="Deterministic evaluation metric that verifies Python syntax and AST validity in model outputs.",
    min_version="0.5.0",
    dependencies=[],
    author="TrainLoop Team",
    tags=["code", "python", "syntax", "ast", "deterministic"],
)
