# Python SDK Tutorial

Follow these steps to start capturing LLM requests.

1. Install the package:
   ```bash
   pip install trainloop-llm-logging
   ```
2. Set the data folder path:
   ```bash
   export TRAINLOOP_DATA_FOLDER="$(pwd)/trainloop/data"
   ```
3. Call `collect()` before importing OpenAI:
   ```python
   from trainloop_llm_logging import collect
   collect()
   import openai
   ```
4. Make your API calls as usual. Collection only occurs when requests are made.
