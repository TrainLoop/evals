---
sidebar_position: 1
---

# Reference

This section contains detailed API documentation and reference materials for TrainLoop Evals.

## CLI Reference

### Commands
- **[CLI Overview](./cli/overview.md)** - Complete CLI command reference
- **[trainloop init](./cli/init.md)** - Initialize a new evaluation workspace
- **[trainloop eval](./cli/eval.md)** - Run evaluation suites
- **[trainloop studio](./cli/studio.md)** - Launch the Studio UI
- **[trainloop add](./cli/add.md)** - Add metrics and suites from registry
- **[trainloop benchmark](./cli/benchmark.md)** - Compare multiple LLM providers

### Configuration
- **[trainloop.config.yaml](./cli/config.md)** - Configuration file reference
- **[Environment Variables](./cli/env-vars.md)** - Environment variable reference

### Technical Specifications
- **[Benchmark Schema](./benchmark-schema.md)** - Data schema for benchmark results

## SDK Reference

### Python SDK
- **[API Reference](./sdk/python/api.md)** - Complete Python API documentation
- **[Configuration](./sdk/python/config.md)** - Python SDK configuration
- **[Types](./sdk/python/types.md)** - Type definitions and interfaces

### TypeScript SDK
- **[API Reference](./sdk/typescript/api.md)** - Complete TypeScript API documentation
- **[Configuration](./sdk/typescript/config.md)** - TypeScript SDK configuration
- **[Types](./sdk/typescript/types.md)** - Type definitions and interfaces

### Go SDK
- **[API Reference](./sdk/go/api.md)** - Complete Go API documentation
- **[Configuration](./sdk/go/config.md)** - Go SDK configuration
- **[Types](./sdk/go/types.md)** - Type definitions and interfaces

## Evaluation System

### Metrics
- **[Metric API](./evaluation/metrics.md)** - Writing custom metrics
- **[Built-in Metrics](./evaluation/builtin-metrics.md)** - Available metrics
- **[Metric Registry](./evaluation/registry.md)** - Metric discovery and management

### Test Suites
- **[Suite API](./evaluation/suites.md)** - Creating test suites
- **[Suite Configuration](./evaluation/suite-config.md)** - Suite configuration options
- **[Suite Registry](./evaluation/suite-registry.md)** - Suite discovery and management

### LLM Judge
- **[Judge API](./evaluation/judge.md)** - LLM judge functionality
- **[Judge Configuration](./evaluation/judge-config.md)** - Judge configuration options
- **[Judge Prompts](./evaluation/judge-prompts.md)** - Customizing judge prompts

## Studio UI

### API Endpoints
- **[Events API](./studio/events.md)** - Event data endpoints
- **[Results API](./studio/results.md)** - Evaluation results endpoints
- **[Benchmarks API](./studio/benchmarks.md)** - Benchmark data endpoints

### Database Schema
- **[DuckDB Schema](./studio/schema.md)** - Database schema reference
- **[Data Types](./studio/data-types.md)** - Data type definitions

## Data Formats

### File Formats
- **[Event Format](./data/events.md)** - LLM event JSONL format
- **[Result Format](./data/results.md)** - Evaluation result format
- **[Benchmark Format](./data/benchmarks.md)** - Benchmark data format

### Registry Formats
- **[Metric Config](./data/metric-config.md)** - Metric configuration format
- **[Suite Config](./data/suite-config.md)** - Suite configuration format

## Integration

### Cloud Storage
- **[S3 Integration](./integration/s3.md)** - Amazon S3 setup
- **[GCS Integration](./integration/gcs.md)** - Google Cloud Storage setup
- **[Azure Integration](./integration/azure.md)** - Azure Blob Storage setup

### CI/CD
- **[GitHub Actions](./integration/github-actions.md)** - GitHub Actions integration
- **[GitLab CI](./integration/gitlab-ci.md)** - GitLab CI integration
- **[Jenkins](./integration/jenkins.md)** - Jenkins integration

## Coming Soon

We're actively working on comprehensive reference documentation for each of these topics. Documentation will be added based on community feedback and common use cases.

## Contributing

Want to contribute to the documentation? We welcome community contributions! Please see our [Contributing Guide](https://github.com/TrainLoop/trainloop-evals/blob/main/CONTRIBUTING.md) for details.

## Questions?

If you need help with a specific API or feature:

- Check the [Guides](../guides/) for practical examples
- Review the [Explanation](../explanation/) for conceptual understanding
- [Open an issue](https://github.com/TrainLoop/trainloop-evals/issues) for questions