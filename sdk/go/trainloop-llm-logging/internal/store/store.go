package store

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/logger"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/types"
)

var log = logger.CreateLogger("trainloop-store")

func nowISO() string {
	return time.Now().UTC().Format(time.RFC3339) // ISO 8601 format
}

// UpdateRegistry updates the _registry.json file.
func UpdateRegistry(dataDir string, loc types.LLMCallLocation, tag string) {
	registryPath := filepath.Join(dataDir, "_registry.json")
	log.Debug("Updating registry at %s", registryPath)

	var reg types.Registry
	if _, err := os.Stat(registryPath); err == nil {
		data, err := os.ReadFile(registryPath)
		if err == nil {
			// Check if data is empty or just "{}", which can happen
			if len(data) == 0 || string(data) == "{}" {
				log.Debug("Registry file is empty or '{}', initializing new registry.")
				reg.Schema = 1
				reg.Files = make(map[string]map[string]types.RegistryEntry)
			} else if err := json.Unmarshal(data, &reg); err != nil {
				log.Error("Corrupt registry file at %s - recreating. Error: %v", registryPath, err)
				reg.Schema = 1
				reg.Files = make(map[string]map[string]types.RegistryEntry)
			} else if reg.Files == nil { // Ensure Files map is initialized
				reg.Files = make(map[string]map[string]types.RegistryEntry)
			}
		} else {
			log.Error("Failed to read existing registry file at %s - recreating. Error: %v", registryPath, err)
			reg.Schema = 1
			reg.Files = make(map[string]map[string]types.RegistryEntry)
		}
	} else {
		log.Debug("Registry file not found at %s, creating new registry.", registryPath)
		reg.Schema = 1
		reg.Files = make(map[string]map[string]types.RegistryEntry)
	}

	if loc.File == "" { // Sanitize location
		loc.File = "unknown"
	}
	if loc.LineNumber == "" {
		loc.LineNumber = "0"
	}

	if _, ok := reg.Files[loc.File]; !ok {
		reg.Files[loc.File] = make(map[string]types.RegistryEntry)
	}

	fileEntries := reg.Files[loc.File]
	now := nowISO()

	entry, exists := fileEntries[loc.LineNumber]
	if exists {
		if entry.Tag != tag { // Tag changed in source
			entry.Tag = tag
		}
		entry.LastSeen = now
		entry.Count++
	} else {
		entry = types.RegistryEntry{
			LineNumber: loc.LineNumber,
			Tag:        tag,
			FirstSeen:  now,
			LastSeen:   now,
			Count:      1,
		}
	}
	fileEntries[loc.LineNumber] = entry

	if err := os.MkdirAll(filepath.Dir(registryPath), 0755); err != nil {
		log.Error("Failed to create directory for registry: %v", err)
		return
	}

	data, err := json.MarshalIndent(reg, "", "  ")
	if err != nil {
		log.Error("Failed to marshal registry: %v", err)
		return
	}

	if err := os.WriteFile(registryPath, data, 0644); err != nil {
		log.Error("Failed to write registry file: %v", err)
		return
	}
	log.Debug("Registry written - %s:%s = %s (count=%d)", loc.File, loc.LineNumber, entry.Tag, entry.Count)
}

// SaveSamples appends samples to a JSONL event file.
func SaveSamples(dataDir string, samples []types.CollectedSample) {
	if len(samples) == 0 {
		return
	}
	eventDir := filepath.Join(dataDir, "events")
	if err := os.MkdirAll(eventDir, 0755); err != nil {
		log.Error("Failed to create events directory %s: %v", eventDir, err)
		return
	}

	nowMs := time.Now().UnixNano() / 1e6
	windowMs := int64(10 * 60 * 1000) // 10 minutes in milliseconds

	// Find the most recent timestamped file
	var latestTimestampMs int64 = 0
	files, err := os.ReadDir(eventDir)
	if err != nil {
		log.Warn("Failed to read event directory %s: %v", eventDir, err)
	} else {
		var timestamps []int64
		for _, file := range files {
			if !file.IsDir() && strings.HasSuffix(file.Name(), ".jsonl") {
				tsStr := strings.TrimSuffix(file.Name(), ".jsonl")
				ts, err := strconv.ParseInt(tsStr, 10, 64)
				if err == nil {
					timestamps = append(timestamps, ts)
				}
			}
		}
		if len(timestamps) > 0 {
			sort.Slice(timestamps, func(i, j int) bool { return timestamps[i] > timestamps[j] })
			latestTimestampMs = timestamps[0]
		}
	}

	targetTimestampMs := nowMs
	if latestTimestampMs > 0 && (nowMs-latestTimestampMs) < windowMs {
		targetTimestampMs = latestTimestampMs
	}

	eventFilePath := filepath.Join(eventDir, fmt.Sprintf("%d.jsonl", targetTimestampMs))
	file, err := os.OpenFile(eventFilePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Error("Failed to open event file %s: %v", eventFilePath, err)
		return
	}
	defer file.Close()

	for _, s := range samples {
		jsonData, err := json.Marshal(s)
		if err != nil {
			log.Warn("Failed to marshal sample to JSON: %v, Sample: %+v", err, s)
			continue
		}
		if _, err := file.Write(append(jsonData, '\n')); err != nil {
			log.Error("Failed to write sample to event file %s: %v", eventFilePath, err)
			// Potentially stop or handle error more gracefully
		}
	}
	log.Debug("Saved %d samples to %s", len(samples), eventFilePath)
}
