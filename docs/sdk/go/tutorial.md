# Go SDK Tutorial

Install the module and initialize collection:
```bash
go get github.com/trainloop/evals/sdk/go/trainloop-llm-logging
```

```go
import trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
func main() {
    trainloop.Collect()
    // make HTTP calls
}
```
Set `TRAINLOOP_DATA_FOLDER` before running.
