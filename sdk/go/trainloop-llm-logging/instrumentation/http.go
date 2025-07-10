package instrumentation

import (
	"net/http"
	"time"

	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/exporter"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/types"
	"github.com/trainloop/evals/sdk/go/trainloop-llm-logging/internal/utils"
)

var originalDefaultTransport http.RoundTripper
var isPatched bool = false

// trainloopTransport wraps an http.RoundTripper to intercept requests.
type trainloopTransport struct {
	originalTransport http.RoundTripper
	exporter          *exporter.FileExporter
	hostAllowlist     []string
}

// RoundTrip executes a single HTTP transaction, capturing data.
func (t *trainloopTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	tag := utils.PopTag(req.Header) // Removes header if present
	fullURL := req.URL.String()

	// Check if this is an LLM call or has a tag
	isLLM := utils.IsLLMCall(fullURL, t.hostAllowlist)
	if !isLLM && tag == "" {
		return t.originalTransport.RoundTrip(req)
	}

	startTime := time.Now()
	var reqBodyBytes []byte
	var err error

	// Read request body if it exists
	if req.Body != nil {
		reqBodyBytes, err = utils.ReadAndReplaceBody(&req.Body)
		if err != nil {
			tlLog.Warn("Failed to read request body for %s: %v", fullURL, err)
			// Proceed without request body
		}
	}

	// Perform the actual request
	resp, err := t.originalTransport.RoundTrip(req)
	endTime := time.Now()

	// If there was an error making the request, we might still want to log the attempt if tagged
	if err != nil {
		if tag != "" { // Only log errors for explicitly tagged requests to avoid noise
			callData := types.LLMCallData{
				URL:             fullURL,
				Tag:             tag,
				StartTime:       startTime,
				EndTime:         endTime,
				IsLLMRequest:    true, // Assume intent if tagged
				Status:          0,    // No response
				RequestBodyStr:  string(utils.CapBody(reqBodyBytes)),
				ResponseBodyStr: err.Error(), // Log error as response
				Location:        utils.CallerSite(),
			}
			t.exporter.RecordLLMCall(callData)
		}
		return nil, err // Return original error
	}

	// Read response body
	var respBodyBytes []byte
	if resp.Body != nil {
		respBodyBytes, err = utils.ReadAndReplaceBody(&resp.Body)
		if err != nil {
			tlLog.Warn("Failed to read response body for %s: %v", fullURL, err)
			// Proceed with what was read or empty if total failure
		}
	}

	// Data for exporter
	callData := types.LLMCallData{
		URL:             fullURL,
		Tag:             tag,
		StartTime:       startTime,
		EndTime:         endTime,
		IsLLMRequest:    isLLM || tag != "",
		Status:          resp.StatusCode,
		RequestBodyStr:  string(utils.CapBody(reqBodyBytes)),
		ResponseBodyStr: string(utils.CapBody(respBodyBytes)), // utils.FormatStreamedContent will handle it in exporter
		Location:        utils.CallerSite(),
	}
	t.exporter.RecordLLMCall(callData)

	return resp, nil
}

// InstallPatches wraps http.DefaultTransport.
func InstallPatches(exp *exporter.FileExporter, hostAllowlist []string) {
	if isPatched {
		tlLog.Info("HTTP instrumentation already installed.")
		return
	}
	originalDefaultTransport = http.DefaultTransport
	if originalDefaultTransport == nil {
		// If http.DefaultTransport is nil, http.Client creates a new one.
		// We ensure it's not nil so we can wrap it.
		originalDefaultTransport = &http.Transport{}
	}

	http.DefaultTransport = &trainloopTransport{
		originalTransport: originalDefaultTransport,
		exporter:          exp,
		hostAllowlist:     hostAllowlist,
	}
	isPatched = true
	tlLog.Info("Successfully patched http.DefaultTransport.")
}

// UninstallPatches restores the original http.DefaultTransport.
// Typically used for testing or cleanup.
func UninstallPatches() {
	if !isPatched {
		tlLog.Info("HTTP instrumentation not installed, nothing to uninstall.")
		return
	}
	if originalDefaultTransport != nil {
		http.DefaultTransport = originalDefaultTransport
	}
	isPatched = false
	tlLog.Info("Uninstalled HTTP instrumentation, restored original http.DefaultTransport.")
}
