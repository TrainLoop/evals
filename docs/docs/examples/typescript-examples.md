---
sidebar_position: 3
---

# TypeScript Examples

Complete working examples demonstrating TrainLoop LLM evaluation with TypeScript and JavaScript.

## Overview

The TypeScript examples include both TypeScript and JavaScript versions:
- **Code Generation**: Testing LLM ability to write valid Python code  
- **Letter Counting**: Testing basic counting accuracy
- **Dual Language Support**: Same examples in both TypeScript and JavaScript

## Prerequisites

- Node.js 16+
- OpenAI API key (or other supported LLM provider)

## Quick Setup

```bash
# Navigate to TypeScript examples
cd examples/typescript

# Install dependencies
npm install

# Create .env file with API keys
cat > .env << EOF
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key  
GEMINI_API_KEY=your-gemini-key
EOF
```

## Run TypeScript Examples

```bash
# Code generation example (evaluates if LLM can write valid code)
NODE_OPTIONS="--require=trainloop-llm-logging" npx ts-node writesValidCode.ts

# Letter counting example (evaluates counting accuracy)
NODE_OPTIONS="--require=trainloop-llm-logging" npx ts-node counterAgent.ts

# Alternative: Use npm scripts
npm run code-generation:ts
npm run letter-counting:ts
```

## Run JavaScript Examples  

```bash
# Code generation example (evaluates if LLM can write valid code)
NODE_OPTIONS="--require=trainloop-llm-logging" node writesValidCode.js

# Letter counting example (evaluates counting accuracy)  
NODE_OPTIONS="--require=trainloop-llm-logging" node counterAgent.js

# Alternative: Use npm scripts
npm run code-generation:js
npm run letter-counting:js
```

## Evaluate Results

```bash
# Install TrainLoop CLI globally (recommended)
pipx install trainloop-cli

# Run evaluation
cd trainloop
trainloop eval
```

## Key Components

### AI Request Utility (TypeScript)

```typescript
import OpenAI from 'openai';
import dotenv from 'dotenv';

dotenv.config();
const client = new OpenAI();

export async function makeAiRequest(
    prompt: string,
    model: string = "gpt-4o-mini",
    maxTokens: number = 500,
    extraHeaders: Record<string, string> = {}
): Promise<string | null> {
    const response = await client.chat.completions.create({
        model,
        messages: [{ role: "user", content: prompt }],
        max_tokens: maxTokens,
    }, {
        headers: extraHeaders
    });
    
    return response.choices[0].message.content;
}
```

### TrainLoop Integration

```typescript
// TypeScript version
import { trainloopTag } from 'trainloop-llm-logging';
import { makeAiRequest } from './aiRequest';

// Tag requests for evaluation suites  
const headers = trainloopTag("code-generation");
const response = await makeAiRequest(promptText, "gpt-4o-mini", 500, headers);
```

```javascript
// JavaScript version
const { trainloopTag } = require('trainloop-llm-logging');
const { makeAiRequest } = require('./aiRequest');

// Tag requests for evaluation suites
const headers = trainloopTag("letter-counting");
const response = await makeAiRequest(promptText, "gpt-4o-mini", 500, headers);
```

## Important Notes

### Logging Setup

TrainLoop logging is configured via `NODE_OPTIONS="--require=trainloop-llm-logging"`. This must be set before running your scripts.

### Package.json Scripts

The examples include pre-configured scripts:

```json
{
  "scripts": {
    "code-generation:ts": "npx ts-node writesValidCode.ts",
    "letter-counting:ts": "npx ts-node counterAgent.ts", 
    "code-generation:js": "node writesValidCode.js",
    "letter-counting:js": "node counterAgent.js"
  }
}
```

## Expected Output

When you run the examples, you'll see:

```
Loaded TrainLoop config from trainloop/trainloop.config.yaml
[dotenv@17.2.0] injecting env (2) from .env
AI Response: ```python
def factorial(n):
    if n < 0:
        raise ValueError("Negative numbers do not have a factorial.")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```
```

## Next Steps

- [View Python Examples](python-examples.md)
- [View Go Examples](go-examples.md) 
- [Learn about Custom Metrics](../tutorials/advanced-metrics.md)