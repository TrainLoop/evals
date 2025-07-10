# Contributing to TrainLoop Evals

Thank you for your interest in contributing to TrainLoop Evals! This document provides a quick overview to get you started.

## 📚 **Complete Contributing Guide**

For comprehensive contributing documentation, please visit our **[Contributing Guide](https://docs.trainloop.ai/development/contributing)** in the documentation site.

The full documentation includes:
- **[Development Setup](https://docs.trainloop.ai/development/local-development)** - Complete environment setup
- **[Building from Source](https://docs.trainloop.ai/development/building-from-source)** - Build process and commands
- **[Testing Guide](https://docs.trainloop.ai/development/testing)** - Test framework and execution
- **[Pull Request Process](https://docs.trainloop.ai/development/pull-request-process)** - PR workflow and guidelines
- **[Code Style](https://docs.trainloop.ai/development/code-style)** - Coding standards and conventions
- **[Architecture](https://docs.trainloop.ai/development/architecture)** - System overview and design

## 🚀 **Quick Start**

### Prerequisites
- Python 3.9+ with pipx
- Node.js 20+ for UI development
- Git for version control

### Development Setup
```bash
# 1. Clone the repository
git clone https://github.com/TrainLoop/trainloop-evals.git
cd trainloop-evals

# 2. Install pipx (if not already installed)
python -m pip install --user pipx
pipx ensurepath

# 3. Install dependencies
npm install

# 4. Run tests to verify setup
npm test
```

### Running the Development Server
```bash
# Documentation site
npm run docs:dev

# Studio UI
npm run dev
```

## 🤝 **Contributing Workflow**

1. **Fork** the repository
2. **Create** a feature branch from `main`
3. **Make** your changes with proper testing
4. **Run** tests and linting: `npm test`
5. **Submit** a pull request with clear description

## 📖 **Getting Help**

- **Documentation**: https://docs.trainloop.ai
- **Issues**: https://github.com/TrainLoop/trainloop-evals/issues
- **Discussions**: https://github.com/TrainLoop/trainloop-evals/discussions

## 🔍 **Need More Details?**

This is a quick reference. For detailed information on any aspect of contributing, please refer to our comprehensive documentation at **https://docs.trainloop.ai/development/contributing**.
