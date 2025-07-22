package main

import (
	"fmt"
	"log"

	"trainloop-go-examples/ai_request"
	trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

func init() {
	// Notice that this is imported and called BEFORE the AI request!
	// This is critical for collecting data.
	trainloop.Collect()
}

func main() {
	// Ensure data is flushed when the program exits
	defer trainloop.Shutdown()

	complaint := "Your package arrived two weeks late and the box was damaged!"
	prompt := fmt.Sprintf(`You are a customer-support agent.
Reply to the following customer in ≤120 words.
Requirements:
1. Begin with a sincere apology
2. Acknowledge the specific problem
3. Offer a concrete next step or compensation
Customer: "%s"`, complaint)

	// Tag this request for the polite responder evaluation suite
	headers := trainloop.TrainloopTag("polite-responder")

	result, err := ai_request.MakeAIRequest(prompt, "gpt-4o-mini", 500, headers)
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	fmt.Printf("AI Response: %s\n", result)
}
