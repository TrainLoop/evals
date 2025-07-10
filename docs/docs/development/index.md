---
sidebar_position: 1
---

# Development Guide

This section contains information for developers who want to contribute to TrainLoop Evals or extend its functionality. Whether you're fixing bugs, adding features, or building custom integrations, this guide will help you get started.

## Getting Started

### Development Setup
- **[Local Development](./local-development.md)** - Set up your development environment
- **[Building from Source](./building-from-source.md)** - Build all components locally
- **[Testing](./testing.md)** - Run the test suite
- **[Debugging](./debugging.md)** - Debug TrainLoop components

### Contributing
- **[Contributing Guide](./contributing.md)** - How to contribute to the project
- **[Code Style](./code-style.md)** - Coding standards and conventions
- **[Pull Request Process](./pull-request-process.md)** - How to submit changes
- **[Issue Reporting](./issue-reporting.md)** - How to report bugs and request features

## Architecture

### System Overview
- **[Architecture Overview](./architecture.md)** - High-level system architecture
- **[Component Interaction](./component-interaction.md)** - How components work together
- **[Data Flow](./data-flow.md)** - Data flow through the system
- **[Technology Stack](./technology-stack.md)** - Technologies used in each component

### Core Components
- **[CLI Architecture](./cli-architecture.md)** - Command-line tool design
- **[SDK Architecture](./sdk-architecture.md)** - Multi-language SDK design
- **[Studio UI Architecture](./studio-ui-architecture.md)** - Web interface design
- **[Registry System](./registry-system.md)** - Component sharing system

## Development Workflows

### Building and Testing
- **[Build System](./build-system.md)** - Build configuration and scripts
- **[Test Framework](./test-framework.md)** - Testing infrastructure
- **[Continuous Integration](./continuous-integration.md)** - CI/CD pipeline
- **[Release Process](./release-process.md)** - How releases are made

### Development Tools
- **[Development Scripts](./development-scripts.md)** - Useful development scripts
- **[Docker Development](./docker-development.md)** - Docker-based development
- **[IDE Setup](./ide-setup.md)** - IDE configuration and recommendations
- **[Debugging Tools](./debugging-tools.md)** - Debugging and profiling tools

## Extending TrainLoop

### Custom Components
- **[Custom Metrics](./custom-metrics.md)** - Develop new evaluation metrics
- **[Custom Suites](./custom-suites.md)** - Create new evaluation suites
- **[Custom Judges](./custom-judges.md)** - Build custom LLM judges
- **[Custom Exporters](./custom-exporters.md)** - Create new data exporters

### SDK Extensions
- **[Python SDK Extensions](./python-sdk-extensions.md)** - Extend the Python SDK
- **[TypeScript SDK Extensions](./typescript-sdk-extensions.md)** - Extend the TypeScript SDK
- **[Go SDK Extensions](./go-sdk-extensions.md)** - Extend the Go SDK
- **[New Language SDKs](./new-language-sdks.md)** - Create SDKs for new languages

### UI Extensions
- **[Studio UI Plugins](./studio-ui-plugins.md)** - Create Studio UI plugins
- **[Custom Charts](./custom-charts.md)** - Add new chart types
- **[Custom Views](./custom-views.md)** - Create new data views
- **[Theme Customization](./theme-customization.md)** - Customize the UI theme

## API Development

### Internal APIs
- **[CLI Core API](./cli-core-api.md)** - Internal CLI API
- **[SDK Core API](./sdk-core-api.md)** - Internal SDK API
- **[Studio Backend API](./studio-backend-api.md)** - Studio backend API
- **[Registry API](./registry-api.md)** - Registry system API

### External Integrations
- **[LLM Provider Integration](./llm-provider-integration.md)** - Integrate new LLM providers
- **[Storage Provider Integration](./storage-provider-integration.md)** - Integrate new storage providers
- **[CI/CD Integration](./cicd-integration.md)** - Integrate with CI/CD systems
- **[Monitoring Integration](./monitoring-integration.md)** - Integrate with monitoring systems

## Performance and Optimization

### Performance Optimization
- **[Profiling](./profiling.md)** - Profile TrainLoop components
- **[Optimization Techniques](./optimization-techniques.md)** - Common optimization patterns
- **[Caching Strategies](./caching-strategies.md)** - Implement effective caching
- **[Parallel Processing](./parallel-processing.md)** - Optimize for parallel execution

### Scaling
- **[Horizontal Scaling](./horizontal-scaling.md)** - Scale across multiple machines
- **[Vertical Scaling](./vertical-scaling.md)** - Scale up individual components
- **[Load Testing](./load-testing.md)** - Test system under load
- **[Capacity Planning](./capacity-planning.md)** - Plan for growth

## Security

### Security Considerations
- **[Security Model](./security-model.md)** - TrainLoop security model
- **[Data Privacy](./data-privacy.md)** - Handling sensitive data
- **[API Security](./api-security.md)** - Secure API design
- **[Dependency Security](./dependency-security.md)** - Secure dependency management

### Security Best Practices
- **[Secure Development](./secure-development.md)** - Secure coding practices
- **[Security Testing](./security-testing.md)** - Test for security vulnerabilities
- **[Vulnerability Management](./vulnerability-management.md)** - Handle security issues
- **[Security Auditing](./security-auditing.md)** - Audit security practices

## Documentation

### Documentation Development
- **[Documentation Standards](./documentation-standards.md)** - Documentation style guide
- **[Writing Guidelines](./writing-guidelines.md)** - Writing effective documentation
- **[Documentation Tools](./documentation-tools.md)** - Tools for documentation
- **[Translation](./translation.md)** - Internationalization and localization

### API Documentation
- **[API Documentation Generation](./api-documentation-generation.md)** - Generate API docs
- **[OpenAPI Specifications](./openapi-specifications.md)** - OpenAPI spec management
- **[SDK Documentation](./sdk-documentation.md)** - SDK documentation standards
- **[Example Management](./example-management.md)** - Manage code examples

## Community

### Community Development
- **[Community Guidelines](./community-guidelines.md)** - Community interaction guidelines
- **[Maintainer Guide](./maintainer-guide.md)** - Guide for project maintainers
- **[Governance](./governance.md)** - Project governance model
- **[Roadmap](./roadmap.md)** - Development roadmap

### Support and Help
- **[Support Channels](./support-channels.md)** - Where to get help
- **[FAQ for Developers](./developer-faq.md)** - Frequently asked questions
- **[Resources](./resources.md)** - Useful development resources
- **[Learning Materials](./learning-materials.md)** - Educational content

## Coming Soon

We're actively working on comprehensive development documentation. Content will be added based on community contributions and development needs.

## Contributing to This Guide

Want to improve this development guide? We welcome contributions! Please see our [Contributing Guide](https://github.com/TrainLoop/trainloop-evals/blob/main/CONTRIBUTING.md) for details.

## Questions?

If you have development questions:

- Check the [API Reference](../reference/) for detailed specifications
- Review the [Guides](../guides/) for practical examples
- [Open an issue](https://github.com/TrainLoop/trainloop-evals/issues) for development questions
- Join our community discussions for real-time help