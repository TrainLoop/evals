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

See the [project README](../../README.md) for more details.
