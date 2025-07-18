---
sidebar_position: 1
---

# Introduction to TrainLoop Evals

Welcome to **TrainLoop Evals**, a comprehensive framework for automating the collection and evaluation of Large Language Model (LLM) outputs. TrainLoop Evals simplifies the process of testing and improving your AI applications with a focus on developer experience and reliability.

## What is TrainLoop Evals?

TrainLoop Evals is an end-to-end evaluation framework that consists of:

- **🤖 CLI Tool** (`trainloop` command) - Python-based evaluation engine for managing evaluation workflows
- **🎨 Studio UI** - Next.js web interface for visualizing and analyzing evaluation results
- **📚 Multi-language SDKs** - Zero-touch instrumentation libraries for Python, TypeScript, and Go
- **🔧 Registry System** - Shareable metrics and evaluation suites for common use cases

## Core Principles

TrainLoop Evals is built around five key principles:

### 🎯 Simplicity First
One environment variable, one function call, one folder of JSON files. No complex setup required.

### 🔄 Vendor Independence
Everything is stored as newline-delimited JSON files. No databases, no vendor lock-in.

### 👥 Meet Developers Where They Are
Accepts both simple declarative flows and existing bespoke evaluation loops.

### 🔒 Type-safe, In-code Tests
All evaluation code lives in your codebase with full type safety.

### 🧩 Composable, Extensible System
Helper generators follow proven patterns (similar to shadcn/ui) with `trainloop add` command.

## Key Features

### 📊 Automatic Data Collection
- **Zero-touch instrumentation** - Add one line to capture all LLM calls
- **Multi-language support** - Works with Python, TypeScript/JavaScript, and Go
- **Flexible tagging** - Tag specific calls for targeted evaluation
- **Buffering control** - Configure immediate or batched data collection

### 🔍 Powerful Evaluation Engine
- **Custom metrics** - Write Python functions to evaluate any aspect of LLM output
- **Test suites** - Group related evaluations into logical collections
- **LLM Judge** - Built-in AI-powered evaluation for subjective metrics
- **Benchmarking** - Compare multiple LLM providers on the same tasks

### 📈 Rich Visualization
- **Interactive Studio UI** - Explore evaluation results with charts and tables
- **DuckDB integration** - Query evaluation data with SQL
- **Real-time updates** - See evaluation results as they happen
- **Export capabilities** - Share and analyze results outside the platform

### 🚀 Production Ready
- **Scalable architecture** - Handles large-scale evaluation workloads
- **Cloud storage support** - Works with S3, GCS, and Azure
- **CI/CD integration** - Automate evaluations in your development pipeline
- **Comprehensive testing** - Extensively tested across all components

## Use Cases

TrainLoop Evals is perfect for:

- **🔧 Development Testing** - Continuously evaluate LLM outputs during development
- **📊 A/B Testing** - Compare different prompts, models, or configurations
- **🔍 Quality Assurance** - Ensure LLM outputs meet quality standards before deployment
- **📈 Performance Monitoring** - Track LLM performance over time in production
- **🏆 Model Comparison** - Benchmark different LLM providers and models
- **🎯 Regression Testing** - Detect when changes negatively impact LLM performance

## How It Works

1. **🔧 Instrument** - Add TrainLoop SDK to your application with minimal code changes
2. **📝 Collect** - Automatically capture LLM requests and responses as JSONL files
3. **📊 Evaluate** - Define custom metrics and test suites to assess LLM performance
4. **📈 Analyze** - Use the Studio UI to visualize results and identify patterns
5. **🔄 Iterate** - Refine your prompts and models based on evaluation insights

## Architecture Overview

![TrainLoop Evals Flow](/trainloop-evals-flow.png)

TrainLoop Evals provides a complete workflow from data collection to analysis:

- **Multi-language SDKs** automatically capture LLM interactions from your applications
- **Event storage** preserves all request/response data in JSONL format
- **Evaluation engine** applies custom metrics and suites to generate results
- **Studio UI** provides interactive visualization and benchmarking capabilities

## Getting Started

Ready to start evaluating your LLM applications? Here's what you need to do:

1. **[Install TrainLoop CLI](./getting-started/installation.md)** - Get the command-line tool
2. **[Follow the Quick Start Guide](./getting-started/quick-start.md)** - Set up your first evaluation
3. **[Explore the Guides](./guides/)** - Learn advanced features and best practices
4. **[Check the Reference](./reference/)** - Detailed API documentation

## Demo

Want to see TrainLoop Evals in action? Check out our demo:

- **[Demo Repository](https://github.com/trainloop/chat-ui-demo)** - Complete example implementation
- **[Live Demo](https://evals.trainloop.ai)** - Interactive demo deployment

## Community and Support

- **[GitHub Repository](https://github.com/trainloop/evals)** - Source code and issues
- **[Contributing Guide](https://github.com/trainloop/evals/blob/main/CONTRIBUTING.md)** - How to contribute
- **[DeepWiki](https://deepwiki.com/TrainLoop/evals)** - Chat directly with the codebase instead of reading docs. It's the purest form of talking to your documentation.
- **[License](https://github.com/trainloop/evals/blob/main/LICENSE)** - MIT License

Get started today and transform how you evaluate and improve your LLM applications!