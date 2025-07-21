# TypeScript SDK How-To

## Initialize the SDK

**Important**: The TrainLoop SDK must be initialized before importing any HTTP client libraries (like OpenAI, Anthropic, Axios, etc.). This ensures proper request interception.

### Correct Import Order

```typescript
// 1. FIRST: Import and initialize TrainLoop
import { collect, trainloopTag } from 'trainloop-llm-logging';
collect(); // Synchronous initialization

// 2. THEN: Import HTTP client libraries
import OpenAI from 'openai';

// 3. Create clients with TrainLoop headers
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  defaultHeaders: trainloopTag('my-feature')
});
```

### Wrong Import Order (Will Show Error)

```typescript
// ❌ WRONG: Importing OpenAI before TrainLoop
import OpenAI from 'openai';
import { collect } from 'trainloop-llm-logging';

collect(); // This will throw an error!
```

The SDK will display a clear error message if HTTP clients are imported too early:
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ TrainLoop SDK Warning: HTTP client libraries imported before initialization   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ The following libraries were imported before TrainLoop SDK was initialized:   ║
║ openai                                                                        ║
║                                                                               ║
║ This prevents the SDK from capturing LLM calls correctly.                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## Flush data immediately
Use the `FLUSH_IMMEDIATELY` env var:
```bash
export TRAINLOOP_FLUSH_IMMEDIATELY=true
```

Or programmatically:
```typescript
import { collect } from 'trainloop-llm-logging';
collect(true);  // Enable instant flush (now synchronous!)
```

## Tag requests
```typescript
import { trainloopTag } from 'trainloop-llm-logging';

fetch(url, { headers: { ...trainloopTag('checkout') } })
```

## Custom config path
```bash
export TRAINLOOP_CONFIG_PATH=./trainloop/trainloop.config.yaml
```

## Config Loading Behavior

The SDK loads configuration in the following order:
1. Environment variables (highest priority)
2. Config file values (fills in any unset env vars)
3. Default values

**Important**: 
- Config file is loaded automatically on first import
- Environment variables always override config file values
- `data_folder` paths in config are resolved relative to the config file location

Example config file:
```yaml
data_folder: ./trainloop/data  # Relative to config file
log_level: info
host_allowlist:
  - api.openai.com
  - api.anthropic.com
flush_immediately: false
```

## Debug Logging

To see detailed HTTP instrumentation logs:
```bash
# Set via environment variable (recommended)
export TRAINLOOP_LOG_LEVEL=debug

# Or in config file (may not work for all logs)
log_level: debug
```

**Note**: HTTP instrumentation logs are at INFO level, not DEBUG level.
