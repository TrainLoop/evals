"""Configuration for the sample suite."""

from registry.config_types import SuiteConfig

config = SuiteConfig(
    name="sample",
    description="A sample evaluation suite demonstrating how to test LLM behavior",
    min_version="0.5.0",
    dependencies=["always_pass"],
    author="TrainLoop Team",
    tags=["example", "starter"],
)
