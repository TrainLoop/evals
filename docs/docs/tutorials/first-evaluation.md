---
sidebar_position: 3
---

# Writing Your First Evaluation

In this tutorial, you'll learn how to write effective evaluation metrics and organize them into comprehensive test suites. We'll build on the quick start guide to create more sophisticated evaluation criteria.

## What You'll Learn

- How to design effective evaluation metrics
- Different types of metrics (rule-based, statistical, semantic)
- How to organize metrics into logical test suites
- Best practices for metric naming and documentation
- How to debug and iterate on your metrics

## Prerequisites

- Completed the [Quick Start Guide](getting-started.md)
- Basic understanding of Python functions
- An LLM application with collected data

## Understanding Evaluation Metrics

### What Makes a Good Metric?

A good evaluation metric should be:
- **Specific** - Tests one clear aspect of quality
- **Reliable** - Produces consistent results
- **Actionable** - Provides clear guidance for improvement
- **Fast** - Runs quickly to enable rapid iteration

### Types of Metrics

#### 1. Rule-Based Metrics
Simple, deterministic checks based on patterns or rules:

```python
def contains_required_elements(sample: Sample) -> int:
    """Check if response contains required elements"""
    response = sample.output.get("content", "")
    required_elements = ["greeting", "name", "helpful"]
    
    for element in required_elements:
        if element.lower() not in response.lower():
            return 0
    return 1
```

#### 2. Statistical Metrics
Metrics based on measurable properties:

```python
def appropriate_length(sample: Sample) -> int:
    """Check if response length is appropriate"""
    response = sample.output.get("content", "")
    word_count = len(response.split())
    
    # Adjust range based on your use case
    return 1 if 10 <= word_count <= 100 else 0
```

#### 3. Semantic Metrics
Metrics that evaluate meaning and context:

```python
def addresses_user_intent(sample: Sample) -> int:
    """Check if response addresses the user's intent"""
    user_message = ""
    for msg in sample.input.get("messages", []):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    response = sample.output.get("content", "")
    
    # Use simple keyword matching or more sophisticated NLP
    if "question" in user_message.lower():
        return 1 if "?" in response or "answer" in response.lower() else 0
    
    return 1  # Default pass for non-question inputs
```

## Building Your Evaluation Suite

### Step 1: Define Your Quality Criteria

Before writing metrics, define what "good" looks like for your use case:

```python
# trainloop/eval/metrics/content_quality.py
from trainloop_cli.eval_core.types import Sample

def is_helpful(sample: Sample) -> int:
    """Check if the response is helpful to the user"""
    response = sample.output.get("content", "").lower()
    
    # Look for helpful indicators
    helpful_indicators = [
        "help", "assist", "support", "solution", "answer",
        "explain", "guide", "suggest", "recommend"
    ]
    
    return 1 if any(indicator in response for indicator in helpful_indicators) else 0

def is_accurate(sample: Sample) -> int:
    """Check if the response contains accurate information"""
    response = sample.output.get("content", "").lower()
    
    # Look for accuracy indicators (customize for your domain)
    inaccurate_indicators = [
        "i'm not sure", "i don't know", "might be wrong",
        "not certain", "unsure", "unclear"
    ]
    
    return 0 if any(indicator in response for indicator in inaccurate_indicators) else 1

def follows_format(sample: Sample) -> int:
    """Check if response follows expected format"""
    response = sample.output.get("content", "")
    
    # Example: Check if response is properly structured
    # Customize based on your format requirements
    has_greeting = any(word in response.lower() for word in ["hello", "hi", "greetings"])
    has_closing = any(word in response.lower() for word in ["thanks", "welcome", "help"])
    
    return 1 if has_greeting and has_closing else 0
```

### Step 2: Create Comprehensive Test Suites

Organize your metrics into logical groupings:

```python
# trainloop/eval/suites/comprehensive_evaluation.py
from trainloop_cli.eval_core.helpers import tag
from ..metrics.content_quality import is_helpful, is_accurate, follows_format
from ..metrics.greeting_quality import has_greeting_word, is_personalized, is_friendly_tone

# Evaluate all LLM interactions
results = tag("").check(  # Empty tag evaluates all data
    # Content quality metrics
    is_helpful,
    is_accurate,
    follows_format,
    
    # Greeting-specific metrics (only applies to greeting calls)
    has_greeting_word,
    is_personalized,
    is_friendly_tone
)
```

### Step 3: Create Focused Test Suites

Create specific suites for different types of interactions:

```python
# trainloop/eval/suites/greeting_focused.py
from trainloop_cli.eval_core.helpers import tag
from ..metrics.greeting_quality import has_greeting_word, is_personalized, is_friendly_tone

# Only evaluate greeting generation calls
results = tag("greeting-generation").check(
    has_greeting_word,
    is_personalized,
    is_friendly_tone
)
```

```python
# trainloop/eval/suites/customer_support.py
from trainloop_cli.eval_core.helpers import tag
from ..metrics.content_quality import is_helpful, is_accurate
from ..metrics.support_specific import resolves_issue, shows_empathy

# Only evaluate customer support interactions
results = tag("customer-support").check(
    is_helpful,
    is_accurate,
    resolves_issue,
    shows_empathy
)
```

## Advanced Metric Patterns

### Using Context from the Request

```python
def matches_requested_tone(sample: Sample) -> int:
    """Check if response matches the requested tone"""
    system_message = ""
    for msg in sample.input.get("messages", []):
        if msg.get("role") == "system":
            system_message = msg.get("content", "").lower()
            break
    
    response = sample.output.get("content", "").lower()
    
    # Check if tone matches system instructions
    if "formal" in system_message:
        informal_words = ["hey", "sup", "yo", "gonna", "wanna"]
        return 0 if any(word in response for word in informal_words) else 1
    
    if "casual" in system_message:
        formal_words = ["furthermore", "consequently", "nevertheless"]
        return 0 if any(word in response for word in formal_words) else 1
    
    return 1  # Default pass if no tone specified
```

### Metrics with Parameters

```python
def max_length_check(max_words: int):
    """Create a metric that checks maximum length"""
    def check_length(sample: Sample) -> int:
        response = sample.output.get("content", "")
        word_count = len(response.split())
        return 1 if word_count <= max_words else 0
    
    return check_length

# Usage in suite
short_response_check = max_length_check(50)
medium_response_check = max_length_check(200)
```

## Testing and Debugging Your Metrics

### Test Individual Metrics

```python
# trainloop/eval/metrics/test_greeting_quality.py
from trainloop_cli.eval_core.types import Sample
from .greeting_quality import has_greeting_word, is_personalized

def test_has_greeting_word():
    # Test case 1: Response with greeting
    sample1 = Sample(
        input={},
        output={"content": "Hello! How can I help you today?"}
    )
    assert has_greeting_word(sample1) == 1
    
    # Test case 2: Response without greeting
    sample2 = Sample(
        input={},
        output={"content": "The weather is nice today."}
    )
    assert has_greeting_word(sample2) == 0
    
    print("✅ has_greeting_word tests passed")

if __name__ == "__main__":
    test_has_greeting_word()
```

### Run Tests Before Evaluation

```bash
# Test your metrics before running full evaluation
python trainloop/eval/metrics/test_greeting_quality.py
```

## Running and Analyzing Results

### Run Your Evaluation

```bash
# Run all suites
trainloop eval

# Run specific suite
trainloop eval --suite comprehensive_evaluation

# Run with verbose output for debugging
trainloop eval --verbose
```

### Analyze Results in Studio UI

```bash
trainloop studio
```

Look for:
- **Failing metrics** - Which criteria are not being met?
- **Patterns in failures** - Are failures clustered around specific inputs?
- **Metric correlations** - Do certain metrics always pass/fail together?

## Best Practices

### 1. Start Simple, Add Complexity

Begin with simple rule-based metrics and gradually add more sophisticated ones:

```python
# Start with this
def has_greeting(sample: Sample) -> int:
    response = sample.output.get("content", "").lower()
    return 1 if "hello" in response else 0

# Evolve to this
def has_appropriate_greeting(sample: Sample) -> int:
    response = sample.output.get("content", "").lower()
    greetings = ["hello", "hi", "greetings", "good morning", "good afternoon", "good evening"]
    return 1 if any(greeting in response for greeting in greetings) else 0
```

### 2. Document Your Metrics

```python
def is_professional_tone(sample: Sample) -> int:
    """
    Check if the response maintains a professional tone.
    
    Criteria:
    - Avoids slang and informal language
    - Uses complete sentences
    - Maintains respectful language
    
    Returns:
        1 if professional tone is maintained, 0 otherwise
    """
    response = sample.output.get("content", "").lower()
    
    unprofessional_words = ["yo", "sup", "gonna", "wanna", "ain't"]
    return 0 if any(word in response for word in unprofessional_words) else 1
```

### 3. Use Descriptive Names

```python
# Good
def contains_required_safety_warning(sample: Sample) -> int:
    pass

# Bad
def check_safety(sample: Sample) -> int:
    pass
```

### 4. Handle Edge Cases

```python
def has_valid_response(sample: Sample) -> int:
    """Check if response is valid and non-empty"""
    response = sample.output.get("content", "")
    
    # Handle edge cases
    if not response:
        return 0
    
    if response.strip() == "":
        return 0
    
    if len(response) < 3:  # Too short to be meaningful
        return 0
    
    return 1
```

## Next Steps

Congratulations! You now know how to write comprehensive evaluation metrics. Next, explore:

- **[Advanced Metrics with LLM Judge](advanced-metrics.md)** - Use AI to evaluate complex quality aspects
- **[Benchmarking and Model Comparison](benchmarking.md)** - Compare different LLM providers
- **[Production Setup](production-setup.md)** - Deploy evaluations in CI/CD pipelines

## Troubleshooting

### Common Issues

#### Metric Always Returns 0 or 1
- Check your logic conditions
- Add debug prints to see what data you're receiving
- Test with known examples

#### Metric Throws Errors
- Add error handling for missing data
- Check data types and structure
- Use try/except blocks for robustness

#### Inconsistent Results
- Ensure your metric is deterministic
- Check for race conditions in data access
- Verify input data consistency

### Debug Example

```python
def debug_metric(sample: Sample) -> int:
    """Example of debugging a metric"""
    try:
        response = sample.output.get("content", "")
        print(f"DEBUG: Response content: '{response}'")
        
        # Your metric logic here
        result = 1 if "hello" in response.lower() else 0
        print(f"DEBUG: Metric result: {result}")
        
        return result
    except Exception as e:
        print(f"DEBUG: Error in metric: {e}")
        return 0
```

Ready to build more sophisticated evaluations? Continue with [Advanced Metrics with LLM Judge](advanced-metrics.md)!