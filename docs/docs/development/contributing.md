# Contributing Guide

Welcome to the TrainLoop Evals project! We're excited to have you contribute to our comprehensive LLM evaluation framework. This guide will help you get started with contributing to the project.

## Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up your development environment** (see [Local Development](./local-development.md))
4. **Make your changes** following our [Code Style](./code-style.md)
5. **Test your changes** using our [Testing Guide](./testing.md)
6. **Submit a pull request** following our [Pull Request Process](./pull-request-process.md)

## Project Overview

TrainLoop Evals is a multi-component system consisting of:

- **CLI Tool** (`cli/`) - Python-based evaluation engine with commands for initialization, evaluation, and studio launch
- **Studio UI** (`ui/`) - Next.js web interface for data visualization and analysis
- **Multi-language SDKs** - Python (`sdk/python/`), TypeScript (`sdk/typescript/`), and Go (`sdk/go/`) instrumentation libraries
- **Registry System** (`registry/`) - Shareable metrics and evaluation suites with Python-based config discovery

For detailed architecture information, see our [Architecture Guide](./architecture.md).

## Ways to Contribute

### Code Contributions

#### Bug Fixes
- Check existing [issues](https://github.com/TrainLoop/trainloop-evals/issues) for bug reports
- Follow the [bug reproduction template](https://github.com/TrainLoop/trainloop-evals/issues/new?template=bug_report.md)
- Include tests that verify the fix

#### New Features
- Open a [feature request](https://github.com/TrainLoop/trainloop-evals/issues/new?template=feature_request.md) first
- Discuss the approach with maintainers
- Implement with comprehensive tests and documentation

#### SDK Enhancements
- Add support for new LLM providers or HTTP libraries
- Improve instrumentation accuracy or performance
- Add new language SDK implementations

#### UI Improvements
- Enhance data visualization components
- Add new chart types or dashboard features
- Improve user experience and accessibility

### Documentation Contributions

- Fix typos or improve clarity in existing documentation
- Add new guides or examples
- Update API documentation
- Create video tutorials or blog posts

### Testing Contributions

- Add missing test coverage
- Create integration tests for new scenarios
- Improve test performance or reliability
- Add load testing or benchmarking

## Development Workflow

### Getting Started

1. **Prerequisites**
   - Python 3.9+ with Poetry
   - Node.js 20.0+ with npm
   - Go 1.21+ (for Go SDK development)
   - Git

2. **Setup**
   ```bash
   git clone https://github.com/YOUR_USERNAME/trainloop-evals.git
   cd trainloop-evals
   ```

3. **Install dependencies**
   ```bash
   # CLI dependencies
   cd cli && poetry install
   
   # SDK dependencies
   cd ../sdk/python && poetry install
   
   # UI dependencies
   cd ../../ui && npm install
   
   # Return to root
   cd ..
   ```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow our [Code Style](./code-style.md) guidelines
   - Write tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   task test
   
   # Run specific test suites
   task test:cli
   task test:sdk
   task test:ui
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new evaluation metric for response quality"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test improvements
   - `refactor:` for code refactoring
   - `perf:` for performance improvements

## Code Quality Standards

### Testing Requirements

- **Unit tests** for all new functions and methods
- **Integration tests** for component interactions
- **End-to-end tests** for user workflows
- **Performance tests** for critical paths

### Code Review Process

1. All code changes require review from at least one maintainer
2. Automated tests must pass
3. Code style checks must pass
4. Documentation must be updated for user-facing changes

### Performance Considerations

- Keep CLI commands responsive (< 2 seconds for common operations)
- Minimize SDK overhead on instrumented applications
- Optimize UI rendering for large datasets
- Use appropriate caching strategies

## Contributing to Different Components

### CLI Development

The CLI is built with Python using Click framework:

- **Location**: `cli/trainloop_cli/`
- **Commands**: `init`, `eval`, `studio`, `add`, `benchmark`
- **Testing**: Use `pytest` with markers for different test types
- **Key files**: 
  - `cli/trainloop_cli/commands/` - Command implementations
  - `cli/trainloop_cli/eval_core/` - Core evaluation logic

### SDK Development

#### Python SDK
- **Location**: `sdk/python/trainloop_llm_logging/`
- **Focus**: Zero-touch HTTP instrumentation
- **Key files**:
  - `instrumentation/` - HTTP library patches
  - `store.py` - Data persistence
  - `register.py` - Registration API

#### TypeScript SDK
- **Location**: `sdk/typescript/src/`
- **Focus**: Node.js HTTP instrumentation
- **Key files**:
  - `instrumentation/` - HTTP and fetch patches
  - `store.ts` - Data persistence
  - `config.ts` - Configuration management

#### Go SDK
- **Location**: `sdk/go/trainloop-llm-logging/`
- **Focus**: Go HTTP instrumentation
- **Key files**:
  - `instrumentation/` - HTTP transport wrapping
  - `internal/store/` - Data persistence
  - `internal/config/` - Configuration

### UI Development

The Studio UI is built with Next.js 15 and React 18:

- **Location**: `ui/`
- **Framework**: Next.js with App Router
- **Database**: DuckDB for local data querying
- **UI Components**: shadcn/ui with Tailwind CSS
- **Key directories**:
  - `app/` - Next.js app routes
  - `components/` - React components
  - `database/` - DuckDB integration

### Registry Development

The registry system enables sharing of metrics and suites:

- **Location**: `registry/`
- **Configuration**: Python-based `config.py` files
- **Discovery**: Type-safe component discovery
- **Key files**:
  - `metrics/` - Shareable metrics
  - `suites/` - Evaluation suites
  - `config_types.py` - Configuration types

## Documentation Guidelines

### Writing Style

- Use clear, concise language
- Include practical examples
- Provide step-by-step instructions
- Add troubleshooting sections where relevant

### Code Examples

```python
# Good: Include context and explain the example
from trainloop_llm_logging import collect

# Initialize TrainLoop logging for your application
collect("./trainloop/trainloop.config.yaml")

# Your LLM calls will now be automatically logged
```

### API Documentation

- Document all public functions and classes
- Include parameter types and return values
- Provide usage examples
- Note any breaking changes

## Community Guidelines

### Communication

- Be respectful and inclusive
- Ask questions in [GitHub Discussions](https://github.com/TrainLoop/trainloop-evals/discussions)
- Use [GitHub Issues](https://github.com/TrainLoop/trainloop-evals/issues) for bugs and feature requests
- Join our community channels for real-time discussion

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/). Please be respectful and professional in all interactions.

## Getting Help

### For Contributors

- **Development questions**: Open a [GitHub Discussion](https://github.com/TrainLoop/trainloop-evals/discussions)
- **Bug reports**: Use the [bug report template](https://github.com/TrainLoop/trainloop-evals/issues/new?template=bug_report.md)
- **Feature requests**: Use the [feature request template](https://github.com/TrainLoop/trainloop-evals/issues/new?template=feature_request.md)

### For Maintainers

- **Review guidelines**: See [Pull Request Process](./pull-request-process.md)
- **Release process**: See [Release Process](./release-process.md)
- **Governance**: See [Governance](./governance.md)

## Resources

- **[Architecture Guide](./architecture.md)** - System design and component interaction
- **[Local Development](./local-development.md)** - Development environment setup
- **[Testing Guide](./testing.md)** - Test framework and practices
- **[Code Style](./code-style.md)** - Coding standards and conventions
- **[API Reference](../reference/)** - Detailed API documentation

## License

By contributing to TrainLoop Evals, you agree that your contributions will be licensed under the [MIT License](https://github.com/TrainLoop/trainloop-evals/blob/main/LICENSE).

---

Thank you for contributing to TrainLoop Evals! Your contributions help make LLM evaluation more accessible and effective for the entire community.