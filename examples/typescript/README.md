# TrainLoop TypeScript/JavaScript Examples

Quick guide to run LLM evaluation examples in TypeScript and JavaScript.

## Setup

```bash
# Install dependencies
npm install

# Create .env file with API keys
cat > .env << EOF
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key  
GEMINI_API_KEY=your-gemini-key
EOF
```

## Run Examples

### TypeScript Examples

```bash
# Code generation example (evaluates if LLM can write valid code)
npx ts-node writesValidCode.ts

# Letter counting example (evaluates counting accuracy)
npx ts-node counterAgent.ts

# Run each script 3-4 times to collect samples
# Check collected data in trainloop/data/events/
```

### JavaScript Examples

```bash
# Code generation example (evaluates if LLM can write valid code)
node writesValidCode.js

# Letter counting example (evaluates counting accuracy)  
node counterAgent.js

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

### Code Generation (`writesValidCode.ts/js`)
Tests how reliably models can generate valid, executable code.
- Prompts for a recursive factorial function
- Measures: syntax correctness, function behavior, error handling
- Most modern LLMs score 100% on this task

### Letter Counting (`counterAgent.ts/js`)
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

## File Structure

- `aiRequest.ts/js` - Utility functions for making OpenAI API requests
- `writesValidCode.ts/js` - Code generation evaluation examples
- `counterAgent.ts/js` - Letter counting evaluation examples
- `trainloop/` - Evaluation configuration and results directory

Both TypeScript and JavaScript versions are provided to demonstrate compatibility with both languages.