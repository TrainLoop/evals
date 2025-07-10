# Architecture Guide

This guide provides a comprehensive overview of the TrainLoop Evals architecture, including system design, component interactions, and data flow patterns.

## System Overview

TrainLoop Evals is a distributed LLM evaluation framework designed around the principle of zero-configuration data collection and flexible evaluation. The system consists of multiple loosely-coupled components that can be deployed independently.

### Core Design Principles

1. **Simplicity First** - One environment variable, one function call, one folder of JSON files
2. **Vendor Independence** - Everything stored as newline-delimited JSON; no databases required
3. **Developer-Friendly** - Meets developers where they are, accepts existing bespoke loops
4. **Type-Safe** - All evaluation code present in codebase with full type safety
5. **Composable** - Extensible system with helper generators (shadcn-like patterns)

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                TrainLoop Evals                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Application    │  │  Application    │  │  Application    │  │     CLI     │ │
│  │   (Python)      │  │  (TypeScript)   │  │     (Go)        │  │    Tool     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│           │                      │                      │               │        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │        │
│  │   Python SDK    │  │ TypeScript SDK  │  │     Go SDK      │       │        │
│  │   (Instrumentation)│  │(Instrumentation)│  │(Instrumentation)│       │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘       │        │
│           │                      │                      │               │        │
│           └──────────────────────┼──────────────────────┘               │        │
│                                  │                                      │        │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            Data Layer                                       │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │     Events      │  │     Results     │  │   Benchmarks    │             │ │
│  │  │   (JSONL)       │  │    (JSONL)      │  │    (JSONL)      │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Evaluation Engine                                    │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │     Metrics     │  │     Suites      │  │     Judges      │             │ │
│  │  │   (Python)      │  │   (Python)      │  │   (LLM-based)   │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Studio UI                                            │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │ │
│  │  │    Dashboard    │  │    Benchmarks   │  │    Analysis     │             │ │
│  │  │   (Next.js)     │  │   (Next.js)     │  │   (Next.js)     │             │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. SDK Layer (Data Collection)

The SDK layer provides zero-touch instrumentation for LLM calls across multiple programming languages.

#### Python SDK (`sdk/python/`)

```python
# Architecture: HTTP instrumentation with monkey patching
from trainloop_llm_logging import collect

# Single function call enables instrumentation
collect("./trainloop/trainloop.config.yaml")

# Automatically captures:
# - OpenAI SDK calls
# - Anthropic SDK calls
# - LangChain calls
# - Raw HTTP requests to LLM providers
```

**Key Components:**
- `instrumentation/` - HTTP library patches (requests, httpx, http.client)
- `store.py` - Thread-safe data persistence
- `exporter.py` - Configurable data export (local, S3, GCS)
- `logger.py` - Structured logging with correlation IDs

#### TypeScript SDK (`sdk/typescript/`)

```typescript
// Architecture: Node.js HTTP/fetch instrumentation
import { collect } from 'trainloop-llm-logging';

// Environment variable configuration
process.env.TRAINLOOP_DATA_FOLDER = './data';
process.env.NODE_OPTIONS = '--require=trainloop-llm-logging';

// Automatically captures:
// - fetch() calls
// - http/https module usage
// - Popular LLM SDK calls
```

**Key Components:**
- `instrumentation/fetch.ts` - Fetch API instrumentation
- `instrumentation/http.ts` - Node.js HTTP module instrumentation
- `store.ts` - Event buffering and persistence
- `config.ts` - Configuration management

#### Go SDK (`sdk/go/`)

```go
// Architecture: HTTP transport wrapping
import "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"

// Wrap HTTP client
client := &http.Client{
    Transport: trainloop.NewInstrumentedTransport(
        http.DefaultTransport,
        trainloop.DefaultConfig(),
    ),
}

// All HTTP calls through this client are instrumented
```

**Key Components:**
- `instrumentation/http.go` - HTTP transport wrapper
- `internal/store/` - Event storage and buffering
- `internal/config/` - Configuration management

### 2. CLI Tool (`cli/`)

The CLI provides the primary interface for managing TrainLoop projects and running evaluations.

#### Command Architecture

```python
# cli/trainloop_cli/commands/
├── __init__.py
├── init.py          # Project initialization
├── eval.py          # Evaluation execution
├── studio.py        # Studio UI launcher
├── add.py           # Registry component addition
└── benchmark/       # Benchmark functionality
    ├── command.py
    ├── runner.py
    └── storage.py
```

#### Core Commands

**`trainloop init`**
- Scaffolds project structure
- Creates sample metrics and suites
- Initializes configuration

**`trainloop eval`**
- Discovers and runs evaluation suites
- Applies metrics to collected events
- Outputs results to JSONL files

**`trainloop studio`**
- Launches web-based visualization
- Provides interactive data exploration
- Supports real-time updates

**`trainloop add`**
- Adds components from registry
- Supports local and remote registries
- Type-safe component discovery

**`trainloop benchmark`**
- Compares multiple LLM providers
- Generates performance and cost analysis
- Supports custom evaluation metrics

### 3. Evaluation Engine (`cli/trainloop_cli/eval_core/`)

The evaluation engine processes collected events through configurable metrics and suites.

#### Component Structure

```python
# Evaluation workflow
Events (JSONL) → Metrics → Suites → Results (JSONL)
```

#### Metrics System

```python
# registry/metrics/is_helpful/is_helpful.py
def is_helpful(event: dict) -> dict:
    """Evaluate if an LLM response is helpful."""
    prompt = event.get("prompt", "")
    response = event.get("response", "")
    
    # Metric logic here
    score = calculate_helpfulness(prompt, response)
    
    return {
        "metric": "is_helpful",
        "score": score,
        "passed": score > 0.7,
        "metadata": {"reasoning": "..."}
    }
```

#### Suites System

```python
# registry/suites/is_helpful/is_helpful.py
from registry.metrics.is_helpful.is_helpful import is_helpful

def suite(events: list) -> list:
    """Evaluate helpfulness across multiple events."""
    results = []
    for event in events:
        result = is_helpful(event)
        results.append(result)
    return results
```

#### LLM Judge Integration

```python
# cli/trainloop_cli/eval_core/judge.py
class LLMJudge:
    """LLM-based evaluation using configurable prompts."""
    
    def judge(self, prompt: str, response: str, criteria: str) -> dict:
        """Evaluate response against criteria using LLM."""
        judge_prompt = f"""
        Evaluate the following response based on: {criteria}
        
        Prompt: {prompt}
        Response: {response}
        
        Provide a score from 0-1 and reasoning.
        """
        
        # LLM call for evaluation
        result = self.llm_client.complete(judge_prompt)
        return parse_judge_result(result)
```

### 4. Studio UI (`ui/`)

The Studio UI provides web-based visualization and analysis of evaluation data.

#### Technology Stack

- **Framework**: Next.js 15 with App Router
- **Database**: DuckDB for local data querying
- **UI Components**: shadcn/ui with Tailwind CSS
- **Charts**: Recharts and Nivo for data visualization

#### Application Structure

```typescript
// app/ (Next.js App Router)
├── api/               # API routes
│   ├── events/        # Event data endpoints
│   ├── results/       # Results data endpoints
│   └── benchmarks/    # Benchmark data endpoints
├── dashboard/         # Main dashboard
├── events/            # Event browser
├── results/           # Results analysis
└── benchmarks/        # Benchmark comparison
```

#### Data Integration

```typescript
// database/duckdb.ts
import Database from 'duckdb';

export class DataManager {
  private db: Database;
  
  async loadEvents(dataFolder: string): Promise<Event[]> {
    // Load JSONL files directly into DuckDB
    const query = `
      SELECT * FROM read_json_auto('${dataFolder}/events/*.jsonl')
      ORDER BY timestamp DESC
    `;
    
    return this.db.all(query);
  }
  
  async aggregateMetrics(suiteId: string): Promise<MetricsSummary> {
    // Complex aggregation queries
    const query = `
      SELECT 
        metric,
        COUNT(*) as total,
        SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed,
        AVG(score) as avg_score
      FROM read_json_auto('${dataFolder}/results/*.jsonl')
      WHERE suite_id = ?
      GROUP BY metric
    `;
    
    return this.db.all(query, [suiteId]);
  }
}
```

### 5. Registry System (`registry/`)

The registry enables sharing and discovery of evaluation components.

#### Component Discovery

```python
# registry/metrics/index.py
from typing import Dict, List
from .always_pass.config import AlwaysPassConfig
from .is_helpful.config import IsHelpfulConfig

METRICS_REGISTRY: Dict[str, type] = {
    "always_pass": AlwaysPassConfig,
    "is_helpful": IsHelpfulConfig,
}

def discover_metrics() -> List[str]:
    """Discover available metrics."""
    return list(METRICS_REGISTRY.keys())
```

#### Type-Safe Configuration

```python
# registry/metrics/is_helpful/config.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class IsHelpfulConfig:
    """Configuration for is_helpful metric."""
    threshold: float = 0.7
    llm_judge: bool = True
    judge_model: str = "gpt-4"
    custom_prompt: Optional[str] = None
    
    def validate(self) -> None:
        """Validate configuration."""
        if not 0 <= self.threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
```

## Data Flow Architecture

### 1. Data Collection Flow

```
Application Code → SDK Instrumentation → Event Capture → Storage
```

**Event Structure:**
```json
{
  "id": "evt_123",
  "timestamp": 1704067200,
  "provider": "openai",
  "model": "gpt-4",
  "prompt": "Explain quantum computing",
  "response": "Quantum computing is...",
  "metadata": {
    "duration_ms": 1500,
    "tokens_used": 150,
    "cost_usd": 0.003
  }
}
```

### 2. Evaluation Flow

```
Events → Metric Discovery → Suite Execution → Results Generation
```

**Result Structure:**
```json
{
  "event_id": "evt_123",
  "suite_id": "helpfulness_suite",
  "metric": "is_helpful",
  "score": 0.85,
  "passed": true,
  "timestamp": 1704067300,
  "metadata": {
    "reasoning": "Response provides clear explanation",
    "confidence": 0.9
  }
}
```

### 3. Visualization Flow

```
JSONL Files → DuckDB → API Endpoints → React Components
```

## Component Interactions

### SDK to CLI Integration

```python
# SDK writes events
sdk.store.save_event({
    "id": "evt_123",
    "timestamp": time.time(),
    "data": event_data
})

# CLI reads events
events = cli.load_events(data_folder)
results = cli.evaluate(events, suite_name)
```

### CLI to Studio Integration

```python
# CLI launches Studio
studio_process = subprocess.Popen([
    "node", "server.js",
    "--data-folder", str(data_folder),
    "--config", str(config_path)
])
```

### Registry Integration

```python
# Add component from registry
registry.add_metric("is_helpful", target_folder="./eval/metrics/")

# Discover local components
local_metrics = registry.discover_local_metrics("./eval/metrics/")
```

## Deployment Patterns

### Local Development

```bash
# Single-machine development
trainloop init
trainloop eval
trainloop studio
```

### Team Collaboration

```yaml
# Docker Compose setup
version: '3.8'
services:
  trainloop-studio:
    build: ./ui
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data
    environment:
      - TRAINLOOP_DATA_FOLDER=/app/data
```

### CI/CD Integration

```yaml
# GitHub Actions workflow
- name: Run TrainLoop Evaluation
  run: |
    trainloop eval --suite regression_tests
    trainloop benchmark --providers openai,anthropic
```

## Performance Characteristics

### SDK Performance

- **Overhead**: < 5ms per instrumented call
- **Memory**: < 10MB additional memory usage
- **Throughput**: > 1000 events/second with buffering

### CLI Performance

- **Evaluation**: ~100 events/second per metric
- **Parallel Processing**: Scales with available CPU cores
- **Memory**: Streaming processing for large datasets

### Studio Performance

- **Data Loading**: DuckDB enables sub-second queries on millions of events
- **Rendering**: Virtual scrolling for large datasets
- **Real-time Updates**: WebSocket integration for live data

## Security Considerations

### Data Privacy

- **Local Storage**: All data stored locally by default
- **Encryption**: Support for encrypted storage backends
- **Access Control**: File-system based access control

### API Security

- **No External Calls**: Evaluation runs entirely locally
- **Configurable Endpoints**: Optional LLM judge with configurable endpoints
- **Input Validation**: Comprehensive input sanitization

## Extensibility Points

### Custom Metrics

```python
# Easy to add new metrics
def custom_metric(event: dict) -> dict:
    """Custom evaluation logic."""
    return {
        "metric": "custom_metric",
        "score": calculate_custom_score(event),
        "passed": score > threshold
    }
```

### Custom Storage Backends

```python
# Support for cloud storage
class S3Store(Store):
    def save_event(self, event: dict) -> None:
        # S3 implementation
        pass
```

### Custom UI Components

```typescript
// Extensible React components
export function CustomChart({ data }: { data: ChartData }) {
  return (
    <div className="custom-chart">
      {/* Custom visualization */}
    </div>
  );
}
```

## Migration and Compatibility

### Version Compatibility

- **Backward Compatibility**: Maintained for data formats
- **Migration Tools**: Built-in migration utilities
- **API Versioning**: Semantic versioning for breaking changes

### Data Format Evolution

```python
# Support for multiple data format versions
def migrate_events(events: List[dict], target_version: str) -> List[dict]:
    """Migrate events to target format version."""
    migrated = []
    for event in events:
        if event.get("version") == "1.0":
            event = migrate_v1_to_v2(event)
        migrated.append(event)
    return migrated
```

## Future Architecture Considerations

### Planned Enhancements

1. **Distributed Evaluation** - Support for distributed metric calculation
2. **Real-time Streaming** - WebSocket support for live event processing
3. **Plugin System** - More flexible plugin architecture
4. **Cloud Integration** - Native cloud deployment options
5. **Advanced Analytics** - Machine learning-based evaluation metrics

### Scalability Roadmap

- **Horizontal Scaling**: Kubernetes-based deployment
- **Data Partitioning**: Automatic data partitioning strategies
- **Caching Layer**: Redis-based caching for improved performance
- **Load Balancing**: Support for multiple Studio instances

## Resources

- **[Local Development](./local-development.md)** - Setting up development environment
- **[Building from Source](./building-from-source.md)** - Building all components
- **[Testing Guide](./testing.md)** - Testing architecture and components
- **[Contributing Guide](./contributing.md)** - Contributing to the architecture

## Getting Help

For architecture-related questions:

- **Design Discussions**: [GitHub Discussions](https://github.com/trainloop/evals/discussions)
- **Architecture Issues**: [GitHub Issues](https://github.com/trainloop/evals/issues)
- **Implementation Questions**: Comment on relevant pull requests

---

This architecture guide provides the foundation for understanding how TrainLoop Evals components work together to provide a comprehensive LLM evaluation platform.