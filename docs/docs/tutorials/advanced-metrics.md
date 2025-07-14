---
sidebar_position: 4
---

# Advanced Metrics with LLM Judge

In this tutorial, you'll learn to use LLM Judge to create sophisticated evaluation metrics that go beyond simple rule-based checks. LLM Judge uses AI to evaluate AI, enabling complex quality assessments.

## What You'll Learn

- How to use LLM Judge for complex evaluations
- When to use LLM Judge vs. rule-based metrics
- How to write effective claims for LLM Judge
- Best practices for reliable LLM Judge metrics
- How to combine LLM Judge with traditional metrics

## Prerequisites

- Completed [Writing Your First Evaluation](first-evaluation.md)
- Understanding of basic metrics and suites
- API keys for LLM providers (OpenAI, Anthropic, etc.)

## Introduction to LLM Judge

### What is LLM Judge?

**LLM Judge** is a TrainLoop feature that uses large language models to evaluate the quality of LLM outputs. It's particularly useful for:

- **Subjective quality assessment** - Tone, helpfulness, clarity
- **Complex reasoning evaluation** - Logical consistency, accuracy
- **Domain-specific criteria** - Professional standards, style guidelines
- **Nuanced semantic understanding** - Intent matching, context awareness

### When to Use LLM Judge

| Use LLM Judge For | Use Rule-Based Metrics For |
|------------------|---------------------------|
| Subjective quality (tone, helpfulness) | Objective criteria (length, format) |
| Complex reasoning evaluation | Simple pattern matching |
| Domain-specific expertise | Universal standards |
| Nuanced understanding | Performance-critical checks |

## Basic LLM Judge Usage

### The `assert_true` Function

The core LLM Judge function compares two claims:

```python
from trainloop_cli.eval_core.judge import assert_true

def is_helpful_response(sample: Sample) -> int:
    """Check if response is helpful using LLM Judge"""
    response = sample.output.get("content", "")
    
    positive_claim = f"The response '{response}' is helpful and provides useful information."
    negative_claim = f"The response '{response}' is not helpful and doesn't provide useful information."
    
    return assert_true(positive_claim, negative_claim)
```

### How LLM Judge Works

1. **Claim Generation** - You provide positive and negative claims
2. **LLM Evaluation** - Multiple LLMs evaluate which claim is more true
3. **Consensus Building** - Results are aggregated across multiple calls
4. **Binary Result** - Returns 1 if positive claim wins, 0 if negative claim wins

## Advanced LLM Judge Patterns

### Context-Aware Evaluation

```python
def matches_user_intent(sample: Sample) -> int:
    """Check if response matches user's intent"""
    user_message = ""
    for msg in sample.input.get("messages", []):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    response = sample.output.get("content", "")
    
    positive_claim = f"The response '{response}' directly addresses the user's request: '{user_message}'"
    negative_claim = f"The response '{response}' does not address the user's request: '{user_message}'"
    
    return assert_true(positive_claim, negative_claim)
```

### Domain-Specific Evaluation

```python
def follows_medical_guidelines(sample: Sample) -> int:
    """Check if response follows medical communication guidelines"""
    response = sample.output.get("content", "")
    
    positive_claim = f"""The response '{response}' follows proper medical communication guidelines by:
    - Being accurate and evidence-based
    - Avoiding definitive diagnoses
    - Recommending professional consultation when appropriate
    - Using clear, accessible language"""
    
    negative_claim = f"""The response '{response}' violates medical communication guidelines by:
    - Making unsupported claims
    - Providing definitive diagnoses
    - Failing to recommend professional consultation
    - Using confusing or inappropriate language"""
    
    return assert_true(positive_claim, negative_claim)
```

### Multi-Criteria Evaluation

```python
def is_professional_customer_service(sample: Sample) -> int:
    """Evaluate multiple aspects of customer service quality"""
    response = sample.output.get("content", "")
    
    positive_claim = f"""The response '{response}' demonstrates excellent customer service by:
    - Showing empathy and understanding
    - Providing clear, actionable solutions
    - Maintaining a professional yet friendly tone
    - Being concise while being thorough"""
    
    negative_claim = f"""The response '{response}' demonstrates poor customer service by:
    - Lacking empathy or understanding
    - Providing unclear or unhelpful solutions
    - Using inappropriate tone or language
    - Being either too brief or overly verbose"""
    
    return assert_true(positive_claim, negative_claim)
```

## Writing Effective Claims

### Best Practices for Claims

#### 1. Be Specific and Detailed

```python
# Good - Specific criteria
positive_claim = f"The response '{response}' is helpful because it provides specific steps, explains the reasoning, and offers alternatives."

# Bad - Too vague
positive_claim = f"The response '{response}' is good."
```

#### 2. Make Claims Mutually Exclusive

```python
# Good - Clear opposite claims
positive_claim = f"The response '{response}' is factually accurate and well-supported."
negative_claim = f"The response '{response}' contains factual errors or unsupported claims."

# Bad - Not mutually exclusive
positive_claim = f"The response '{response}' is accurate."
negative_claim = f"The response '{response}' is confusing."
```

#### 3. Include Context When Relevant

```python
def appropriate_response_tone(sample: Sample) -> int:
    """Check if response tone matches the context"""
    user_message = ""
    for msg in sample.input.get("messages", []):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    response = sample.output.get("content", "")
    
    # Include context in claims
    positive_claim = f"Given the user's message '{user_message}', the response '{response}' uses an appropriate tone that matches the context and user's emotional state."
    negative_claim = f"Given the user's message '{user_message}', the response '{response}' uses an inappropriate tone that doesn't match the context or user's emotional state."
    
    return assert_true(positive_claim, negative_claim)
```

## Complex Evaluation Scenarios

### Evaluating Reasoning and Logic

```python
def has_logical_reasoning(sample: Sample) -> int:
    """Check if response demonstrates logical reasoning"""
    response = sample.output.get("content", "")
    
    positive_claim = f"""The response '{response}' demonstrates clear logical reasoning by:
    - Presenting information in a logical sequence
    - Making valid inferences from given information
    - Avoiding logical fallacies
    - Drawing appropriate conclusions"""
    
    negative_claim = f"""The response '{response}' lacks logical reasoning by:
    - Presenting information in a confusing order
    - Making invalid inferences
    - Containing logical fallacies
    - Drawing inappropriate conclusions"""
    
    return assert_true(positive_claim, negative_claim)
```

### Evaluating Creativity and Originality

```python
def is_creative_response(sample: Sample) -> int:
    """Check if response is creative and original"""
    response = sample.output.get("content", "")
    
    positive_claim = f"""The response '{response}' demonstrates creativity by:
    - Offering unique or novel perspectives
    - Using imaginative language or examples
    - Providing original insights or solutions
    - Avoiding clichéd or generic content"""
    
    negative_claim = f"""The response '{response}' lacks creativity by:
    - Offering only conventional perspectives
    - Using predictable language or examples
    - Providing generic insights or solutions
    - Relying on clichéd or overused content"""
    
    return assert_true(positive_claim, negative_claim)
```

### Evaluating Completeness

```python
def provides_complete_answer(sample: Sample) -> int:
    """Check if response completely addresses the question"""
    user_message = ""
    for msg in sample.input.get("messages", []):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    response = sample.output.get("content", "")
    
    positive_claim = f"""The response '{response}' provides a complete answer to the question '{user_message}' by:
    - Addressing all parts of the question
    - Providing sufficient detail and explanation
    - Covering relevant aspects and considerations
    - Offering actionable information where appropriate"""
    
    negative_claim = f"""The response '{response}' provides an incomplete answer to the question '{user_message}' by:
    - Ignoring parts of the question
    - Providing insufficient detail or explanation
    - Missing relevant aspects or considerations
    - Failing to offer actionable information"""
    
    return assert_true(positive_claim, negative_claim)
```

## Combining LLM Judge with Traditional Metrics

### Hybrid Evaluation Suite

```python
# trainloop/eval/suites/hybrid_evaluation.py
from trainloop_cli.eval_core.helpers import tag
from ..metrics.rule_based import has_greeting_word, appropriate_length, contains_contact_info
from ..metrics.llm_judge import is_helpful_response, matches_user_intent, is_professional_tone

# Combine rule-based and LLM Judge metrics
results = tag("customer-support").check(
    # Fast rule-based checks
    has_greeting_word,
    appropriate_length,
    contains_contact_info,
    
    # Sophisticated LLM Judge evaluations
    is_helpful_response,
    matches_user_intent,
    is_professional_tone
)
```

### Performance-Optimized Approach

```python
def smart_evaluation_suite(sample: Sample) -> dict:
    """Use rule-based metrics first, LLM Judge for edge cases"""
    results = {}
    
    # Fast rule-based checks first
    results['has_greeting'] = has_greeting_word(sample)
    results['appropriate_length'] = appropriate_length(sample)
    
    # Only use LLM Judge for complex cases
    if results['has_greeting'] and results['appropriate_length']:
        results['is_helpful'] = is_helpful_response(sample)
        results['matches_intent'] = matches_user_intent(sample)
    else:
        # Skip expensive LLM Judge checks for obviously bad responses
        results['is_helpful'] = 0
        results['matches_intent'] = 0
    
    return results
```

## Configuration and Optimization

### Configuring LLM Judge

```yaml
# trainloop.config.yaml
trainloop:
  judge:
    # Models to use for evaluation
    models:
      - openai/gpt-4o
      - anthropic/claude-3-sonnet-20240229
      - openai/gpt-4o-mini
    
    # Number of calls per model per claim
    calls_per_model_per_claim: 3
    
    # Temperature for consistency
    temperature: 0.1
    
    # Maximum tokens for judge responses
    max_tokens: 100
    
    # Timeout for judge calls
    timeout: 30
```

### Optimizing Performance

#### 1. Use Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_helpfulness_check(response_content: str) -> int:
    """Cache LLM Judge results for identical responses"""
    positive_claim = f"The response '{response_content}' is helpful and informative."
    negative_claim = f"The response '{response_content}' is unhelpful and uninformative."
    
    return assert_true(positive_claim, negative_claim)

def is_helpful_cached(sample: Sample) -> int:
    response = sample.output.get("content", "")
    return cached_helpfulness_check(response)
```

#### 2. Batch Similar Evaluations

```python
def batch_tone_evaluation(samples: List[Sample]) -> List[int]:
    """Evaluate tone for multiple samples efficiently"""
    results = []
    
    for sample in samples:
        response = sample.output.get("content", "")
        positive_claim = f"The response '{response}' has a professional and appropriate tone."
        negative_claim = f"The response '{response}' has an unprofessional or inappropriate tone."
        
        result = assert_true(positive_claim, negative_claim)
        results.append(result)
    
    return results
```

## Testing and Validation

### Test LLM Judge Metrics

```python
def test_llm_judge_consistency():
    """Test that LLM Judge metrics are consistent"""
    sample = Sample(
        input={"messages": [{"role": "user", "content": "Hello, how are you?"}]},
        output={"content": "Hello! I'm doing well, thank you for asking. How can I help you today?"}
    )
    
    # Run the same metric multiple times
    results = []
    for i in range(5):
        result = is_helpful_response(sample)
        results.append(result)
    
    # Check consistency (should be mostly the same)
    consistency_rate = sum(results) / len(results)
    print(f"Consistency rate: {consistency_rate}")
    
    # Should be either very high (>0.8) or very low (<0.2)
    assert consistency_rate > 0.8 or consistency_rate < 0.2, "Inconsistent LLM Judge results"
```

### Validate Against Human Judgment

```python
def validate_against_human_judgment():
    """Compare LLM Judge results with human evaluations"""
    test_cases = [
        {
            "sample": Sample(
                input={"messages": [{"role": "user", "content": "Explain quantum computing"}]},
                output={"content": "Quantum computing is complicated stuff with atoms and things."}
            ),
            "human_rating": 0  # Human says this is not helpful
        },
        {
            "sample": Sample(
                input={"messages": [{"role": "user", "content": "Explain quantum computing"}]},
                output={"content": "Quantum computing uses quantum mechanical properties like superposition and entanglement to process information in fundamentally different ways than classical computers, potentially solving certain problems exponentially faster."}
            ),
            "human_rating": 1  # Human says this is helpful
        }
    ]
    
    agreement_count = 0
    for test_case in test_cases:
        llm_rating = is_helpful_response(test_case["sample"])
        if llm_rating == test_case["human_rating"]:
            agreement_count += 1
    
    agreement_rate = agreement_count / len(test_cases)
    print(f"Agreement with human judgment: {agreement_rate:.2%}")
```

## Best Practices Summary

### 1. Start with Rule-Based, Add LLM Judge

```python
# Good progression
def comprehensive_quality_check(sample: Sample) -> int:
    # Quick rule-based elimination
    if not has_minimum_length(sample):
        return 0
    
    if not contains_required_elements(sample):
        return 0
    
    # Sophisticated LLM Judge evaluation
    return is_high_quality_response(sample)
```

### 2. Use Specific, Detailed Claims

```python
# Good - Specific and actionable
positive_claim = f"The response '{response}' provides accurate, step-by-step instructions that are easy to follow and include necessary warnings."

# Bad - Vague and subjective
positive_claim = f"The response '{response}' is good."
```

### 3. Monitor and Validate Results

```python
# Add monitoring to your LLM Judge metrics
def monitored_helpfulness_check(sample: Sample) -> int:
    result = is_helpful_response(sample)
    
    # Log for analysis
    log_metric_result("helpfulness", result, sample.output.get("content", ""))
    
    return result
```

## Common Pitfalls and Solutions

### 1. Inconsistent Results

**Problem:** LLM Judge returns different results for the same input

**Solution:** 
- Lower temperature in configuration
- Use more specific claims
- Increase number of calls per claim

### 2. Slow Performance

**Problem:** LLM Judge metrics are too slow

**Solution:**
- Use caching for repeated content
- Combine with rule-based pre-filtering
- Use faster models for simple evaluations

### 3. Unreliable Evaluation

**Problem:** LLM Judge doesn't match human judgment

**Solution:**
- Validate against human examples
- Refine claim wording
- Use multiple models for consensus

## Next Steps

You now know how to create sophisticated evaluation metrics using LLM Judge! Continue with:

- **[Benchmarking and Model Comparison](benchmarking.md)** - Compare different LLM providers
- **[Production Setup](production-setup.md)** - Deploy evaluations in CI/CD pipelines

## Troubleshooting

### Common Issues

#### LLM Judge Calls Failing
- Check API keys and rate limits
- Verify model names in configuration
- Check network connectivity

#### Unexpected Results
- Review claim wording for clarity
- Test with known examples
- Check for model-specific biases

#### Performance Issues
- Implement caching for repeated evaluations
- Use rule-based pre-filtering
- Consider using faster/cheaper models

Ready to compare different LLM providers? Continue with [Benchmarking and Model Comparison](benchmarking.md)!