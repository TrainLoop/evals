from registry.config_types import SuiteConfig

config = SuiteConfig(
    name="is_helpful",
    description="A suite that uses the is_helpful metric to evaluate responses tagged with 'my-tag'.",
    min_version="0.1.0",
    dependencies=["is_helpful"],  # Refers to the 'is_helpful' metric
    author="TrainLoop Team",
    tags=["helpfulness", "example"],
)
