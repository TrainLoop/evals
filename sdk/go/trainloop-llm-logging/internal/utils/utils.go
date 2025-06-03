package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/trainloop/sdk/go/trainloop-llm-logging/internal/logger"
	"github.com/trainloop/sdk/go/trainloop-llm-logging/internal/types"
)

var tlLog = logger.CreateLogger("trainloop-utils")

// HeaderName is the HTTP header used for tagging calls.
const HeaderName = "X-Trainloop-Tag"
const maxBodyBytes = 2 * 1024 * 1024 // 2MB

// NowMs returns the current time in milliseconds since epoch.
func NowMs() int64 {
	return time.Now().UnixNano() / 1e6
}

// CapBody truncates a byte slice to a maximum size.
func CapBody(body []byte) []byte {
	if len(body) > maxBodyBytes {
		return body[:maxBodyBytes]
	}
	return body
}

// CallerSite inspects the call stack to find the user's code location.
func CallerSite() types.LLMCallLocation {
	// Adjust skip value based on where this function is called from.
	// This might need tuning. The goal is to skip SDK internal frames.
	// 0: runtime.Callers
	// 1: CallerSite (this function)
	// 2: The function that called CallerSite (e.g., record_llm_call in exporter, or RoundTrip in http.go)
	// 3: The function in the SDK that triggered the instrumentation (e.g. our RoundTrip wrapper)
	// 4: The user's code that made the HTTP call (potentially, depends on http client internals)
	// We iterate to find a non-SDK file.
	for skip := 3; skip < 15; skip++ {
		pc, file, line, ok := runtime.Caller(skip)
		if !ok {
			break
		}
		funcName := runtime.FuncForPC(pc).Name()

		// Skip Go library paths and SDK internal paths
		// This logic might need to be more robust
		isStdLib := strings.HasPrefix(file, runtime.GOROOT())
		isSDKInternal := strings.Contains(file, "trainloop-sdk-go") || strings.Contains(funcName, "trainloop")

		if !isStdLib && !isSDKInternal {
			return types.LLMCallLocation{File: file, LineNumber: strconv.Itoa(line)}
		}
	}
	return types.LLMCallLocation{File: "unknown", LineNumber: "0"}
}

// ParseRequestBody parses a JSON request body string.
func ParseRequestBody(s string) *types.ParsedRequestBody {
	if s == "" {
		return nil
	}
	var body map[string]any
	err := json.Unmarshal([]byte(s), &body)
	if err != nil {
		tlLog.Warn("Failed to parse request body JSON: %v. Body: %s", err, s)
		return nil
	}

	messagesData, messagesOk := body["messages"]
	modelData, modelOk := body["model"]

	if messagesOk && modelOk {
		var messages []map[string]string
		// Type assertion for messages
		if msgsArray, ok := messagesData.([]any); ok {
			for _, item := range msgsArray {
				if msgMap, ok := item.(map[string]any); ok {
					strMap := make(map[string]string)
					for k, v := range msgMap {
						if vStr, ok := v.(string); ok {
							strMap[k] = vStr
						}
					}
					messages = append(messages, strMap)
				}
			}
		}

		model, _ := modelData.(string)

		// Collect other parameters as modelParams
		modelParams := make(map[string]any)
		for k, v := range body {
			if k != "messages" && k != "model" {
				modelParams[k] = v
			}
		}

		return &types.ParsedRequestBody{
			Messages:    messages,
			Model:       model,
			ModelParams: modelParams,
		}
	}
	tlLog.Warn("Skipping request body due to missing 'messages' or 'model' field: %s", s)
	return nil
}

// ParseResponseBody parses a JSON response body string.
func ParseResponseBody(s string) *types.ParsedResponseBody {
	if s == "" {
		return nil
	}
	var body map[string]any
	err := json.Unmarshal([]byte(s), &body)
	if err != nil {
		tlLog.Warn("Failed to parse response body JSON: %v. Body: %s", err, s)
		return nil
	}

	if contentData, ok := body["content"]; ok {
		if contentStr, ok := contentData.(string); ok {
			return &types.ParsedResponseBody{Content: contentStr}
		}
		// Handle nested content, e.g., {"content": {"content": "text"}}
		if contentMap, ok := contentData.(map[string]any); ok {
			if nestedContent, ok := contentMap["content"].(string); ok {
				return &types.ParsedResponseBody{Content: nestedContent}
			}
		}
	}

	// Try to find content in choices (OpenAI specific)
	if choicesData, ok := body["choices"].([]any); ok && len(choicesData) > 0 {
		if choiceMap, ok := choicesData[0].(map[string]any); ok {
			if messageData, ok := choiceMap["message"].(map[string]any); ok {
				if contentStr, ok := messageData["content"].(string); ok {
					return &types.ParsedResponseBody{Content: contentStr}
				}
			}
			// For streaming delta
			if deltaData, ok := choiceMap["delta"].(map[string]any); ok {
				if contentStr, ok := deltaData["content"].(string); ok {
					// This is usually a chunk, formatter should handle aggregation
					return &types.ParsedResponseBody{Content: contentStr}
				}
			}
		}
	}
	tlLog.Warn("Skipping response body due to missing 'content' field or incompatible structure: %s", s)
	return nil
}

// IsLLMCall checks if the URL hostname is in the allowlist.
func IsLLMCall(urlString string, allowlist []string) bool {
	parsedURL, err := url.Parse(urlString)
	if err != nil {
		tlLog.Debug("Failed to parse URL for LLM check: %s, Error: %v", urlString, err)
		return false
	}
	hostname := parsedURL.Hostname()
	for _, allowedHost := range allowlist {
		if hostname == strings.TrimSpace(allowedHost) {
			return true
		}
	}
	return false
}

// PopTag extracts and removes the X-Trainloop-Tag from headers.
func PopTag(headers http.Header) string {
	tag := headers.Get(HeaderName)
	headers.Del(HeaderName) // Del is case-insensitive for canonical keys
	return tag
}

var (
	openaiStreamRE    = regexp.MustCompile(`(?m)^data:\s*(\{.*?"choices".*?\})\s*$`)
	anthropicStreamRE = regexp.MustCompile(`(?m)^data:\s*(\{.*?"content_block_delta".*?\})\s*$`)
)

// FormatStreamedContent collapses an SSE chat stream into a single JSON blob.
func FormatStreamedContent(rawBody []byte) []byte {
	text := string(rawBody)

	// OpenAI
	if strings.Contains(text, `"chat.completion.chunk"`) {
		var parts []string
		matches := openaiStreamRE.FindAllStringSubmatch(text, -1)
		for _, match := range matches {
			if len(match) > 1 {
				var chunkData struct {
					Choices []struct {
						Delta struct {
							Content string `json:"content"`
						} `json:"delta"`
					} `json:"choices"`
				}
				if err := json.Unmarshal([]byte(match[1]), &chunkData); err == nil {
					if len(chunkData.Choices) > 0 && chunkData.Choices[0].Delta.Content != "" {
						parts = append(parts, chunkData.Choices[0].Delta.Content)
					}
				}
			}
		}
		if len(parts) > 0 {
			content := strings.Join(parts, "")
			out := map[string]string{"content": content}
			if jsonData, err := json.Marshal(out); err == nil {
				return jsonData
			}
		}
	}

	// Anthropic
	if strings.Contains(text, `"content_block_delta"`) {
		var parts []string
		matches := anthropicStreamRE.FindAllStringSubmatch(text, -1)
		for _, match := range matches {
			if len(match) > 1 {
				var chunkData struct {
					Delta struct {
						Text string `json:"text"`
					} `json:"delta"`
					Type string `json:"type"`
				}
				if err := json.Unmarshal([]byte(match[1]), &chunkData); err == nil {
					if chunkData.Type == "content_block_delta" && chunkData.Delta.Text != "" {
						parts = append(parts, chunkData.Delta.Text)
					}
				}
			}
		}
		if len(parts) > 0 {
			content := strings.Join(parts, "")
			out := map[string]string{"content": content}
			if jsonData, err := json.Marshal(out); err == nil {
				return jsonData
			}
		}
	}

	return rawBody // Fallback to original if not a known stream format or parsing fails
}

// ReadAndReplaceBody reads an io.ReadCloser and replaces it with a new one containing the same content.
// This is useful for reading request/response bodies multiple times.
func ReadAndReplaceBody(bodySlot *io.ReadCloser) ([]byte, error) {
	if bodySlot == nil || *bodySlot == nil {
		return nil, nil
	}
	bodyBytes, err := io.ReadAll(*bodySlot)
	(*bodySlot).Close() // Close the original body
	if err != nil {
		return nil, fmt.Errorf("failed to read body: %w", err)
	}
	*bodySlot = io.NopCloser(bytes.NewBuffer(bodyBytes)) // Replace with a new reader
	return bodyBytes, nil
}
