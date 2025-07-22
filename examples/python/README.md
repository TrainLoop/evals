# TrainLoop Python Examples

Quick guide to run LLM evaluation examples.

## Setup

```bash
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

# Customer support tone example (evaluates polite responses)
python polite_responder.py

# Active voice transformation example (evaluates style rewriting)
python active_voice_rewriter.py

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

## Benchmark Models

```bash
# Compare different models
trainloop benchmark
```

## What's Being Evaluated

### Code Generation (`writes_valid_code.py`)
Tests how reliably models can generate valid, executable code.
- Prompts for a recursive factorial function
- Measures: syntax correctness, function behavior, error handling
- Most modern LLMs score 100% on this task

### Letter Counting (`counter_agent.py`)
Tests basic counting abilities that humans find trivial but LLMs often fail.
- Prompts to count each letter in "strawberry"
- Measures: format compliance, counting accuracy
- Common failure: counting 'r' as 2 instead of 3 due to tokenization

### Customer Support Tone (`polite_responder.py`)
Tests whether models can produce polite, empathetic customer service responses.
- Prompts for a response to an angry customer complaint
- Measures: politeness/apology, word count limit (≤120 words)
- Evaluates tone, empathy, and solution-oriented approach

### Active Voice Transformation (`active_voice_rewriter.py`)
Tests simple style transformation from passive to active voice.
- Prompts to rewrite a passive sentence in active voice
- Measures: successful voice transformation while preserving meaning
- Evaluates basic writing style adaptation

Results are saved in `trainloop/data/results/`

## View Results in Studio

```bash
# Launch the interactive UI to explore results
trainloop studio
```

This opens a web interface to visualize the events, results, and benchmarks.