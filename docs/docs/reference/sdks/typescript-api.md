---
sidebar_position: 3
---

# TypeScript SDK API

The TrainLoop Evals TypeScript SDK provides zero-touch instrumentation for Node.js and TypeScript applications.

## Installation

```bash
npm install @trainloop/sdk
```

## Quick Start

```typescript
import trainloop from '@trainloop/sdk';

// Initialize the SDK
trainloop.init({ endpoint: 'http://localhost:8000' });

// Your LLM calls are automatically instrumented
import OpenAI from 'openai';
const openai = new OpenAI();
const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello, world!' }]
});
```

## Configuration

The SDK can be configured using environment variables or initialization parameters:

### Environment Variables

- `TRAINLOOP_ENDPOINT` - The endpoint to send traces to (default: `http://localhost:8000`)
- `TRAINLOOP_API_KEY` - API key for authentication (optional)
- `TRAINLOOP_DEBUG` - Enable debug logging (default: `false`)

### Initialization Parameters

```typescript
import trainloop from '@trainloop/sdk';

trainloop.init({
  endpoint: 'http://localhost:8000',
  apiKey: 'your-api-key',
  debug: true
});
```

## Supported Libraries

The TypeScript SDK automatically instruments the following libraries:

- OpenAI
- Anthropic
- LangChain
- Custom HTTP clients

## Manual Instrumentation

For custom instrumentation, you can use the manual tracing API:

```typescript
import trainloop from '@trainloop/sdk';

const span = trainloop.trace('my-llm-call');
span.setInput({ prompt: 'Hello, world!' });
// Your LLM call here
span.setOutput({ response: 'Hello! How can I help you?' });
span.finish();
```