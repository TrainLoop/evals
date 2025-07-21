# Go Getting Started

Complete working example demonstrating TrainLoop LLM evaluation with Go.

## Overview

The Go examples demonstrate two core evaluation scenarios:
- **Code Generation**: Testing LLM ability to write valid Python code
- **Letter Counting**: Testing basic counting accuracy

## Prerequisites

- Go 1.20+
- OpenAI API key (or other supported LLM provider)

## Quick Setup

```bash
# Navigate to Go examples
cd examples/go

# Install Go dependencies
go mod tidy

# Note: If you encounter import issues with trainloop-llm-logging,
# the examples use the GitHub import path:
# import trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"

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
go run ai_request.go writes_valid_code.go

# Letter counting example (evaluates counting accuracy)  
go run ai_request.go counter_agent.go

# Run each script 3-4 times to collect samples
# Check collected data in trainloop/data/events/
```

## Evaluate Results

```bash
# Install TrainLoop CLI globally (recommended)
pipx install trainloop-cli

# Check that it installed correctly
trainloop --version

# Run evaluation
cd trainloop
trainloop eval
```

## Key Components

### AI Request Utility (`ai_request.go`)

```go
package main

import (
    "context"
    "fmt"
    "os"
    
    "github.com/joho/godotenv"
    "github.com/sashabaranov/go-openai"
)

func init() {
    godotenv.Load()
}

func MakeAIRequest(prompt, model string, maxTokens int, extraHeaders map[string]string) (string, error) {
    if model == "" {
        model = "gpt-4"
    }

    client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))
    
    req := openai.ChatCompletionRequest{
        Model:     model,
        MaxTokens: maxTokens,
        Messages: []openai.ChatCompletionMessage{
            {
                Role:    openai.ChatMessageRoleUser,
                Content: prompt,
            },
        },
    }

    resp, err := client.CreateChatCompletion(context.Background(), req)
    if err != nil {
        return "", fmt.Errorf("chat completion error: %v", err)
    }

    return resp.Choices[0].Message.Content, nil
}
```

### TrainLoop Integration

```go
package main

import (
    "fmt"
    "log"
    
    trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

func init() {
    // CRITICAL: Call Collect() in init() BEFORE making AI requests
    trainloop.Collect()
}

func main() {
    // Tag requests for evaluation suites
    headers := trainloop.TrainloopTag("code-generation")
    response, err := MakeAIRequest(promptText, "gpt-4", 500, headers)
    if err != nil {
        log.Fatalf("Error: %v", err)
    }
    
    fmt.Printf("AI Response: %s\n", response)
}
```

## Important Notes

### Import Path

Use the GitHub import path for the TrainLoop SDK:

```go
import trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
```

### Initialization Order

The `trainloop.Collect()` call must happen in `init()` before any AI requests:

```go
func init() {
    trainloop.Collect()
}
```

## Expected Output

When you run the examples, you'll see:

```
AI Response: def factorial(n):
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)
```

## Project Structure

```
go/
├── ai_request.go          # AI request utility functions
├── writes_valid_code.go   # Code generation example
├── counter_agent.go       # Letter counting example
├── go.mod                 # Go module definition
├── go.sum                 # Go module checksums
└── trainloop/            # Evaluation configuration
    ├── eval/
    │   ├── metrics/      # Custom metrics
    │   └── suites/       # Evaluation suites
    └── data/
        ├── events/       # Collected LLM interactions
        └── results/      # Evaluation results
```

## Next Steps

- [View Python Examples](../python/getting-started.md)
- [View TypeScript Examples](../typescript/getting-started.md)
- [Learn about Custom Metrics](../../tutorials/advanced-metrics.md)