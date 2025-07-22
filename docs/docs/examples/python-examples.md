---
sidebar_position: 2
---

# Python Examples

Complete working example demonstrating TrainLoop LLM evaluation with Python.

## Overview

The Python examples demonstrate two core evaluation scenarios:
- **Code Generation**: Testing LLM ability to write valid Python code
- **Letter Counting**: Testing basic counting accuracy

## Prerequisites

- Python 3.8+
- OpenAI API key (or other supported LLM provider)

## Quick Setup

```bash
# Navigate to Python examples
cd examples/python

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with API keys
cp .env.example .env
```

## Run Examples

```bash
# Code generation example (evaluates if LLM can write valid code)
python writes_valid_code.py

# Letter counting example (evaluates counting accuracy)
python counter_agent.py

# Run each script 3-4 times to collect samples
# Check collected data in trainloop/data/events/
```

## Evaluate Results

```bash
# Install TrainLoop CLI globally (recommended)
pipx install trainloop-cli

# Or install in virtual environment
pip install -e ../../cli

# Check that it installed correctly
trainloop --version

# Run evaluation
cd trainloop
trainloop eval
```

## Key Components

### AI Request Utility (`ai_request.py`)

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def make_ai_request(
    prompt: str,
    model: str = "gpt-4.1",
    max_tokens: int = 500,
    extra_headers: dict = {},
):
    # Makes request with TrainLoop instrumentation
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        extra_headers=extra_headers,
    )
    return response.choices[0].message.content
```

### TrainLoop Integration

```python
from trainloop_llm_logging import collect, trainloop_tag

# CRITICAL: Import and call collect BEFORE importing OpenAI
collect(flush_immediately=True)

from ai_request import make_ai_request

# Tag requests for evaluation suites
headers = trainloop_tag("code-generation")
response = make_ai_request(prompt, extra_headers=headers)
```

## Expected Output

When you run the examples, you'll see:

```
[TrainLoop] Loading config...
[TrainLoop] Loaded TrainLoop config from trainloop/trainloop.config.yaml
AI Response: def factorial(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)
```

## Next Steps

- [View TypeScript Examples](typescript-examples.md)
- [View Go Examples](go-examples.md)
- [Learn about Custom Metrics](../tutorials/advanced-metrics.md)