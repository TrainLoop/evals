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

	passive := "The quarterly report was prepared by the finance team."
	prompt := fmt.Sprintf(`Rewrite the sentence below in ACTIVE voice, preserving meaning.  
Sentence: "%s"
Only output the rewritten sentence.`, passive)

	// Tag this request for the active voice evaluation suite
	headers := trainloop.TrainloopTag("active-voice")

	result, err := ai_request.MakeAIRequest(prompt, "gpt-4o-mini", 500, headers)
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	fmt.Printf("AI Response: %s\n", result)
}
