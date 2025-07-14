# Go SDK How-To

## Flush data immediately
Call `Flush()` on the exporter or use the `Shutdown()` helper when your app exits.

## Tag requests
```go
req.Header.Set(trainloop.HeaderName, "checkout")
```

## Custom config path
```go
trainloop.Collect("./trainloop/trainloop.config.yaml")
```
