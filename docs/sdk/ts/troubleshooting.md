# TypeScript SDK Troubleshooting

## Common Issues

### Events Not Being Written to Disk

**Symptoms**: No `.jsonl` files appear in the data folder after running your script.

**Causes & Solutions**:

1. **Short-lived scripts exiting too quickly**
   - Solution: Use instant flush mode
   ```typescript
   await collect(true);  // Enable instant flush
   ```
   
2. **Auto-initialization with NODE_OPTIONS in short scripts**
   - Problem: `NODE_OPTIONS="--require=trainloop-llm-logging"` may not flush before exit
   - Solution: Use explicit initialization instead
   ```typescript
   import { collect, shutdown } from 'trainloop-llm-logging';
   await collect();
   // ... your code ...
   await shutdown();  // Note: shutdown is async but doesn't return a promise
   ```

3. **Missing await on async operations**
   - Ensure you're awaiting `collect()`
   - Note: `flush()` and `shutdown()` are async functions but work synchronously

### Debug Logs Not Appearing

**Symptoms**: No INFO or DEBUG logs from the SDK even with `log_level: debug`.

**Cause**: Logger timing issue - loggers are created before config is loaded.

**Solution**: Set the environment variable instead:
```bash
export TRAINLOOP_LOG_LEVEL=debug
```

### HTTP Instrumentation Not Working

**Symptoms**: HTTP calls to LLM providers aren't being captured.

**Possible causes**:

1. **Host not in allowlist**
   - Check your `host_allowlist` configuration
   - Default includes common providers (OpenAI, Anthropic, etc.)

2. **SDK not initialized**
   - Ensure `collect()` is called before making HTTP requests

3. **Custom HTTP client**
   - The SDK patches native `fetch` and Node.js `http/https` modules
   - Custom clients may need manual instrumentation

### Config File Not Being Loaded

**Symptoms**: SDK uses default values instead of config file settings.

**Solutions**:

1. **Check file location**
   - Default: `./trainloop.config.yaml`
   - Set custom path: `export TRAINLOOP_CONFIG_PATH=/path/to/config`

2. **Verify YAML syntax**
   - Ensure proper indentation and formatting

3. **Remember precedence**
   - Environment variables always override config file values

## Debugging Tips

### Verify SDK is Active
```typescript
import { collect } from 'trainloop-llm-logging';

// Check if fetch is patched
console.log('Fetch patched:', global.fetch.name === 'patchedFetch');

await collect();
console.log('TrainLoop initialized');
```

### Check Environment
```bash
# See all TrainLoop env vars
env | grep TRAINLOOP
```

### Manual Testing
```typescript
// Force a flush to test writing
import { flush } from 'trainloop-llm-logging';
await flush();
```

## Technical Deep Dive (For SDK Contributors)

This section documents critical implementation details discovered during SDK debugging that future contributors should be aware of.

### Logger Initialization Timing Issue

**Root Cause**: Loggers were originally created at module load time in multiple files:
- `store.ts` (line 5)
- `exporter.ts` (line 7) 
- `instrumentation/fetch.ts` (line 6)
- `instrumentation/http.ts` (line 10)
- `instrumentation/utils.ts` (line 6)

**Problem**: These loggers were instantiated BEFORE config file loading, when `TRAINLOOP_LOG_LEVEL` was undefined, causing them to default to "warn" level.

**Module Loading Order**:
```
1. User requires SDK
2. Modules imported → Loggers created with LOG_LEVEL=undefined 
3. Config loading sets TRAINLOOP_LOG_LEVEL=DEBUG
4. But loggers already created with wrong level
```

**Solution Implemented**: Lazy logger initialization using Proxy pattern. Loggers are now created on first use rather than module load time, ensuring they pick up the correct log level from config.

### Auto-initialization with NODE_OPTIONS

**Root Cause**: When using `NODE_OPTIONS="--require=trainloop-llm-logging"`, the SDK auto-initializes before the user's script runs. For short-lived scripts, this causes events to be buffered but never written because:
- Default behavior uses timer-based flush (10 seconds or 5 events)
- Short scripts exit before timer fires or batch size reached
- Events remain buffered in memory

**Critical Code Paths**:
- Auto-initialization: `src/index.ts` line 59: `collect();`
- Config loading: `src/config.ts` - loads on first import
- Flush logic: `src/exporter.ts` - timer-based by default

### Key Architectural Discoveries

**OpenAI SDK Uses Fetch**: The OpenAI SDK uses the native `fetch` API, not `http`/`https` modules. The SDK correctly patches `global.fetch` and verification shows `global.fetch.name` changes from "fetch" to "patchedFetch".

**Config Loading Precedence**: The config loading implementation correctly:
- Always loads config file even when some env vars are set
- Uses config values for any unset environment variables  
- Ensures environment variables take precedence over config values
- Resolves `data_folder` path relative to config file location

### Testing Considerations

When writing tests for the SDK, be aware of:

1. **Module Loading Order**: Tests must clear module cache between test cases to properly test initialization timing
2. **Async Timing**: Flush operations may be asynchronous even when they appear synchronous
3. **Environment Isolation**: Tests must carefully manage environment variables to avoid cross-test contamination
4. **File System State**: Integration tests should use isolated temporary directories

### Debugging Utilities

For debugging timing issues:
```typescript
// Track module loading order
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(id) {
  if (id.includes('logger') || id.includes('config')) {
    console.log(`[REQUIRE] ${id} - LOG_LEVEL=${process.env.TRAINLOOP_LOG_LEVEL}`);
  }
  return originalRequire.apply(this, arguments);
};
```

For verifying lazy initialization:
```typescript
// Check if logger creates on first use
import { createLogger } from 'trainloop-llm-logging/dist/logger';
const logger = createLogger('test');
// Logger proxy created but not initialized
logger.debug('This will initialize the logger');
// Now logger is initialized with current env vars
```