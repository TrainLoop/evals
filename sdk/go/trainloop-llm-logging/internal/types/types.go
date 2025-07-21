package types

import "time"

// LLMCallLocation stores the file and line number of an LLM call.
type LLMCallLocation struct {
	File       string `json:"file"`
	LineNumber string `json:"lineNumber"`
}

// ParsedResponseBody represents the structured content of an LLM response.
type ParsedResponseBody struct {
	Content string `json:"content"`
}

// ParsedRequestBody represents the structured content of an LLM request.
type ParsedRequestBody struct {
	Messages    []map[string]string `json:"messages"`
	Model       string              `json:"model"`
	ModelParams map[string]any      `json:"modelParams"`
}

// CollectedSample is the structure for storing a single LLM call's data.
type CollectedSample struct {
	DurationMs  int64               `json:"durationMs"`
	Tag         string              `json:"tag"`
	Input       []map[string]string `json:"input"` // This is ParsedRequestBody.Messages
	Output      *ParsedResponseBody `json:"output"`
	Model       string              `json:"model"`
	ModelParams map[string]any      `json:"modelParams"`
	StartTimeMs int64               `json:"startTimeMs"` // Unix timestamp
	EndTimeMs   int64               `json:"endTimeMs"`   // Unix timestamp
	URL         string              `json:"url"`
	Location    LLMCallLocation     `json:"location"`
}

// LLMCallData is used to pass raw call data to the exporter.
type LLMCallData struct {
	RequestBodyStr  string
	ResponseBodyStr string
	URL             string
	Tag             string
	Location        LLMCallLocation
	StartTime       time.Time
	EndTime         time.Time
	IsLLMRequest    bool
	Headers         map[string]string
	Status          int
}

// TrainloopConfigObject represents the 'trainloop' section of the config file.
type TrainloopConfigObject struct {
	DataFolder       string   `yaml:"data_folder"`
	HostAllowlist    []string `yaml:"host_allowlist"`
	LogLevel         string   `yaml:"log_level"`
	FlushImmediately *bool    `yaml:"flush_immediately"`
}

// TrainloopConfig is the top-level structure for the config file.
type TrainloopConfig struct {
	Trainloop TrainloopConfigObject `yaml:"trainloop"`
}

// RegistryEntry stores metadata for a call site in the registry.
type RegistryEntry struct {
	LineNumber string `json:"lineNumber"`
	Tag        string `json:"tag"`
	FirstSeen  string `json:"firstSeen"` // ISO-8601 UTC
	LastSeen   string `json:"lastSeen"`
	Count      int    `json:"count"`
}

// Registry is the structure for the _registry.json file.
type Registry struct {
	Schema int                                 `json:"schema"` // always 1 for now
	Files  map[string]map[string]RegistryEntry `json:"files"`  // file → line → entry
}
