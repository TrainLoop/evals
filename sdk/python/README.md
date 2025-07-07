# TrainLoop Evals SDK (Python)

Automatically capture LLM calls from Python apps so they can be graded later.

## Install

```bash
pip install trainloop-llm-logging
```

## Quick example

```python
from trainloop_llm_logging import collect, trainloop_tag
collect()  # patch HTTP clients
openai.chat.completions.create(..., trainloop_tag("my-tag"))
```

Set `TRAINLOOP_DATA_FOLDER` to choose where event files are written or set `data_folder` in your `trainloop.config.yaml` file.

## Buffering and Flushing

By default, the SDK buffers LLM calls and flushes them every 10 seconds or when 5+ calls are buffered. This is efficient for long-running applications.

### Immediate Flushing

For testing or scripts that may exit quickly, use `flush_immediately=True`:

```python
from trainloop_llm_logging import collect
collect(flush_immediately=True)  # Flush after each LLM call
```

### Manual Flushing

For more control, use the default buffering and flush manually when needed:

```python
from trainloop_llm_logging import collect, flush

collect()  # Default buffering (10s or 5+ calls)
# ... your LLM calls ...
flush()  # Manually flush buffered calls
```

This is particularly useful for:
- Testing scenarios where you need immediate data
- Scripts that may terminate before the buffer flushes
- Debugging or development workflows

See the [project README](../../README.md) for more details.
