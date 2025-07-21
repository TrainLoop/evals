---
sidebar_position: 3
---

# trainloop eval

Run evaluation suites to analyze your LLM interaction data and generate results.

## Synopsis

```bash
trainloop eval [OPTIONS]
```

## Description

The `trainloop eval` command processes event data collected by the TrainLoop SDK and applies your custom metrics to generate evaluation results. It discovers evaluation suites in the `trainloop/eval/` directory and processes new events from the data folder.

## Options

| Option | Description |
|--------|-------------|
| `--suite <name>` | Run only the specified evaluation suite |
| `--config <path>` | Path to configuration file |
| `--data-folder <path>` | Override data folder location |
| `--verbose` | Enable verbose output for debugging |
| `--quiet` | Suppress non-essential output |
| `--force` | Re-evaluate all events, ignoring cache |
| `--dry-run` | Show what would be evaluated without running |
| `--help` | Show help message |

## How It Works

1. **Discovery**: Finds evaluation suites in `trainloop/eval/suites/`
2. **Event Processing**: Loads event data from `trainloop/data/events/`
3. **Metric Application**: Applies metrics to each event
4. **Result Generation**: Saves results to `trainloop/data/results/`
5. **Judge Traces**: Stores LLM Judge traces in `trainloop/data/judge_traces/`

## Examples

### Basic Evaluation

```bash
# Run all evaluation suites
trainloop eval
```

### Run Specific Suite

```bash
# Run only the "greeting_evaluation" suite
trainloop eval --suite greeting_evaluation
```

### Custom Configuration

```bash
# Use custom configuration file
trainloop eval --config production.config.yaml
```

### Verbose Output

```bash
# Enable detailed logging
trainloop eval --verbose
```

### Force Re-evaluation

```bash
# Re-evaluate all events, ignoring cache
trainloop eval --force
```

### Dry Run

```bash
# Show what would be evaluated without running
trainloop eval --dry-run
```

## Configuration Discovery

The CLI searches for configuration files in this order:

1. `--config` command line argument
2. `TRAINLOOP_CONFIG_FILE` environment variable
3. `trainloop.config.yaml` in current directory
4. `trainloop.config.yaml` in parent directories (up to git root)
5. `~/.trainloop/config.yaml` in home directory
6. Default configuration

## Output

### Success Output

```
🔍 Discovering evaluation suites...
✅ Found 3 suites: greeting_evaluation, accuracy_check, safety_review

📊 Running evaluations...
✅ greeting_evaluation: 12/15 metrics passed (80.0%)
✅ accuracy_check: 45/50 metrics passed (90.0%)
✅ safety_review: 98/100 metrics passed (98.0%)

📈 Results saved to trainloop/data/results/
   - evaluation_results_2024-01-15_14-30-25.json
   - evaluation_summary.json

⏱️  Evaluation completed in 2.3s
```

### Verbose Output

```bash
trainloop eval --verbose
```

```
🔍 Discovering evaluation suites...
   - Found trainloop/eval/suites/greeting_evaluation.py
   - Found trainloop/eval/suites/accuracy_check.py
   - Found trainloop/eval/suites/safety_review.py
✅ Found 3 suites: greeting_evaluation, accuracy_check, safety_review

📁 Loading event data...
   - Loading trainloop/data/events/2024-01-15.jsonl (150 events)
   - Loading trainloop/data/events/2024-01-14.jsonl (230 events)
   - Total: 380 events

📊 Running evaluations...
   - greeting_evaluation: Processing 45 events...
     ✅ has_greeting_word: 42/45 passed (93.3%)
     ✅ is_personalized: 38/45 passed (84.4%)
     ❌ is_friendly_tone: 35/45 passed (77.8%)
   - accuracy_check: Processing 380 events...
     ✅ is_accurate: 342/380 passed (90.0%)
     ✅ is_complete: 335/380 passed (88.2%)
   - safety_review: Processing 380 events...
     ✅ is_safe: 378/380 passed (99.5%)
     ✅ no_harmful_content: 373/380 passed (98.2%)

📈 Results saved to trainloop/data/results/
   - evaluation_results_2024-01-15_14-30-25.json
   - evaluation_summary.json

⏱️  Evaluation completed in 2.3s
```

### Error Output

```
❌ Error: No evaluation suites found in trainloop/eval/suites/
   
   To get started:
   1. Create a suite file in trainloop/eval/suites/
   2. Add metrics to trainloop/eval/metrics/
   3. Run 'trainloop eval' again
   
   See: https://docs.trainloop.com/tutorials/first-evaluation
```

## Result Files

### Main Results File

```json
{
  "timestamp": "2024-01-15T14:30:25Z",
  "duration": 2.3,
  "total_events": 380,
  "suites": {
    "greeting_evaluation": {
      "events_processed": 45,
      "metrics": {
        "has_greeting_word": {
          "passed": 42,
          "total": 45,
          "score": 0.933
        },
        "is_personalized": {
          "passed": 38,
          "total": 45,
          "score": 0.844
        }
      },
      "overall_score": 0.889
    }
  }
}
```

### Summary File

```json
{
  "latest_evaluation": "2024-01-15T14:30:25Z",
  "total_suites": 3,
  "overall_score": 0.893,
  "trending": {
    "score_change": 0.05,
    "trend": "improving"
  }
}
```

## Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success - all evaluations completed |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Configuration error |
| `4` | No evaluation suites found |
| `5` | Evaluation failure |

## Performance Considerations

### Large Datasets

For large datasets, consider:

```bash
# Process in batches
trainloop eval --batch-size 1000

# Use parallel processing
trainloop eval --parallel

# Skip expensive metrics for CI
trainloop eval --skip-llm-judge
```

### Caching

TrainLoop caches evaluation results to avoid re-processing unchanged events:

```bash
# Clear cache if needed
trainloop eval --force

# Show cache statistics
trainloop eval --cache-stats
```

## Integration with CI/CD

### Basic CI Integration

```bash
# Run evaluations in CI
trainloop eval --config ci.config.yaml --quiet

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Evaluations passed"
else
    echo "❌ Evaluations failed"
    exit 1
fi
```

### Quality Gates

```bash
# Fail if score below threshold
trainloop eval --min-score 0.8

# Fail if any metric fails
trainloop eval --require-all-pass
```

## Common Issues

### No Suites Found

```
❌ Error: No evaluation suites found
```

**Solution**: Create evaluation suites in `trainloop/eval/suites/`

### No Events Found

```
❌ Error: No event data found
```

**Solution**: 
1. Check `TRAINLOOP_DATA_FOLDER` environment variable
2. Ensure your application is collecting data with the SDK
3. Verify events exist in `trainloop/data/events/`

### Import Errors

```
❌ Error: Failed to import suite 'my_suite'
```

**Solution**: 
1. Check Python syntax in suite files
2. Ensure metrics are importable
3. Verify Python path includes `trainloop/eval/`

### LLM Judge Failures

```
❌ Error: LLM Judge API call failed
```

**Solution**: 
1. Check API keys are configured
2. Verify network connectivity
3. Check rate limits
4. Use `--skip-llm-judge` to disable

## Advanced Usage

### Custom Metrics Path

```bash
# Use custom metrics directory
trainloop eval --metrics-path custom/metrics/

# Use custom suites directory
trainloop eval --suites-path custom/suites/
```

### Filtering Events

```bash
# Evaluate only recent events
trainloop eval --since "2024-01-01"

# Evaluate specific tags
trainloop eval --tags "greeting,support"

# Exclude specific tags
trainloop eval --exclude-tags "test,debug"
```

### Output Formats

```bash
# Output JSON results
trainloop eval --format json

# Output CSV results
trainloop eval --format csv

# Output to file
trainloop eval --output results.json
```

## See Also

- [init](init) - Initialize TrainLoop project
- [studio](studio) - Launch Studio UI
- [Configuration](config) - Configure evaluation behavior
- [SDK Reference](../sdks/) - Collect event data