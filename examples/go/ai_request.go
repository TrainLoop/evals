package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	"github.com/sashabaranov/go-openai"
)

func init() {
	godotenv.Load()
}

// MakeAIRequest makes a request to the OpenAI API using the specified model and prompt.
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

	client := openai.NewClient(apiKey)

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

// Example usage function (commented out so this can be used as a library)
// func main() {
// 	response, err := MakeAIRequest("Hello, world!", "gpt-4", 100, nil)
// 	if err != nil {
// 		log.Fatalf("Error: %v", err)
// 	}
// 	fmt.Printf("AI Response: %s\n", response)
// }