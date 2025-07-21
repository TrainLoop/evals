---
sidebar_position: 1
---

# Examples

Complete working examples demonstrating TrainLoop LLM evaluation across multiple programming languages.

## Quick Start Examples

Each language example includes two core scenarios:

### 📝 Code Generation Evaluation
Tests how reliably models can generate valid, executable code.
- Prompts for a recursive factorial function
- Measures: syntax correctness, function behavior, error handling  
- Most modern LLMs score 100% on this task

### 🔤 Letter Counting Evaluation  
Tests basic counting abilities that humans find trivial but LLMs often fail.
- Prompts to count each letter in "strawberry"
- Measures: format compliance, counting accuracy
- Common failure: counting 'r' as 2 instead of 3 due to tokenization

## Language Examples

- [**Python Examples**](python-examples.md) - Complete Python implementation with Poetry
- [**TypeScript Examples**](typescript-examples.md) - TypeScript/JavaScript with npm  
- [**Go Examples**](go-examples.md) - Go implementation with Go modules

## What You'll Learn

- **SDK Integration**: How to instrument your LLM calls for evaluation
- **Data Collection**: Automatic collection of request/response pairs
- **Custom Metrics**: Writing evaluation metrics for your specific use cases
- **Benchmarking**: Comparing performance across different models
- **Studio Integration**: Visualizing results in the TrainLoop Studio UI

## Repository Structure

All examples are available in the [main repository](https://github.com/trainloop/evals) under `/examples/`:

```
examples/
├── python/          # Python examples with Poetry
├── typescript/      # TypeScript/JavaScript examples with npm  
└── go/             # Go examples with Go modules
```

Each language directory includes:
- Complete setup instructions
- Example AI request utilities
- Evaluation metric definitions
- Configuration files
- Sample data and results