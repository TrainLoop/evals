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
	sentence := "I love strawberries"
	promptText := fmt.Sprintf(`
Count the occurrences of each letter in the following sentence: <sentence>%s</sentence>.
Output your answer in a code block with each letter and its count on a separate line.
Use the exact format: <letter> - <count>
Only include letters that appear in the word.
Sort the letters alphabetically.
`, sentence)

	// Tag this request for the letter counting evaluation suite
	headers := trainloop.TrainloopTag("letter-counting")
	response, err := MakeAIRequest(promptText, "gpt-4", 500, headers)
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	fmt.Printf("AI Response: %s\n", response)
}