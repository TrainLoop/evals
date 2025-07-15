---
sidebar_position: 1
---

# TypeScript SDK API

Complete API reference for the TrainLoop TypeScript/JavaScript SDK.

## Installation

```bash
npm install trainloop-llm-logging
```

## Basic Usage

```javascript
const { OpenAI } = require('openai');
const { trainloopTag } = require('trainloop-llm-logging');

const client = new OpenAI();

const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{"role": "user", "content": "Hello"}]
}, {
    headers: { ...trainloopTag("greeting") }
});
```

## Initialization

The TypeScript SDK uses automatic instrumentation via Node.js require flags:

```bash
# Automatic instrumentation
NODE_OPTIONS="--require=trainloop-llm-logging" node app.js

# With environment variables
TRAINLOOP_DATA_FOLDER=./data NODE_OPTIONS="--require=trainloop-llm-logging" node app.js
```

## API Reference

### trainloopTag(tag, metadata?)

Generate headers for tagging LLM calls.

**Parameters**:
- `tag` (string): Tag name
- `metadata` (object, optional): Additional metadata

**Returns**: Object with headers for HTTP requests

**Example**:
```javascript
// Basic tagging
const headers = trainloopTag("greeting");

// With metadata
const headers = trainloopTag("customer-support", { 
    priority: "high", 
    version: "1.0" 
});
```

### shutdown()

Gracefully shutdown TrainLoop and flush buffered events.

**Example**:
```javascript
const { shutdown } = require('trainloop-llm-logging');

// Flush and shutdown
await shutdown();
```

## Supported Libraries

The TypeScript SDK automatically instruments:

- **OpenAI** (`openai` package)
- **Anthropic** (`@anthropic-ai/sdk` package)
- **Node.js HTTP/HTTPS** (built-in modules)
- **Fetch API** (Node.js 18+)

## Configuration

### Via Environment Variables

```bash
export TRAINLOOP_DATA_FOLDER="./data"
export TRAINLOOP_FLUSH_IMMEDIATELY=true
export TRAINLOOP_TAGS="production,v1.0"
```

### Via Configuration File

```yaml
# trainloop.config.yaml
sdk:
  flush_immediately: false
  buffer_size: 5
  buffer_timeout: 10
  tags: ["production"]
```

## Advanced Usage

### Manual Instrumentation

```javascript
// Without automatic instrumentation
const { instrument } = require('trainloop-llm-logging');

// Manually instrument specific modules
instrument();
```

### Custom Data Folder

```javascript
process.env.TRAINLOOP_DATA_FOLDER = '/custom/path';
// Then start with --require flag
```

### Error Handling

```javascript
process.on('uncaughtException', (error) => {
    if (error.message.includes('TrainLoop')) {
        console.warn('TrainLoop error:', error.message);
        // Continue without instrumentation
    }
});
```

## Examples

### OpenAI Chat Completion

```javascript
const { OpenAI } = require('openai');
const { trainloopTag } = require('trainloop-llm-logging');

const client = new OpenAI();

async function generateResponse() {
    const response = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
    }, {
        headers: { ...trainloopTag("qa") }
    });
    
    return response.choices[0].message.content;
}
```

### Anthropic Claude

```javascript
const Anthropic = require('@anthropic-ai/sdk');
const { trainloopTag } = require('trainloop-llm-logging');

const client = new Anthropic();

async function generateResponse() {
    const response = await client.messages.create({
        model: "claude-3-haiku-20240307",
        max_tokens: 1000,
        messages: [
            {"role": "user", "content": "Hello, Claude!"}
        ]
    }, {
        headers: { ...trainloopTag("greeting") }
    });
    
    return response.content[0].text;
}
```

### Express.js Application

```javascript
const express = require('express');
const { OpenAI } = require('openai');
const { trainloopTag, shutdown } = require('trainloop-llm-logging');

const app = express();
const client = new OpenAI();

app.post('/chat', async (req, res) => {
    const response = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: req.body.messages
    }, {
        headers: { ...trainloopTag("chat-api") }
    });
    
    res.json(response);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    await shutdown();
    process.exit(0);
});

app.listen(3000);
```

### Streaming Responses

```javascript
const { OpenAI } = require('openai');
const { trainloopTag } = require('trainloop-llm-logging');

const client = new OpenAI();

async function streamChat() {
    const stream = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [{"role": "user", "content": "Tell me a story"}],
        stream: true
    }, {
        headers: { ...trainloopTag("streaming") }
    });
    
    for await (const chunk of stream) {
        process.stdout.write(chunk.choices[0]?.delta?.content || '');
    }
}
```

## TypeScript Support

```typescript
import { OpenAI } from 'openai';
import { trainloopTag } from 'trainloop-llm-logging';

const client = new OpenAI();

async function generateResponse(message: string): Promise<string> {
    const response = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [{"role": "user", "content": message}]
    }, {
        headers: { ...trainloopTag("typescript-example") }
    });
    
    return response.choices[0].message.content || '';
}
```

## Troubleshooting

### Common Issues

**Module not found**: Install with `npm install trainloop-llm-logging`

**No data collected**: Ensure `--require=trainloop-llm-logging` flag is used

**High memory usage**: Set `TRAINLOOP_FLUSH_IMMEDIATELY=true`

**Missing events**: Verify environment variables are set correctly

### Debug Mode

```bash
# Enable debug logging
DEBUG=trainloop* NODE_OPTIONS="--require=trainloop-llm-logging" node app.js
```

## See Also

- [SDK Overview](../index.md) - Multi-language SDK documentation
- [Getting Started](../../../tutorials/getting-started.md) - Complete setup guide
- [Python SDK](../python/api.md) - Python API reference
- [Go SDK](../go/api.md) - Go API reference