from registry.config_types import MetricConfig

config = MetricConfig(
    name="is_helpful",
    description="Metric using the TrainLoop judge to evaluate response helpfulness.",
    min_version="0.1.0",
    dependencies=[],
    author="TrainLoop Team",
    tags=["judge", "helpfulness"],
)
