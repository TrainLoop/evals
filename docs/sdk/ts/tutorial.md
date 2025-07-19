# TypeScript SDK Tutorial

## Installation

```bash
npm install trainloop-llm-logging
```

## Basic Usage

### Step 1: Import Order is Critical!

**⚠️ Important**: Always import and initialize TrainLoop BEFORE importing any HTTP client libraries.

```javascript
// ✅ CORRECT: TrainLoop first
import { collect, trainloopTag } from 'trainloop-llm-logging';
collect(); // Synchronous - no await needed!

// Then import HTTP clients
import OpenAI from 'openai';

// ❌ WRONG: This will throw an error
import OpenAI from 'openai';
import { collect } from 'trainloop-llm-logging';
collect(); // Error: OpenAI imported before TrainLoop!
```

### Step 2: Tag Your LLM Calls

Use `trainloopTag` to categorize your LLM calls:

```javascript
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  defaultHeaders: trainloopTag('my-feature')
});
```

### For Long-Running Applications

Use auto-initialization with NODE_OPTIONS:
```bash
NODE_OPTIONS="--require=trainloop-llm-logging" node index.js
```

### For Short-Lived Scripts

**⚠️ Important**: Scripts that exit quickly need special handling to ensure events are written to disk.

#### Option 1: Instant Flush (Recommended)
```javascript
import { collect } from 'trainloop-llm-logging';

// Enable instant flush mode (synchronous)
collect(true);

// Your LLM calls here...
```

#### Option 2: Manual Shutdown
```javascript
import { collect, shutdown } from 'trainloop-llm-logging';

collect(); // Synchronous initialization

// Your LLM calls here...

// Always flush before exiting
await shutdown();
```

## Complete Example

Here's a complete working example:

```javascript
// example.js
import { collect, trainloopTag } from 'trainloop-llm-logging';

// 1. Initialize TrainLoop first (synchronous)
collect(true); // true = instant flush for short scripts

// 2. Now import OpenAI
import OpenAI from 'openai';

async function main() {
  // 3. Create OpenAI client with TrainLoop headers
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    defaultHeaders: trainloopTag('tutorial-example')
  });

  // 4. Make LLM calls - they'll be automatically captured
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [{ role: 'user', content: 'Hello!' }]
  });

  console.log(completion.choices[0].message.content);
  
  // Events are automatically saved to ./trainloop/data/events/
}

main();
```

## Configuration

Set the data folder path:
```bash
export TRAINLOOP_DATA_FOLDER="$(pwd)/trainloop/data"
```

Or use a config file (`trainloop.config.yaml`):
```yaml
data_folder: ./trainloop/data
log_level: info
```

## Key Points

- Collection happens only when HTTP calls to LLM providers occur
- The SDK automatically patches `fetch` and Node.js HTTP modules
- Events are buffered and written in batches by default
- Short scripts may exit before buffers are flushed
