package instrumentation

import (
	"sync"

	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/exporter"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/logger"
)

var tlLog = logger.CreateLogger("trainloop-instrumentation")
var once sync.Once
var installed bool = false

// InstallAllPatches initializes all available instrumentations.
func InstallAllPatches(exp *exporter.FileExporter, hostAllowlist []string) {
	once.Do(func() {
		InstallPatches(exp, hostAllowlist)
		// Add other instrumentations here if any (e.g., gRPC)
		installed = true
		tlLog.Info("All instrumentations installed.")
	})
	if installed {
		tlLog.Debug("Instrumentation already installed.")
	}
}
