---
sidebar_position: 4
---

# Go SDK API

The TrainLoop Evals Go SDK provides zero-touch instrumentation for Go applications.

## Installation

```bash
go get github.com/trainloop/sdk-go
```

## Quick Start

```go
package main

import (
    "context"
    "log"
    
    "github.com/trainloop/sdk-go"
    "github.com/sashabaranov/go-openai"
)

func main() {
    // Initialize the SDK
    trainloop.Init(trainloop.Config{
        Endpoint: "http://localhost:8000",
    })

    // Your LLM calls are automatically instrumented
    client := openai.NewClient("your-api-key")
    resp, err := client.CreateChatCompletion(
        context.Background(),
        openai.ChatCompletionRequest{
            Model: openai.GPT4,
            Messages: []openai.ChatCompletionMessage{
                {Role: openai.ChatMessageRoleUser, Content: "Hello, world!"},
            },
        },
    )
    if err != nil {
        log.Fatal(err)
    }
    
    log.Println(resp.Choices[0].Message.Content)
}
```

## Configuration

The SDK can be configured using environment variables or initialization parameters:

### Environment Variables

- `TRAINLOOP_ENDPOINT` - The endpoint to send traces to (default: `http://localhost:8000`)
- `TRAINLOOP_API_KEY` - API key for authentication (optional)
- `TRAINLOOP_DEBUG` - Enable debug logging (default: `false`)

### Initialization Parameters

```go
trainloop.Init(trainloop.Config{
    Endpoint: "http://localhost:8000",
    APIKey:   "your-api-key",
    Debug:    true,
})
```

## Supported Libraries

The Go SDK automatically instruments the following libraries:

- go-openai
- Custom HTTP clients

## Manual Instrumentation

For custom instrumentation, you can use the manual tracing API:

```go
span := trainloop.StartTrace("my-llm-call")
span.SetInput(map[string]interface{}{
    "prompt": "Hello, world!",
})
// Your LLM call here
span.SetOutput(map[string]interface{}{
    "response": "Hello! How can I help you?",
})
span.Finish()
```