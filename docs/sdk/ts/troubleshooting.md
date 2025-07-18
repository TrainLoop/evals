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