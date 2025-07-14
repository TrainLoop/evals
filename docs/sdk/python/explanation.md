# Python SDK Explanation

The SDK patches `requests` and `httpx`. It writes JSONL files to the data folder. Calls are buffered and flushed every ten seconds or after five items. Set `flush_immediately=True` to disable buffering. The library reads configuration from `trainloop.config.yaml` or environment variables. Collection starts when you call `collect()` and stops when the process exits.
