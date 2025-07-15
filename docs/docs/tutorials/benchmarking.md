---
sidebar_position: 5
---

# Benchmarking and Model Comparison

In this tutorial, you'll learn how to systematically compare different LLM providers to find the best model for your specific use case. We'll cover cost analysis, performance evaluation, and decision-making frameworks.

## What You'll Learn

- How to set up benchmarking for multiple LLM providers
- Cost vs. performance analysis techniques
- How to interpret benchmark results
- Best practices for model selection
- How to track performance over time

## Prerequisites

- Completed [Advanced Metrics with LLM Judge](advanced-metrics.md)
- API keys for multiple LLM providers
- Existing evaluation metrics and test suites

## Introduction to Benchmarking

### Why Benchmark?

Benchmarking helps you:
- **Choose the right model** - Find the best performer for your use case
- **Optimize costs** - Balance performance with API costs
- **Track improvements** - Monitor how new models perform
- **Make data-driven decisions** - Replace guesswork with evidence

### What TrainLoop Benchmarking Does

TrainLoop's benchmarking feature:
1. **Re-runs your prompts** against multiple LLM providers
2. **Applies your existing metrics** to all provider responses
3. **Generates comparison reports** with performance and cost data
4. **Visualizes results** in Studio UI for easy analysis

## Setting Up Benchmarking

### Step 1: Configure API Keys

First, ensure you have API keys for the providers you want to test:

```bash
# Create or update your .env file
cat > .env << 'EOF'
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
EOF
```

### Step 2: Configure Benchmark Providers

Edit your `trainloop.config.yaml` to specify which models to benchmark:

```yaml
# trainloop.config.yaml
trainloop:
  data_folder: "./data"
  
  # Benchmarking configuration
  benchmark:
    providers:
      # OpenAI models
      - provider: openai
        model: gpt-4o
        temperature: 0.7
        max_tokens: 1000
      
      - provider: openai
        model: gpt-4o-mini
        temperature: 0.7
        max_tokens: 1000
      
      # Anthropic models
      - provider: anthropic
        model: claude-3-5-sonnet-20241022
        temperature: 0.7
        max_tokens: 1000
      
      - provider: anthropic
        model: claude-3-haiku-20240307
        temperature: 0.7
        max_tokens: 1000
    
    # Optional: Limit number of samples for faster benchmarking
    max_samples: 100
    
    # Optional: Parallel execution settings
    max_concurrent_requests: 5
    
    # Optional: Cost tracking
    track_costs: true
```

### Step 3: Run Benchmarking

```bash
# Run benchmark against all configured providers
trainloop benchmark

# Run benchmark for specific tag
trainloop benchmark --tag greeting-generation

# Run benchmark with custom config
trainloop benchmark --config custom-benchmark.yaml
```

## Understanding Benchmark Results

### Performance Metrics

TrainLoop provides several performance metrics:

```
📊 Benchmark Results Summary
════════════════════════════════

Model Performance:
┌─────────────────────────────────┬─────────┬─────────┬─────────┬─────────┐
│ Model                           │ Avg     │ Min     │ Max     │ Samples │
├─────────────────────────────────┼─────────┼─────────┼─────────┼─────────┤
│ openai/gpt-4o                  │ 0.85    │ 0.67    │ 1.00    │ 100     │
│ openai/gpt-4o-mini             │ 0.82    │ 0.60    │ 1.00    │ 100     │
│ anthropic/claude-3-5-sonnet    │ 0.88    │ 0.73    │ 1.00    │ 100     │
│ anthropic/claude-3-haiku       │ 0.79    │ 0.53    │ 1.00    │ 100     │
└─────────────────────────────────┴─────────┴─────────┴─────────┴─────────┘

Cost Analysis:
┌─────────────────────────────────┬─────────────┬─────────────┬─────────────┐
│ Model                           │ Cost/1K tok │ Total Cost  │ Cost/Score  │
├─────────────────────────────────┼─────────────┼─────────────┼─────────────┤
│ openai/gpt-4o                  │ $0.015      │ $4.50       │ $0.053      │
│ openai/gpt-4o-mini             │ $0.001      │ $0.30       │ $0.004      │
│ anthropic/claude-3-5-sonnet    │ $0.015      │ $4.80       │ $0.055      │
│ anthropic/claude-3-haiku       │ $0.001      │ $0.32       │ $0.004      │
└─────────────────────────────────┴─────────────┴─────────────┴─────────────┘
```

### Metric-Level Analysis

View performance by individual metrics:

```bash
# Detailed breakdown by metric
trainloop benchmark --detailed
```

```
📈 Detailed Metric Analysis
═══════════════════════════════

Metric: has_greeting_word
┌─────────────────────────────────┬─────────┬─────────┬─────────┐
│ Model                           │ Score   │ Samples │ Pass %  │
├─────────────────────────────────┼─────────┼─────────┼─────────┤
│ openai/gpt-4o                  │ 0.95    │ 100     │ 95%     │
│ openai/gpt-4o-mini             │ 0.93    │ 100     │ 93%     │
│ anthropic/claude-3-5-sonnet    │ 0.97    │ 100     │ 97%     │
│ anthropic/claude-3-haiku       │ 0.89    │ 100     │ 89%     │
└─────────────────────────────────┴─────────┴─────────┴─────────┘

Metric: is_helpful_response
┌─────────────────────────────────┬─────────┬─────────┬─────────┐
│ Model                           │ Score   │ Samples │ Pass %  │
├─────────────────────────────────┼─────────┼─────────┼─────────┤
│ openai/gpt-4o                  │ 0.82    │ 100     │ 82%     │
│ openai/gpt-4o-mini             │ 0.75    │ 100     │ 75%     │
│ anthropic/claude-3-5-sonnet    │ 0.86    │ 100     │ 86%     │
│ anthropic/claude-3-haiku       │ 0.71    │ 100     │ 71%     │
└─────────────────────────────────┴─────────┴─────────┴─────────┘
```

## Analyzing Results in Studio UI

### Launch Studio for Benchmark Analysis

```bash
trainloop studio
```

### Key Views for Benchmark Analysis

#### 1. Model Comparison Dashboard
- Side-by-side performance comparison
- Cost vs. performance scatter plots
- Metric breakdown by model

#### 2. Sample-Level Analysis
- Individual responses from each model
- Quality differences for the same prompt
- Edge case identification

#### 3. Cost Analysis
- Total cost projections
- Cost per quality score
- ROI calculations

## Advanced Benchmarking Strategies

### 1. Stratified Benchmarking

Test different types of prompts separately:

```python
# trainloop/eval/suites/stratified_benchmark.py
from trainloop_cli.eval_core.helpers import tag

# Benchmark simple questions
simple_questions = tag("simple-qa").check(
    has_correct_answer,
    is_concise,
    is_clear
)

# Benchmark complex reasoning
complex_reasoning = tag("complex-reasoning").check(
    has_logical_flow,
    addresses_all_aspects,
    shows_depth
)

# Benchmark creative tasks
creative_tasks = tag("creative").check(
    is_original,
    is_engaging,
    follows_constraints
)
```

### 2. Domain-Specific Benchmarking

Create benchmarks for your specific domain:

```python
# trainloop/eval/suites/medical_benchmark.py
from trainloop_cli.eval_core.helpers import tag

# Medical information accuracy
medical_accuracy = tag("medical-info").check(
    is_medically_accurate,
    avoids_diagnosis,
    recommends_professional_consultation,
    uses_appropriate_disclaimers
)

# Medical communication quality
medical_communication = tag("medical-info").check(
    is_accessible_language,
    shows_empathy,
    is_reassuring_but_realistic,
    provides_actionable_advice
)
```

### 3. Time-Series Benchmarking

Track performance over time:

```bash
# Run benchmarks regularly
trainloop benchmark --tag time-series-test --output benchmark-$(date +%Y%m%d).json

# Compare with previous results
trainloop benchmark --compare-with benchmark-20240101.json
```

## Model Selection Framework

### 1. Define Your Priorities

Create a scoring framework based on your priorities:

```python
# Example priority weights
priorities = {
    "accuracy": 0.4,      # 40% weight
    "cost": 0.3,          # 30% weight
    "speed": 0.2,         # 20% weight
    "creativity": 0.1     # 10% weight
}
```

### 2. Normalize Scores

```python
def calculate_composite_score(benchmark_results, priorities):
    """Calculate composite score based on priorities"""
    models = {}
    
    for model_name, results in benchmark_results.items():
        # Normalize scores (0-1 scale)
        accuracy_score = results['avg_metric_score']
        cost_score = 1 - (results['cost_per_token'] / max_cost)  # Lower cost = higher score
        speed_score = 1 - (results['avg_response_time'] / max_time)  # Faster = higher score
        creativity_score = results['creativity_metric']
        
        # Calculate weighted composite score
        composite_score = (
            accuracy_score * priorities['accuracy'] +
            cost_score * priorities['cost'] +
            speed_score * priorities['speed'] +
            creativity_score * priorities['creativity']
        )
        
        models[model_name] = composite_score
    
    return models
```

### 3. Decision Matrix

| Model | Accuracy | Cost | Speed | Creativity | Composite |
|-------|----------|------|-------|------------|-----------|
| GPT-4o | 0.85 | 0.2 | 0.7 | 0.8 | 0.64 |
| GPT-4o-mini | 0.82 | 0.9 | 0.8 | 0.7 | 0.81 |
| Claude-3.5-Sonnet | 0.88 | 0.2 | 0.6 | 0.9 | 0.66 |
| Claude-3-Haiku | 0.79 | 0.9 | 0.9 | 0.6 | 0.79 |

## Production Benchmarking

### 1. Automated Benchmarking

```bash
# Create benchmark automation script
cat > benchmark_automation.sh << 'EOF'
#!/bin/bash

# Run daily benchmarks
trainloop benchmark --tag daily-benchmark --output "benchmark-$(date +%Y%m%d).json"

# Compare with baseline
trainloop benchmark --compare-with baseline-benchmark.json

# Alert if performance drops
if [[ $? -ne 0 ]]; then
    echo "Performance regression detected!" | mail -s "Benchmark Alert" team@company.com
fi
EOF

# Make executable
chmod +x benchmark_automation.sh

# Add to cron for daily execution
echo "0 2 * * * /path/to/benchmark_automation.sh" | crontab -
```

### 2. Continuous Monitoring

```python
# trainloop/eval/suites/continuous_monitoring.py
import datetime
from trainloop_cli.eval_core.helpers import tag

# Tag with timestamp for tracking
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
monitoring_tag = f"continuous-monitoring-{current_date}"

# Monitor key metrics
monitoring_results = tag(monitoring_tag).check(
    core_functionality_works,
    response_quality_maintained,
    cost_within_budget,
    response_time_acceptable
)
```

### 3. A/B Testing Framework

```python
# trainloop/eval/suites/ab_testing.py
from trainloop_cli.eval_core.helpers import tag

# Test new model against current production model
def ab_test_models(test_model, control_model, sample_size=1000):
    """
    Run A/B test between two models
    """
    # Run benchmark for both models
    test_results = benchmark_model(test_model, sample_size)
    control_results = benchmark_model(control_model, sample_size)
    
    # Statistical significance testing
    significance = calculate_statistical_significance(test_results, control_results)
    
    return {
        'test_model': test_model,
        'control_model': control_model,
        'test_performance': test_results['avg_score'],
        'control_performance': control_results['avg_score'],
        'improvement': test_results['avg_score'] - control_results['avg_score'],
        'statistical_significance': significance,
        'recommendation': 'deploy' if significance > 0.95 and test_results['avg_score'] > control_results['avg_score'] else 'keep_current'
    }
```

## Common Benchmarking Scenarios

### 1. Cost Optimization

```yaml
# Low-cost benchmark configuration
trainloop:
  benchmark:
    providers:
      - provider: openai
        model: gpt-4o-mini
      - provider: anthropic
        model: claude-3-haiku-20240307
      - provider: google
        model: gemini-pro
    
    # Focus on cost-effective models
    cost_threshold: 0.01  # Max $0.01 per 1K tokens
    performance_threshold: 0.75  # Min 75% pass rate
```

### 2. Accuracy Optimization

```yaml
# High-accuracy benchmark configuration
trainloop:
  benchmark:
    providers:
      - provider: openai
        model: gpt-4o
        temperature: 0.1  # Lower temperature for consistency
      - provider: anthropic
        model: claude-3-5-sonnet-20241022
        temperature: 0.1
    
    # Focus on accuracy metrics
    accuracy_weight: 0.8
    cost_weight: 0.2
```

### 3. Speed Optimization

```yaml
# Speed-focused benchmark configuration
trainloop:
  benchmark:
    providers:
      - provider: openai
        model: gpt-4o-mini
        max_tokens: 500  # Shorter responses
      - provider: anthropic
        model: claude-3-haiku-20240307
        max_tokens: 500
    
    # Measure response times
    track_response_times: true
    max_response_time: 3.0  # 3 second timeout
```

## Best Practices

### 1. Start Small, Scale Up

```bash
# Start with small sample size
trainloop benchmark --max-samples 10

# Increase gradually
trainloop benchmark --max-samples 100

# Full benchmark when confident
trainloop benchmark
```

### 2. Use Representative Data

```python
# Ensure your benchmark data represents real usage
def create_representative_benchmark():
    """Create benchmark data that matches production patterns"""
    
    # Sample from different time periods
    morning_samples = tag("morning-usage").sample(25)
    afternoon_samples = tag("afternoon-usage").sample(25)
    evening_samples = tag("evening-usage").sample(25)
    weekend_samples = tag("weekend-usage").sample(25)
    
    # Combine for comprehensive benchmark
    return morning_samples + afternoon_samples + evening_samples + weekend_samples
```

### 3. Regular Benchmarking

```bash
# Weekly performance check
0 0 * * 1 trainloop benchmark --tag weekly-check

# Monthly comprehensive benchmark
0 0 1 * * trainloop benchmark --comprehensive

# Quarterly model evaluation
0 0 1 1,4,7,10 * trainloop benchmark --full-evaluation
```

## Troubleshooting

### Common Issues

#### 1. API Rate Limits
```bash
# Reduce concurrent requests
trainloop benchmark --max-concurrent 2

# Add delays between requests
trainloop benchmark --request-delay 1.0
```

#### 2. Inconsistent Results
```bash
# Use larger sample sizes
trainloop benchmark --max-samples 500

# Lower temperature for consistency
trainloop benchmark --temperature 0.1
```

#### 3. Cost Concerns
```bash
# Limit sample size
trainloop benchmark --max-samples 50

# Use cheaper models for initial testing
trainloop benchmark --models gpt-4o-mini,claude-3-haiku
```

## Next Steps

Congratulations! You now know how to benchmark and compare LLM models effectively. Continue with:

- **[Production Setup and CI/CD](production-setup.md)** - Deploy evaluations in production environments

## Key Takeaways

1. **Benchmark regularly** - Model performance changes over time
2. **Consider multiple factors** - Balance accuracy, cost, and speed
3. **Use representative data** - Ensure benchmarks match real usage
4. **Automate the process** - Set up continuous benchmarking
5. **Make data-driven decisions** - Replace intuition with evidence

Ready to deploy your evaluations in production? Continue with [Production Setup and CI/CD](production-setup.md)!