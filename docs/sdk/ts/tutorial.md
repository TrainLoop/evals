# TypeScript SDK Tutorial

## Installation

```bash
npm install trainloop-llm-logging
```

## Basic Usage

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

// Enable instant flush mode
await collect(true);

// Your LLM calls here...
```

#### Option 2: Manual Shutdown
```javascript
import { collect, shutdown } from 'trainloop-llm-logging';

await collect();

// Your LLM calls here...

// Always flush before exiting
await shutdown();
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
