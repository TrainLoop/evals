# TrainLoop TypeScript/JavaScript Examples

Quick guide to run LLM evaluation examples in TypeScript and JavaScript.

## Setup

```bash
# Install dependencies
npm install

# Create .env file with API keys
cp .env.example .env
```

## Run Examples

### TypeScript Examples

```bash
# Code generation example (evaluates if LLM can write valid code)
npx ts-node writesValidCode.ts

# Letter counting example (evaluates counting accuracy)
npx ts-node counterAgent.ts

# Customer support tone example (evaluates polite responses)
npx ts-node politeResponder.ts

# Active voice transformation example (evaluates style rewriting)
npx ts-node activeVoiceRewriter.ts

# Run each script 3-4 times to collect samples
# Check collected data in trainloop/data/events/
```

### JavaScript Examples

```bash
# Code generation example (evaluates if LLM can write valid code)
node writesValidCode.js

# Letter counting example (evaluates counting accuracy)  
node counterAgent.js

# Customer support tone example (evaluates polite responses)
node politeResponder.js

# Active voice transformation example (evaluates style rewriting)
node activeVoiceRewriter.js

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

### Customer Support Tone (`politeResponder.ts/js`)
Tests whether models can produce polite, empathetic customer service responses.
- Prompts for a response to an angry customer complaint
- Measures: politeness/apology, word count limit (≤120 words)
- Evaluates tone, empathy, and solution-oriented approach

### Active Voice Transformation (`activeVoiceRewriter.ts/js`)
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

## File Structure

- `aiRequest.ts/js` - Utility functions for making OpenAI API requests
- `writesValidCode.ts/js` - Code generation evaluation examples
- `counterAgent.ts/js` - Letter counting evaluation examples
- `politeResponder.ts/js` - Customer support tone evaluation examples
- `activeVoiceRewriter.ts/js` - Active voice transformation evaluation examples
- `trainloop/` - Evaluation configuration and results directory

Both TypeScript and JavaScript versions are provided to demonstrate compatibility with both languages.