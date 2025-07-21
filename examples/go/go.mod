module trainloop-go-examples

go 1.20

require (
	github.com/joho/godotenv v1.4.0
	github.com/sashabaranov/go-openai v1.17.9
	trainloop-llm-logging v0.0.0
)

require (
	github.com/trainloop/evals/sdk/go/trainloop-llm-logging v0.0.0-20250720223115-ce8ded92ad69 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)

replace trainloop-llm-logging => ../../sdk/go/trainloop-llm-logging
