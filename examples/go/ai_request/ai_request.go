package ai_request

import (
	"context"
	"fmt"
	"net/http"
	"os"

	"github.com/joho/godotenv"
	"github.com/sashabaranov/go-openai"
)

func init() {
	godotenv.Load()
}

// MakeAIRequest makes a request to the OpenAI API using the specified model and prompt.
// The TrainLoop SDK automatically captures OpenAI requests for evaluation.
//
// Parameters:
//   - prompt: The prompt string to send to the model
//   - model: The model ID to use for the request (defaults to "gpt-4")
//   - maxTokens: Maximum number of tokens to generate in the response
//   - extraHeaders: Additional headers to pass with the request (e.g., for tagging)
//
// Returns the AI's response as a string, or an error if the request fails.
func MakeAIRequest(prompt, model string, maxTokens int, extraHeaders map[string]string) (string, error) {
	if model == "" {
		model = "gpt-4"
	}

	apiKey := os.Getenv("OPENAI_API_KEY")
	if apiKey == "" {
		return "", fmt.Errorf("OPENAI_API_KEY environment variable is not set")
	}

	// Create client with optional custom transport for tagging
	var client *openai.Client
	if len(extraHeaders) > 0 {
		// Create HTTP client with tagged headers for this request
		httpClient := &http.Client{
			Transport: &taggedTransport{extraHeaders: extraHeaders},
		}
		config := openai.DefaultConfig(apiKey)
		config.HTTPClient = httpClient
		client = openai.NewClientWithConfig(config)
	} else {
		// Standard client - SDK will still capture OpenAI requests automatically
		client = openai.NewClient(apiKey)
	}

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

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response choices returned")
	}

	return resp.Choices[0].Message.Content, nil
}

// taggedTransport is a simple transport wrapper that adds TrainLoop tags to requests
type taggedTransport struct {
	extraHeaders map[string]string
}

func (t *taggedTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	// Add extra headers (typically TrainLoop tags) to the request
	for key, value := range t.extraHeaders {
		req.Header.Set(key, value)
	}
	// Use the default transport which is already instrumented by the SDK
	return http.DefaultTransport.RoundTrip(req)
}