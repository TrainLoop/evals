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
cat > .env << EOF
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key  
GEMINI_API_KEY=your-gemini-key
EOF
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

Results are saved in `trainloop/data/results/`

## View Results in Studio

```bash
# Launch the interactive UI to explore results
trainloop studio
```

This opens a web interface to visualize the events, results, and benchmarks.