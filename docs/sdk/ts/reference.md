# TypeScript SDK Reference

## Public API

### `collect(instantFlush?: boolean): Promise<void>`
Initializes TrainLoop data collection.
- `instantFlush` (optional): If `true`, writes events immediately after each LLM call. Recommended for short-lived scripts.

### `trainloopTag(name: string): void`
Tags subsequent LLM calls with a custom identifier.

### `flush(): Promise<void>`
Manually flushes buffered events to disk. Only works after `collect()` has been called.

### `shutdown(): Promise<void>`
Flushes all buffered events and closes the SDK. Always call this before exiting.

### `HEADER_NAME`
The HTTP header name used for tagging requests.

## Environment Variables

### `TRAINLOOP_DATA_FOLDER`
Path to the data folder. Defaults to `./trainloop/data`.

### `TRAINLOOP_CONFIG_PATH`
Path to the config file. Defaults to `./trainloop.config.yaml`.

### `TRAINLOOP_HOST_ALLOWLIST`
Comma-separated list of allowed hosts for instrumentation.

### `TRAINLOOP_LOG_LEVEL`
Logging level: `error`, `warn`, `info`, or `debug`.

**⚠️ Important**: Due to module loading order, setting `log_level` in the config file may not affect HTTP instrumentation logs. Use the environment variable for reliable debug logging.

### `TRAINLOOP_FLUSH_IMMEDIATELY`
Set to `true` to enable instant flush mode (same as `collect(true)`)
