---
sidebar_position: 1
---

# Go SDK API

Complete API reference for the TrainLoop Go SDK.

## Installation

```bash
go get github.com/trainloop/evals/sdk/go/trainloop-llm-logging
```

## Basic Usage

```go
package main

import (
    "context"
    "fmt"
    "log"
    "os"
    
    "github.com/sashabaranov/go-openai"
    trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

func main() {
    // Initialize TrainLoop
    trainloop.Init()
    defer trainloop.Shutdown()
    
    // Use with OpenAI
    client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))
    
    resp, err := client.CreateChatCompletion(
        context.Background(),
        openai.ChatCompletionRequest{
            Model: openai.GPT4OMini,
            Messages: []openai.ChatCompletionMessage{
                {Role: openai.ChatMessageRoleUser, Content: "Hello"},
            },
        },
    )
    
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Println(resp.Choices[0].Message.Content)
}
```

## API Reference

### Init(options ...Option)

Initialize TrainLoop data collection.

**Parameters**:
- `options` ([]Option): Configuration options

**Example**:
```go
// Basic initialization
trainloop.Init()

// With options
trainloop.Init(
    trainloop.WithDataFolder("./custom-data"),
    trainloop.WithFlushImmediately(true),
    trainloop.WithTags([]string{"production"}),
)
```

### Shutdown()

Gracefully shutdown TrainLoop and flush buffered events.

**Example**:
```go
defer trainloop.Shutdown()
```

### TrainloopTag(tag string) map[string]string

Create headers with TrainLoop tags for HTTP requests.

**Parameters**:
- `tag` (string): Tag name

**Returns**: Map of headers for HTTP requests

**Example**:
```go
// Basic tagging
headers := trainloop.TrainloopTag("greeting")
headers2 := trainloop.TrainloopTag("customer-support")

// Use with your HTTP client
// Add headers to your request as needed
```

### Collect(ctx context.Context, data interface{})

Manually collect event data.

**Parameters**:
- `ctx` (context.Context): Request context
- `data` (interface{}): Event data

**Example**:
```go
// Collect custom event
trainloop.Collect(ctx, map[string]interface{}{
    "event_type": "custom",
    "data": "some data",
})
```

## Configuration Options

### WithDataFolder(folder string)

Set custom data folder.

```go
trainloop.Init(trainloop.WithDataFolder("/custom/path"))
```

### WithFlushImmediately(enabled bool)

Enable/disable immediate flushing.

```go
trainloop.Init(trainloop.WithFlushImmediately(true))
```

### WithTags(tags []string)

Set default tags for all events.

```go
trainloop.Init(trainloop.WithTags([]string{"production", "v1.0"}))
```

### WithBufferSize(size int)

Set buffer size for batching.

```go
trainloop.Init(trainloop.WithBufferSize(100))
```

### WithBufferTimeout(timeout time.Duration)

Set buffer timeout.

```go
import "time"

trainloop.Init(trainloop.WithBufferTimeout(30 * time.Second))
```

## Supported Libraries

The Go SDK automatically instruments:

- **OpenAI** (`github.com/sashabaranov/go-openai`)
- **Standard HTTP client** (`net/http`)
- **Custom HTTP clients** (via context)

## Environment Variables

```bash
export TRAINLOOP_DATA_FOLDER="./data"
export TRAINLOOP_FLUSH_IMMEDIATELY=true
export TRAINLOOP_TAGS="production,v1.0"
```

## Advanced Usage

### Custom HTTP Client

```go
import (
    "net/http"
    "time"
    
    trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

func main() {
    trainloop.Init()
    defer trainloop.Shutdown()
    
    // Custom HTTP client
    client := &http.Client{
        Timeout: 30 * time.Second,
        Transport: trainloop.NewRoundTripper(http.DefaultTransport),
    }
    
    // Use tagged context
    ctx := trainloop.TrainloopTag("custom-http", nil)
    req, _ := http.NewRequestWithContext(ctx, "GET", "https://api.example.com", nil)
    
    resp, err := client.Do(req)
    if err != nil {
        log.Fatal(err)
    }
    defer resp.Body.Close()
}
```

### Conditional Instrumentation

```go
import "os"

func main() {
    // Only instrument in production
    if os.Getenv("ENVIRONMENT") == "production" {
        trainloop.Init()
        defer trainloop.Shutdown()
    }
}
```

### Error Handling

```go
func main() {
    err := trainloop.Init()
    if err != nil {
        log.Printf("TrainLoop initialization failed: %v", err)
        // Continue without instrumentation
    } else {
        defer trainloop.Shutdown()
    }
}
```

## Examples

### OpenAI Chat Completion

```go
package main

import (
    "context"
    "fmt"
    "log"
    "os"
    
    "github.com/sashabaranov/go-openai"
    trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

func main() {
    trainloop.Init()
    defer trainloop.Shutdown()
    
    client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))
    
    resp, err := client.CreateChatCompletion(
        context.Background(),
        openai.ChatCompletionRequest{
            Model: openai.GPT4OMini,
            Messages: []openai.ChatCompletionMessage{
                {Role: openai.ChatMessageRoleSystem, Content: "You are a helpful assistant."},
                {Role: openai.ChatMessageRoleUser, Content: "What is the capital of France?"},
            },
        },
    )
    
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Println(resp.Choices[0].Message.Content)
}
```

### HTTP Server with TrainLoop

```go
package main

import (
    "context"
    "encoding/json"
    "net/http"
    "os"
    
    "github.com/sashabaranov/go-openai"
    trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

type ChatRequest struct {
    Messages []openai.ChatCompletionMessage `json:"messages"`
}

func main() {
    trainloop.Init()
    defer trainloop.Shutdown()
    
    client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))
    
    http.HandleFunc("/chat", func(w http.ResponseWriter, r *http.Request) {
        var req ChatRequest
        json.NewDecoder(r.Body).Decode(&req)
        
        // Tag the request
        ctx := trainloop.TrainloopTag("chat-api", map[string]string{
            "endpoint": "/chat",
            "method": r.Method,
        })
        
        resp, err := client.CreateChatCompletionWithContext(
            ctx,
            openai.ChatCompletionRequest{
                Model: openai.GPT4OMini,
                Messages: req.Messages,
            },
        )
        
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        
        json.NewEncoder(w).Encode(resp)
    })
    
    http.ListenAndServe(":8080", nil)
}
```

### Concurrent Requests

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "os"
    
    "github.com/sashabaranov/go-openai"
    trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

func main() {
    trainloop.Init()
    defer trainloop.Shutdown()
    
    client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))
    
    var wg sync.WaitGroup
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            
            ctx := trainloop.TrainloopTag("concurrent", map[string]string{
                "worker_id": fmt.Sprintf("%d", id),
            })
            
            resp, err := client.CreateChatCompletionWithContext(
                ctx,
                openai.ChatCompletionRequest{
                    Model: openai.GPT4OMini,
                    Messages: []openai.ChatCompletionMessage{
                        {Role: openai.ChatMessageRoleUser, Content: fmt.Sprintf("Hello from worker %d", id)},
                    },
                },
            )
            
            if err != nil {
                fmt.Printf("Worker %d error: %v\n", id, err)
                return
            }
            
            fmt.Printf("Worker %d: %s\n", id, resp.Choices[0].Message.Content)
        }(i)
    }
    
    wg.Wait()
}
```

## Troubleshooting

### Common Issues

**Module not found**: Run `go get github.com/trainloop/evals/sdk/go/trainloop-llm-logging`

**No data collected**: Check that `TRAINLOOP_DATA_FOLDER` is set and writable

**High memory usage**: Enable `WithFlushImmediately(true)` for high-volume applications

**Missing events**: Ensure `Init()` is called before making HTTP requests

### Debug Mode

```go
import "log"

func main() {
    // Enable debug logging
    trainloop.Init(trainloop.WithDebug(true))
    defer trainloop.Shutdown()
}
```

## See Also

- [SDK Overview](../index.md) - Multi-language SDK documentation
- [Getting Started](../../../tutorials/getting-started.md) - Complete setup guide
- [Python SDK](../python/api.md) - Python API reference
- [TypeScript SDK](../typescript/api.md) - TypeScript API reference