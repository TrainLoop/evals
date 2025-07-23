package main

import (
	"net/http"
	"os"
	"sync"

	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/instrumentation"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/config"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/exporter"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/logger"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/utils"
)

var (
	globalExporter *exporter.FileExporter
	isInitialized  bool
	initLock       sync.Mutex
	sdkLog         = logger.CreateLogger("trainloop-sdk")
)

// HeaderName is the name of the HTTP header used for tagging.
const HeaderName = utils.HeaderName

// TrainloopTag creates a map containing the Trainloop tag, suitable for merging into HTTP headers.
func TrainloopTag(tag string) map[string]string {
	return map[string]string{
		HeaderName: tag,
	}
}

// AddTrainloopTagToHeaders is a convenience function to add the trainloop tag to an http.Header object.
func AddTrainloopTagToHeaders(headers http.Header, tag string) {
	if headers == nil {
		return
	}
	headers.Set(HeaderName, tag)
}

// Collect initializes the TrainLoop LLM Logging SDK.
// It loads configuration, sets up an exporter, and installs patches.
// It is idempotent and safe to call multiple times.
// trainloopConfigPathOpt is an optional path to the configuration file.
func Collect(trainloopConfigPathOpt ...string) {
	initLock.Lock()
	defer initLock.Unlock()

	if isInitialized {
		sdkLog.Debug("TrainLoop SDK already initialized.")
		return
	}

	var configPath string
	if len(trainloopConfigPathOpt) > 0 {
		configPath = trainloopConfigPathOpt[0]
	}
	config.LoadConfigIntoEnv(configPath) // Loads config and sets env vars

	// SDK is disabled if TRAINLOOP_DATA_FOLDER is not set.
	dataFolder := os.Getenv("TRAINLOOP_DATA_FOLDER")
	if dataFolder == "" {
		sdkLog.Warn("TRAINLOOP_DATA_FOLDER not set - TrainLoop SDK disabled.")
		// Do not set isInitialized to true, so it can be retried if env changes.
		return
	}
	sdkLog.Info("TRAINLOOP_DATA_FOLDER set to: %s", dataFolder)

	// Initialize the global exporter
	// Pass a function to get TRAINLOOP_DATA_FOLDER dynamically,
	// as it might be set by LoadConfigIntoEnv after NewFileExporter is called.
	dataDirFunc := func() string { return os.Getenv("TRAINLOOP_DATA_FOLDER") }
	globalExporter = exporter.NewFileExporter(10, 5, dataDirFunc) // 10s interval, 5 items batch

	// Install patches
	hostAllowlist := config.GetHostAllowlist()
	instrumentation.InstallAllPatches(globalExporter, hostAllowlist)

	isInitialized = true
	sdkLog.Info("TrainLoop Evals SDK initialized successfully.")
}

// Shutdown gracefully shuts down the SDK, flushing any pending data.
// It's good practice to call this before your application exits.
func Shutdown() {
	initLock.Lock() // Ensure synchronized access to globalExporter
	defer initLock.Unlock()

	if !isInitialized || globalExporter == nil {
		sdkLog.Info("TrainLoop SDK not initialized or already shut down.")
		return
	}

	sdkLog.Info("Shutting down TrainLoop SDK...")
	globalExporter.Shutdown()
	globalExporter = nil  // Allow re-initialization if needed, though typically not
	isInitialized = false // Reset for potential re-init in some scenarios (e.g. tests)
	sdkLog.Info("TrainLoop SDK shut down complete.")
}

// GetGlobalExporter returns the shared global exporter instance.
// This is mostly for internal use or advanced scenarios.
func GetGlobalExporter() *exporter.FileExporter {
	return globalExporter
}
