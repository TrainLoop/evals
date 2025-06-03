# TrainLoop Evals SDK (Go)

Automatically capture LLM calls from Go applications so they can be graded later. This SDK instruments the standard `net/http` package to log requests to common LLM providers.

## Installation

```bash
go get github.com/TrainLoop/evals/sdk/go/trainloop-llm-logging
```

This will add the TrainLoop SDK to your `go.mod` file and download the necessary dependencies.

## Quick Example

Modify your application's entry point (`main.go` or similar) to initialize the SDK:

```go
package main

import (
	"log"
	"net/http"
	"os"
	"time"

	trainloop "github.com/TrainLoop/evals/sdk/go/trainloop-llm-logging"
)

func main() {
	// Initialize the TrainLoop SDK.
	// This will instrument http.DefaultTransport.
	// Call this early in your application's lifecycle.
	trainloop.Collect() // Optionally, pass a path to trainloop.config.yaml: trainloop.Collect("./custom/trainloop.config.yaml")

	// Defer Shutdown to ensure any buffered data is flushed before the application exits.
	defer trainloop.Shutdown()

	// Example: Make an HTTP request using the default client.
	// This request will be captured if the host (api.openai.com) is in the allowlist.
	log.Println("Making a request to OpenAI...")
	_, err := http.Get("https://api.openai.com/v1/models") // Example LLM API URL
	if err != nil {
		log.Printf("HTTP Get error: %v", err)
	}

	// Example: Tagging a specific call
	log.Println("Making a tagged request to Anthropic...")
	client := &http.Client{}
	req, _ := http.NewRequest("POST", "https://api.anthropic.com/v1/messages", nil) // Example LLM API URL

	// Add the TrainLoop tag to the request headers
	trainloop.AddTrainloopTagToHeaders(req.Header, "my-custom-anthropic-call")
	// Alternatively, for more complex header manipulation:
	// tags := trainloop.TrainloopTag("my-custom-anthropic-call")
	// req.Header.Set(trainloop.HeaderName, tags[trainloop.HeaderName])

	_, err = client.Do(req)
	if err != nil {
		log.Printf("HTTP Do error with tag: %v", err)
	}

	log.Println("Application finished. TrainLoop SDK will flush remaining data on shutdown.")
	// In a real application, proper signal handling should call trainloop.Shutdown()
}
```

## Configuration

The SDK can be configured using environment variables or a `trainloop.config.yaml` file. Environment variables take precedence.

**Environment Variables:**

*   `TRAINLOOP_DATA_FOLDER`: (Required) Path to the directory where event files and the registry will be written. If not set, the SDK will be disabled.
*   `TRAINLOOP_HOST_ALLOWLIST`: Comma-separated list of hostnames to monitor (e.g., `api.openai.com,api.anthropic.com`). Defaults to `api.openai.com,api.anthropic.com`.
*   `TRAINLOOP_LOG_LEVEL`: Logging level for the SDK itself (e.g., `DEBUG`, `INFO`, `WARN`, `ERROR`). Defaults to `WARN`.
*   `TRAINLOOP_CONFIG_PATH`: Optional path to a `trainloop.config.yaml` file. If not set, the SDK looks for `trainloop/trainloop.config.yaml` or `./trainloop.config.yaml` relative to the current working directory.

**`trainloop.config.yaml` file:**

Create this file in your project (e.g., at the root or in a `trainloop/` subdirectory).

```yaml
trainloop:
  data_folder: "./trainloop_data"  # Relative paths are resolved from the config file's location or CWD
  host_allowlist:
    - "api.openai.com"
    - "api.anthropic.com"
  log_level: "INFO"
```

## Tagging Calls

To distinguish between different LLM calls in your application, you can add a tag to the HTTP request headers:

```go
import (
	"net/http"
	trainloop "github.com/TrainLoop/evals/sdk/go/trainloop-llm-logging"
)

// ...

req, _ := http.NewRequest("POST", "https://api.some-llm.com/complete", myRequestBody)

// Add the tag
trainloop.AddTrainloopTagToHeaders(req.Header, "summarize-article-v2")

// Or, if you need the tag as a map for other header construction:
// tagHeader := trainloop.TrainloopTag("summarize-article-v2")
// req.Header.Set(trainloop.HeaderName, tagHeader[trainloop.HeaderName])

client := &http.Client{}
resp, err := client.Do(req)
// ...
```

The tag will be associated with the logged call in the `_registry.json` and the event files.

## How it Works

The `trainloop.Collect()` function patches the `http.DefaultTransport`. This means that any HTTP requests made using the standard Go `http.Client` (when not configured with a custom `Transport`) or convenience functions like `http.Get()` and `http.Post()` will be automatically instrumented.

The SDK captures:
*   Request and response bodies (truncated if very large).
*   Request URL, method, and status code.
*   Call duration.
*   The call site (file and line number) in your code that initiated the HTTP request.
*   Any `X-Trainloop-Tag` header.

## Output

*   **Event Logs**: LLM call data is saved in JSONL format (`.jsonl` files) within the `events/` subdirectory of your `TRAINLOOP_DATA_FOLDER`. Files are sharded by timestamp.
*   **Registry**: A `_registry.json` file is maintained in the `TRAINLOOP_DATA_FOLDER`, mapping call locations (file and line number) to their tags and usage counts.

See the [project README](../../../README.md) for more context.