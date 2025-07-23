package storage

import (
	"context"
	"encoding/json"
	"fmt"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"gocloud.dev/blob"
	_ "gocloud.dev/blob/fileblob"
	_ "gocloud.dev/blob/gcsblob"
	_ "gocloud.dev/blob/s3blob"

	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/logger"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/types"
)

var log = logger.CreateLogger("trainloop-cloud-storage")

// openBucket opens a blob bucket for the given path
func openBucket(ctx context.Context, dir string) (*blob.Bucket, error) {
	switch {
	case strings.HasPrefix(dir, "s3://"),
		strings.HasPrefix(dir, "gs://"),
		strings.HasPrefix(dir, "gcp://"),
		strings.HasPrefix(dir, "file://"):
		return blob.OpenBucket(ctx, dir)
	default:
		// bare local path ⇒ turn it into file:// URL
		abs, err := filepath.Abs(dir)
		if err != nil {
			return nil, fmt.Errorf("failed to get absolute path: %w", err)
		}
		abs = filepath.ToSlash(abs)
		return blob.OpenBucket(ctx, "file://"+abs)
	}
}

// nowISO returns current time in ISO 8601 format
func nowISO() string {
	return time.Now().UTC().Format(time.RFC3339)
}

// UpdateRegistry updates the _registry.json file using cloud storage
func UpdateRegistry(ctx context.Context, dataDir string, loc types.LLMCallLocation, tag string) error {
	log.Debug("Updating registry with cloud storage: %s", dataDir)

	bucket, err := openBucket(ctx, dataDir)
	if err != nil {
		return fmt.Errorf("failed to open bucket: %w", err)
	}
	defer bucket.Close()

	registryKey := "_registry.json"

	// Load existing registry
	var reg types.Registry
	exists, err := bucket.Exists(ctx, registryKey)
	if err != nil {
		log.Warn("Error checking if registry exists: %v", err)
	}

	if exists {
		data, err := bucket.ReadAll(ctx, registryKey)
		if err != nil {
			log.Warn("Failed to read existing registry: %v", err)
		} else if len(data) == 0 || string(data) == "{}" {
			log.Debug("Registry file is empty or '{}', initializing new registry.")
			reg.Schema = 1
			reg.Files = make(map[string]map[string]types.RegistryEntry)
		} else if err := json.Unmarshal(data, &reg); err != nil {
			log.Error("Corrupt registry file - recreating. Error: %v", err)
			reg.Schema = 1
			reg.Files = make(map[string]map[string]types.RegistryEntry)
		} else if reg.Files == nil {
			reg.Files = make(map[string]map[string]types.RegistryEntry)
		}
	} else {
		log.Debug("Registry file not found, creating new registry.")
		reg.Schema = 1
		reg.Files = make(map[string]map[string]types.RegistryEntry)
	}

	// Sanitize location
	if loc.File == "" {
		loc.File = "unknown"
	}
	if loc.LineNumber == "" {
		loc.LineNumber = "0"
	}

	// Update registry
	if _, ok := reg.Files[loc.File]; !ok {
		reg.Files[loc.File] = make(map[string]types.RegistryEntry)
	}

	fileEntries := reg.Files[loc.File]
	now := nowISO()

	entry, exists := fileEntries[loc.LineNumber]
	if exists {
		if entry.Tag != tag {
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

	// Write registry back to storage
	data, err := json.MarshalIndent(reg, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal registry: %w", err)
	}

	w, err := bucket.NewWriter(ctx, registryKey, nil)
	if err != nil {
		return fmt.Errorf("failed to create writer for registry: %w", err)
	}

	if _, err := w.Write(data); err != nil {
		w.Close()
		return fmt.Errorf("failed to write registry data: %w", err)
	}

	if err := w.Close(); err != nil {
		return fmt.Errorf("failed to close registry writer: %w", err)
	}

	log.Debug("Registry written to cloud storage - %s:%s = %s (count=%d)", loc.File, loc.LineNumber, entry.Tag, entry.Count)
	return nil
}

// SaveSamples appends samples to a JSONL event file using cloud storage
func SaveSamples(ctx context.Context, dataDir string, samples []types.CollectedSample) error {
	if len(samples) == 0 {
		return nil
	}

	log.Debug("Saving %d samples to cloud storage: %s", len(samples), dataDir)

	bucket, err := openBucket(ctx, dataDir)
	if err != nil {
		return fmt.Errorf("failed to open bucket: %w", err)
	}
	defer bucket.Close()

	nowMs := time.Now().UnixNano() / 1e6
	windowMs := int64(10 * 60 * 1000) // 10 minutes in milliseconds

	// Find the most recent timestamped file
	var latestTimestampMs int64 = 0

	// List files in events/ directory
	eventPrefix := "events/"
	iter := bucket.List(&blob.ListOptions{Prefix: eventPrefix})
	var timestamps []int64

	for {
		obj, err := iter.Next(ctx)
		if err != nil {
			break // End of list or error
		}

		if strings.HasSuffix(obj.Key, ".jsonl") {
			filename := strings.TrimPrefix(obj.Key, eventPrefix)
			tsStr := strings.TrimSuffix(filename, ".jsonl")
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

	targetTimestampMs := nowMs
	if latestTimestampMs > 0 && (nowMs-latestTimestampMs) < windowMs {
		targetTimestampMs = latestTimestampMs
	}

	// Prepare JSONL content
	var lines []string
	for _, s := range samples {
		jsonData, err := json.Marshal(s)
		if err != nil {
			log.Warn("Failed to marshal sample to JSON: %v, Sample: %+v", err, s)
			continue
		}
		lines = append(lines, string(jsonData))
	}

	if len(lines) == 0 {
		return nil
	}

	content := strings.Join(lines, "\n") + "\n"
	eventKey := fmt.Sprintf("events/%d.jsonl", targetTimestampMs)

	// Check if file exists, if so append to it
	exists, err := bucket.Exists(ctx, eventKey)
	if err != nil {
		log.Warn("Error checking if event file exists: %v", err)
	}

	if exists {
		// Read existing content and append
		existingData, err := bucket.ReadAll(ctx, eventKey)
		if err != nil {
			log.Warn("Failed to read existing event file: %v", err)
		} else {
			content = string(existingData) + content
		}
	}

	// Write the content
	w, err := bucket.NewWriter(ctx, eventKey, nil)
	if err != nil {
		return fmt.Errorf("failed to create writer for event file: %w", err)
	}

	if _, err := w.Write([]byte(content)); err != nil {
		w.Close()
		return fmt.Errorf("failed to write event data: %w", err)
	}

	if err := w.Close(); err != nil {
		return fmt.Errorf("failed to close event writer: %w", err)
	}

	log.Debug("Saved %d samples to cloud storage: %s", len(samples), eventKey)
	return nil
}
