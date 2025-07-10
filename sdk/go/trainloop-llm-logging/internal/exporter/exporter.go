package exporter

import (
	"sync"
	"time"

	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/logger"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/store"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/types"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/utils"
)

var log = logger.CreateLogger("trainloop-exporter")

// FileExporter buffers and flushes LLM call data.
type FileExporter struct {
	buf             []types.LLMCallData
	lock            sync.Mutex
	flushInterval   time.Duration
	batchSize       int
	ticker          *time.Ticker
	shutdownChan    chan struct{}
	wg              sync.WaitGroup
	dataDirProvider func() string // Function to get TRAINLOOP_DATA_FOLDER
}

// NewFileExporter creates a new FileExporter.
// interval and batchLen are in seconds and number of calls, respectively.
func NewFileExporter(intervalSec int, batchLen int, dataDirFunc func() string) *FileExporter {
	if intervalSec <= 0 {
		intervalSec = 10
	}
	if batchLen <= 0 {
		batchLen = 5
	}

	exporter := &FileExporter{
		buf:             make([]types.LLMCallData, 0, batchLen),
		flushInterval:   time.Duration(intervalSec) * time.Second,
		batchSize:       batchLen,
		shutdownChan:    make(chan struct{}),
		dataDirProvider: dataDirFunc,
	}

	exporter.wg.Add(1)
	go exporter.flushLoop()

	return exporter
}

// RecordLLMCall adds an LLM call to the buffer.
func (e *FileExporter) RecordLLMCall(call types.LLMCallData) {
	log.Info("Recording LLM call: %s", call.URL)
	if !call.IsLLMRequest {
		return
	}

	e.lock.Lock()
	e.buf = append(e.buf, call)
	shouldFlush := len(e.buf) >= e.batchSize
	e.lock.Unlock()

	if shouldFlush {
		// Trigger immediate flush non-blockingly if possible, or let ticker handle it
		// For simplicity, we'll let the ticker or shutdown handle it,
		// or you can add a dedicated channel to trigger flushes.
		log.Debug("Buffer reached batch size, will flush on next cycle or manual flush.")
	}
}

func (e *FileExporter) export() {
	e.lock.Lock()
	if len(e.buf) == 0 {
		e.lock.Unlock()
		return
	}
	// Create a copy of the buffer to export, then clear original
	callsToExport := make([]types.LLMCallData, len(e.buf))
	copy(callsToExport, e.buf)
	e.buf = e.buf[:0] // Clear buffer
	e.lock.Unlock()

	log.Info("Exporting %d calls", len(callsToExport))
	dataDir := e.dataDirProvider()
	if dataDir == "" {
		log.Warn("TRAINLOOP_DATA_FOLDER not set - export skipped")
		return
	}

	var samples []types.CollectedSample
	for _, llmCall := range callsToExport {
		log.Debug("Processing LLM call for export: %s", llmCall.URL)

		// Use FormatStreamedContent for response body before parsing
		formattedRespBodyBytes := utils.FormatStreamedContent([]byte(llmCall.ResponseBodyStr))
		parsedRequest := utils.ParseRequestBody(llmCall.RequestBodyStr)
		parsedResponse := utils.ParseResponseBody(string(formattedRespBodyBytes))

		if parsedRequest == nil || parsedResponse == nil {
			log.Warn("Invalid request (%v) or response (%v) for URL %s - skipping", parsedRequest == nil, parsedResponse == nil, llmCall.URL)
			continue
		}

		loc := llmCall.Location
		if loc.File == "" { // If location wasn't properly captured
			loc = utils.CallerSite() // Try to get it again, though might point here
		}
		tag := llmCall.Tag
		if tag == "" {
			tag = "untagged"
		}

		store.UpdateRegistry(dataDir, loc, tag)
		log.Debug("Updated registry for call to %s", llmCall.URL)

		startTimeMs := llmCall.StartTime.UnixNano() / 1e6
		endTimeMs := llmCall.EndTime.UnixNano() / 1e6
		durationMs := endTimeMs - startTimeMs
		if durationMs < 0 {
			durationMs = 0
		}

		sample := types.CollectedSample{
			DurationMs:  durationMs,
			Tag:         llmCall.Tag,
			Input:       parsedRequest.Messages,
			Output:      parsedResponse,
			Model:       parsedRequest.Model,
			ModelParams: parsedRequest.ModelParams,
			StartTimeMs: startTimeMs,
			EndTimeMs:   endTimeMs,
			URL:         llmCall.URL,
			Location:    loc,
		}
		samples = append(samples, sample)
	}

	if len(samples) > 0 {
		store.SaveSamples(dataDir, samples)
	}
}

func (e *FileExporter) flushLoop() {
	defer e.wg.Done()
	e.ticker = time.NewTicker(e.flushInterval)
	defer e.ticker.Stop()

	for {
		select {
		case <-e.ticker.C:
			log.Debug("Flush ticker fired")
			e.export()
		case <-e.shutdownChan:
			log.Info("Shutdown signal received, performing final export.")
			e.export() // Perform a final export
			return
		}
	}
}

// Flush forces an export of any buffered calls.
func (e *FileExporter) Flush() {
	log.Info("Manual flush requested.")
	e.export()
}

// Shutdown performs a final flush and stops the exporter.
func (e *FileExporter) Shutdown() {
	log.Info("Shutting down FileExporter...")
	close(e.shutdownChan) // Signal the flushLoop to stop
	e.wg.Wait()           // Wait for flushLoop to finish
	log.Info("FileExporter shut down.")
}
