package main

import (
	"fmt"
	"log"

	trainloop "trainloop-llm-logging"
)

func init() {
	// Notice that this is imported and called BEFORE the AI request!
	// This is critical for collecting data.
	trainloop.Collect()
}

func main() {
	promptText := `Write a Python function that calculates the factorial of a number recursively. 
The function should be named 'factorial' and take one parameter 'n'. 
It should return 1 if n is 0 or 1, and n * factorial(n-1) otherwise.
Include proper error handling for negative numbers.
Output only the code in a single code block, no explanations.`

	// Tag this request for the code generation evaluation suite
	headers := trainloop.TrainloopTag("code-generation")
	response, err := MakeAIRequest(promptText, "gpt-4", 500, headers)
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	fmt.Printf("AI Response: %s\n", response)
}