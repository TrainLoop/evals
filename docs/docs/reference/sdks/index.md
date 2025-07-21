---
sidebar_position: 1
---

# SDK Reference

TrainLoop Evals provides SDKs for multiple languages to instrument your LLM applications with zero-touch instrumentation.

## Installation

Choose your language:

```bash
# Python
pip install trainloop-sdk

# TypeScript/Node.js
npm install @trainloop/sdk

# Go
go get github.com/trainloop/sdk-go
```

## Quick Start

All SDKs follow the same pattern - initialize once, then your LLM calls are automatically instrumented:

```python
# Python
import trainloop
trainloop.init(endpoint="http://localhost:8000")
```

```typescript
// TypeScript
import trainloop from '@trainloop/sdk';
trainloop.init({ endpoint: 'http://localhost:8000' });
```

```go
// Go
trainloop.Init(trainloop.Config{
    Endpoint: "http://localhost:8000",
})
```

## Core Features

All SDKs provide the same functionality:

- **Zero-touch instrumentation**: Automatically capture LLM requests and responses
- **HTTP-based collection**: Simple HTTP endpoint to collect traces
- **Framework agnostic**: Works with any LLM library or framework
- **Minimal overhead**: Designed for production use with minimal performance impact

## Language-Specific Documentation

- [**Python SDK**](python-api.md) - Complete Python API reference and examples
- [**TypeScript SDK**](typescript-api.md) - TypeScript/JavaScript API reference and examples  
- [**Go SDK**](go-api.md) - Go API reference and examples