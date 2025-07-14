---
sidebar_position: 4
---

# Multi-Service Instrumentation

Collect data from several services or languages in one project.

## Tutorial

1. Add the SDK to each service.
2. Point all services to the same data folder.
   ```bash
   export TRAINLOOP_DATA_FOLDER=/var/trainloop/data
   ```
3. Use unique labels when calling the SDK:
   ```python
   # Python example
   from trainloop_llm_logging import trainloop_tag
   headers = trainloop_tag("orders-service")
   ```
4. Run `trainloop eval` to process events from all services.

## How-tos

- [Python SDK reference](../docs/reference/sdk/python/api.md)
- [TypeScript SDK reference](../docs/reference/sdk/typescript/api.md)
- [Go SDK reference](../docs/reference/sdk/go/api.md)

## Pitfalls

- Synchronize clocks across machines for accurate timing.
- Flush buffers before each container stops.
- Use clear labels so metrics map back to the right service.
- Check that config files in each service don't override global settings.
