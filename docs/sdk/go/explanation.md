# Go SDK Explanation

The package wraps the standard `http` client. It captures request and response bodies. Samples are buffered and saved in the data folder. Configuration comes from environment variables or `trainloop.config.yaml`. The SDK starts when you call `Collect()` and should be stopped with `Shutdown()`.
