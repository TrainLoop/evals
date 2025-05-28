# TrainLoop Registry

This directory contains pre-built metrics and suites that can be installed using the `trainloop add` command.

## Structure

```
registry/
├── config_types.py         # Type definitions for configs
├── metrics/
│   ├── index.py            # Auto-generated list of available metrics
│   └── {metric_name}/
│       ├── config.py       # Metric metadata and configuration
│       └── {metric_name}.py # Metric implementation
└── suites/
    ├── index.py            # Auto-generated list of available suites
    └── {suite_name}/
        ├── config.py       # Suite metadata and dependencies
        └── {suite_name}.py # Suite implementation
```

## Adding a New Metric

1. Create a new directory under `registry/metrics/` with your metric name
2. Add `config.py`:
   ```python
   from registry.config_types import MetricConfig

   config = MetricConfig(
       name="your_metric_name",
       description="What this metric does",
       min_version="0.5.0",  # Minimum CLI version required
       dependencies=[],      # Other metrics this depends on
       author="Your Name",
       tags=["category", "purpose"],
   )
   ```
3. Add `{metric_name}.py` with your implementation
4. The metric will automatically appear in the index (no manual updates needed!)

## Adding a New Suite

1. Create a new directory under `registry/suites/` with your suite name
2. Add `config.py`:
   ```python
   from registry.config_types import SuiteConfig

   config = SuiteConfig(
       name="your_suite_name",
       description="What this suite tests",
       min_version="0.5.0",
       dependencies=["metric_one", "metric_two"],  # Required metrics
       author="Your Name",
       tags=["category", "use_case"],
   )
   ```
3. Add `{suite_name}.py` with your suite definition
4. The suite will automatically appear in the index (no manual updates needed!)

## Usage

Users can install components using:

```bash
# Install a metric
trainloop add metric always_pass

# Install a suite (and its dependencies)
trainloop add suite sample

# List available components
trainloop add metric --list
trainloop add suite --list

# Force overwrite existing components
trainloop add metric always_pass --force

# Use a specific version
trainloop add metric always_pass --version 0.4.0
```

## Version Compatibility

The `min_version` field in config ensures that components are only installed on compatible CLI versions. This prevents users from installing components that rely on features not available in their version.

## Best Practices

1. Keep metrics focused on a single concern
2. Metrics must return a reward between 0 and 1, where 1 is a pass and 0 is a fail
3. Suites must return an array of Result objects
4. Include meaningful error messages
5. Use descriptive names that indicate what the metric/suite tests. Check for existing names to avoid conflicts.
6. Use type hints for better IDE support and validation
