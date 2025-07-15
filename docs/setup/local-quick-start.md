---
sidebar_position: 1
---

# Local Quick-Start

This guide shows how to run TrainLoop Evals on your machine. Follow the steps below to collect data and view results.

## Tutorial

1. Install all dependencies:
   ```bash
   ./scripts/setup.py
   ```
2. Initialize your workspace:
   ```bash
   trainloop init
   ```
3. Instrument your app with an SDK. See the [Python SDK guide](../docs/guides/python-sdk.md) for details.
4. Run an evaluation:
   ```bash
   trainloop eval
   ```
5. Open the Studio UI:
   ```bash
   trainloop studio
   ```

## How-tos

- [Write metrics](../docs/guides/writing-metrics.md)
- [Create suites](../docs/guides/creating-suites.md)
- [Analyze data](../docs/guides/data-analysis.md)

## Pitfalls

- Ensure timing data is collected by keeping SDK versions up to date.
- Always flush events on shutdown so nothing is lost.
- Label requests with `trainloop_tag()` to group results.
- Remember configuration cascades from CLI flags to environment variables to `trainloop.config.yaml`.
