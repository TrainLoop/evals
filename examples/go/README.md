# TrainLoop Go Examples

This directory demonstrates LLM evaluation using Go with TrainLoop's evaluation framework.

## Project Structure

```
examples/go/
├── ai_request/           # Shared AI request package
│   └── ai_request.go    # Simplified HTTP client using TrainLoop SDK  
├── cmd/                 # Individual example programs
│   ├── active_voice_rewriter/
│   ├── counter_agent/
│   ├── polite_responder/
│   └── writes_valid_code/
├── go.mod              # Single Go module for all examples
└── trainloop/          # Evaluation configuration and results
```

## Quick Start

### 1. Setup Environment

```bash
# Install Go dependencies
go mod tidy

# Create .env file with your keys
cp .env.example .env
```

### 2. Run Examples

Each example demonstrates different evaluation scenarios:

```bash
# Code generation - tests if LLM writes valid, executable code
go run cmd/writes_valid_code/writes_valid_code.go

# Letter counting - tests basic counting abilities (surprisingly difficult for LLMs)  
go run cmd/counter_agent/counter_agent.go

# Customer support - tests polite, empathetic response generation
go run cmd/polite_responder/polite_responder.go

# Writing style - tests active voice transformation
go run cmd/active_voice_rewriter/active_voice_rewriter.go
```

**💡 Tip:** Run each example 3-4 times to collect multiple data points for evaluation.

### 3. Evaluate Results

```bash
# Install TrainLoop CLI (if not already installed)
pipx install trainloop-cli

# Run evaluation on collected data
cd trainloop
trainloop eval

# View results in interactive web UI
trainloop studio
```

## How It Works

### TrainLoop SDK Integration

The examples use a **simplified architecture** that leverages the TrainLoop Go SDK's automatic instrumentation:

1. **Shared AI Request Package** (`ai_request/`): Simple HTTP client wrapper
2. **Automatic Instrumentation**: TrainLoop SDK patches HTTP transport globally via `trainloop.Collect()`
3. **Request Tagging**: Optional tagging with `trainloop.TrainloopTag()` for evaluation suites
4. **Data Collection**: All OpenAI API calls automatically captured and saved to `trainloop/data/events/`

### Code Architecture Benefits

- **No complex transport wrapping**: SDK handles HTTP instrumentation automatically
- **Thread-safe**: No manual mutex management needed  
- **Clean separation**: Shared logic in `ai_request/`, examples in `cmd/`
- **Linter-friendly**: Each example in its own directory avoids "main redeclared" errors

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

### Code Generation (`writes_valid_code.go`)
Tests how reliably models can generate valid, executable code.
- Prompts for a recursive factorial function
- Measures: syntax correctness, function behavior, error handling
- Most modern LLMs score 100% on this task

### Letter Counting (`counter_agent.go`)
Tests basic counting abilities that humans find trivial but LLMs often fail.
- Prompts to count each letter in "strawberry"
- Measures: format compliance, counting accuracy
- Common failure: counting 'r' as 2 instead of 3 due to tokenization

### Customer Support Tone (`polite_responder.go`)
Tests whether models can produce polite, empathetic customer service responses.
- Prompts for a response to an angry customer complaint
- Measures: politeness/apology, word count limit (≤120 words)
- Evaluates tone, empathy, and solution-oriented approach

### Active Voice Transformation (`active_voice_rewriter.go`)
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