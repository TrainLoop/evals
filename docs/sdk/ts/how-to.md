# TypeScript SDK How-To

## Flush data immediately
Use the `FLUSH_IMMEDIATELY` env var:
```bash
export TRAINLOOP_FLUSH_IMMEDIATELY=true
```

## Tag requests
```typescript
fetch(url, { headers: { ...trainloopTag('checkout') } })
```

## Custom config path
```bash
export TRAINLOOP_CONFIG_PATH=./trainloop/trainloop.config.yaml
```
