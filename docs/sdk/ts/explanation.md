# TypeScript SDK Explanation

The package patches `http`, `https`, and `fetch`. It buffers calls and writes them to JSONL files in the data folder. Use `TRAINLOOP_FLUSH_IMMEDIATELY=true` for testing. The SDK reads configuration from `trainloop.config.yaml` if environment variables are missing. Collection starts automatically when the module loads.
