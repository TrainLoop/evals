---
sidebar_position: 6
---

# Production Setup and CI/CD

In this tutorial, you'll learn how to deploy TrainLoop Evals in production environments, set up automated evaluation pipelines, and integrate with your development workflow.

## What You'll Learn

- How to set up TrainLoop Evals in production environments
- CI/CD pipeline integration patterns
- Monitoring and alerting strategies
- Scaling considerations for high-volume applications
- Security best practices for production deployment

## Prerequisites

- Completed [Benchmarking and Model Comparison](benchmarking.md)
- Understanding of CI/CD concepts
- Access to a CI/CD platform (GitHub Actions, GitLab CI, etc.)
- Production environment access

## Production Architecture Overview

### Deployment Patterns

#### 1. Embedded Evaluation

```
Your Application → TrainLoop SDK → Event Data → Scheduled Evaluation
```

Best for: Applications with moderate LLM usage

#### 2. Centralized Evaluation

```
Multiple Apps → Central Data Store → TrainLoop CLI → Results Dashboard
```

Best for: Organizations with multiple LLM applications

#### 3. Event-Driven Evaluation

```
Application → Event Queue → TrainLoop Worker → Real-time Results
```

Best for: High-volume applications requiring immediate feedback

## Setting Up Production Environment

### 1. Environment Configuration

Create production-ready configuration:

```yaml
# trainloop.config.yaml (production)
trainloop:
  data_folder: "/var/lib/trainloop/data"
  log_level: "info"
  
  # Production data retention
  data_retention:
    events: 30  # Keep event data for 30 days
    results: 90  # Keep results for 90 days
  
  # Performance settings
  performance:
    batch_size: 1000
    max_concurrent_evaluations: 10
    evaluation_timeout: 300  # 5 minutes
  
  # Judge configuration
  judge:
    models:
      - openai/gpt-4o-mini  # Cost-effective for production
      - anthropic/claude-3-haiku-20240307
    calls_per_model_per_claim: 2  # Reduce for speed
    temperature: 0.1  # Consistent results
    timeout: 30
  
  # Monitoring
  monitoring:
    enabled: true
    metrics_endpoint: "http://prometheus:9090"
    alert_threshold: 0.7  # Alert if performance drops below 70%
```

### 2. Docker Deployment

Create production Docker setup:

```dockerfile
# Dockerfile.production
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -s /bin/bash trainloop
USER trainloop
WORKDIR /home/trainloop

# Install TrainLoop CLI
RUN pip install --user trainloop-cli

# Copy configuration
COPY --chown=trainloop:trainloop trainloop.config.yaml .
COPY --chown=trainloop:trainloop evaluation/ ./evaluation/

# Create data directory
RUN mkdir -p data/events data/results

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Default command
CMD ["trainloop", "studio", "--host", "0.0.0.0", "--port", "3000"]
```

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  trainloop-evaluator:
    build:
      context: .
      dockerfile: Dockerfile.production
    environment:
      - TRAINLOOP_DATA_FOLDER=/home/trainloop/data
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - trainloop_data:/home/trainloop/data
      - ./evaluation:/home/trainloop/evaluation:ro
    ports:
      - "3000:3000"
    restart: unless-stopped
    depends_on:
      - prometheus
      - grafana
  
  trainloop-scheduler:
    build:
      context: .
      dockerfile: Dockerfile.production
    environment:
      - TRAINLOOP_DATA_FOLDER=/home/trainloop/data
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - trainloop_data:/home/trainloop/data
      - ./evaluation:/home/trainloop/evaluation:ro
    command: ["sh", "-c", "while true; do trainloop eval && sleep 3600; done"]
    restart: unless-stopped
  
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped
  
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3001:3000"
    restart: unless-stopped

volumes:
  trainloop_data:
  prometheus_data:
  grafana_data:
```

### 3. Kubernetes Deployment

```yaml
# k8s/trainloop-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trainloop-evaluator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trainloop-evaluator
  template:
    metadata:
      labels:
        app: trainloop-evaluator
    spec:
      containers:
      - name: trainloop
        image: your-registry/trainloop-evaluator:latest
        ports:
        - containerPort: 3000
        env:
        - name: TRAINLOOP_DATA_FOLDER
          value: "/data"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-api-keys
              key: openai-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-api-keys
              key: anthropic-api-key
        volumeMounts:
        - name: data-volume
          mountPath: /data
        - name: config-volume
          mountPath: /app/trainloop.config.yaml
          subPath: trainloop.config.yaml
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: trainloop-data-pvc
      - name: config-volume
        configMap:
          name: trainloop-config
```

## CI/CD Pipeline Integration

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/evaluation-pipeline.yml
name: LLM Evaluation Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 */6 * * *'  # Run every 6 hours

jobs:
  evaluate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install trainloop-cli
        pip install -r requirements.txt
    
    - name: Set up TrainLoop
      run: |
        mkdir -p trainloop/data
        export TRAINLOOP_DATA_FOLDER="$(pwd)/trainloop/data"
    
    - name: Run application to collect data
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        TRAINLOOP_DATA_FOLDER: ${{ github.workspace }}/trainloop/data
      run: |
        # Run your application to generate test data
        python scripts/generate_test_data.py
    
    - name: Run evaluations
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        TRAINLOOP_DATA_FOLDER: ${{ github.workspace }}/trainloop/data
      run: |
        trainloop eval --config trainloop.config.yaml
    
    - name: Run benchmarks
      if: github.event_name == 'schedule'  # Only on scheduled runs
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        TRAINLOOP_DATA_FOLDER: ${{ github.workspace }}/trainloop/data
      run: |
        trainloop benchmark --max-samples 100
    
    - name: Check quality gates
      run: |
        python scripts/check_quality_gates.py
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: evaluation-results
        path: trainloop/data/results/
    
    - name: Notify on failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        text: "LLM Evaluation Pipeline failed on ${{ github.ref }}"
```

### 2. Quality Gates Script

```python
# scripts/check_quality_gates.py
import json
import sys
from pathlib import Path

def check_quality_gates():
    """Check if evaluation results meet quality thresholds"""
    
    # Define quality thresholds
    thresholds = {
        'minimum_pass_rate': 0.80,  # 80% of metrics must pass
        'critical_metrics': {
            'is_helpful': 0.85,
            'is_accurate': 0.90,
            'is_safe': 0.95
        }
    }
    
    # Load latest results
    results_dir = Path('trainloop/data/results')
    latest_result = max(results_dir.glob('*.json'), key=lambda p: p.stat().st_mtime)
    
    with open(latest_result) as f:
        results = json.load(f)
    
    # Check overall pass rate
    total_metrics = len(results['metrics'])
    passed_metrics = sum(1 for metric in results['metrics'] if metric['passed'])
    overall_pass_rate = passed_metrics / total_metrics
    
    if overall_pass_rate < thresholds['minimum_pass_rate']:
        print(f"❌ Overall pass rate ({overall_pass_rate:.2%}) below threshold ({thresholds['minimum_pass_rate']:.2%})")
        sys.exit(1)
    
    # Check critical metrics
    for metric_name, threshold in thresholds['critical_metrics'].items():
        metric_result = next((m for m in results['metrics'] if m['name'] == metric_name), None)
        if metric_result and metric_result['score'] < threshold:
            print(f"❌ Critical metric {metric_name} ({metric_result['score']:.2%}) below threshold ({threshold:.2%})")
            sys.exit(1)
    
    print("✅ All quality gates passed!")
    return True

if __name__ == "__main__":
    check_quality_gates()
```

### 3. GitLab CI Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - test
  - evaluate
  - benchmark
  - deploy

variables:
  TRAINLOOP_DATA_FOLDER: "${CI_PROJECT_DIR}/trainloop/data"

before_script:
  - pip install trainloop-cli
  - mkdir -p trainloop/data

test:
  stage: test
  script:
    - python -m pytest tests/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

evaluate:
  stage: evaluate
  script:
    - python scripts/generate_test_data.py
    - trainloop eval
    - python scripts/check_quality_gates.py
  artifacts:
    paths:
      - trainloop/data/results/
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

benchmark:
  stage: benchmark
  script:
    - trainloop benchmark --max-samples 100
  artifacts:
    paths:
      - trainloop/data/results/
    expire_in: 1 month
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_COMMIT_BRANCH == "main"
  only:
    - schedules

deploy:
  stage: deploy
  script:
    - docker build -t trainloop-evaluator .
    - docker push $CI_REGISTRY_IMAGE/trainloop-evaluator:latest
    - kubectl apply -f k8s/
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## Monitoring and Alerting

### 1. Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'trainloop-evaluator'
    static_configs:
      - targets: ['trainloop-evaluator:3000']
    scrape_interval: 30s
    metrics_path: '/metrics'
```

### 2. Custom Metrics Collection

```python
# scripts/collect_metrics.py
import json
import time
from prometheus_client import start_http_server, Gauge, Counter, Histogram

# Define metrics
evaluation_score = Gauge('trainloop_evaluation_score', 'Overall evaluation score', ['suite'])
evaluation_duration = Histogram('trainloop_evaluation_duration_seconds', 'Evaluation duration')
evaluation_count = Counter('trainloop_evaluations_total', 'Total evaluations', ['status'])
llm_api_calls = Counter('trainloop_llm_api_calls_total', 'LLM API calls', ['provider', 'model'])

def collect_and_report_metrics():
    """Collect TrainLoop metrics and report to Prometheus"""
    
    # Load latest results
    results_dir = Path('trainloop/data/results')
    latest_result = max(results_dir.glob('*.json'), key=lambda p: p.stat().st_mtime)
    
    with open(latest_result) as f:
        results = json.load(f)
    
    # Report metrics
    for suite_name, suite_results in results['suites'].items():
        evaluation_score.labels(suite=suite_name).set(suite_results['score'])
    
    evaluation_duration.observe(results['duration'])
    evaluation_count.labels(status='success').inc()
    
    # Report LLM API usage
    for call in results['api_calls']:
        llm_api_calls.labels(
            provider=call['provider'],
            model=call['model']
        ).inc()

if __name__ == "__main__":
    start_http_server(8000)
    
    while True:
        try:
            collect_and_report_metrics()
            time.sleep(60)  # Report every minute
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            evaluation_count.labels(status='error').inc()
```

### 3. Grafana Dashboard

```json
{
  "dashboard": {
    "title": "TrainLoop Evals Dashboard",
    "panels": [
      {
        "title": "Overall Evaluation Score",
        "type": "stat",
        "targets": [
          {
            "expr": "avg(trainloop_evaluation_score)",
            "legendFormat": "Average Score"
          }
        ]
      },
      {
        "title": "Evaluation Scores by Suite",
        "type": "timeseries",
        "targets": [
          {
            "expr": "trainloop_evaluation_score",
            "legendFormat": "{{suite}}"
          }
        ]
      },
      {
        "title": "Evaluation Duration",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(trainloop_evaluation_duration_seconds_sum[5m]) / rate(trainloop_evaluation_duration_seconds_count[5m])",
            "legendFormat": "Average Duration"
          }
        ]
      },
      {
        "title": "API Usage by Provider",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (provider) (trainloop_llm_api_calls_total)",
            "legendFormat": "{{provider}}"
          }
        ]
      }
    ]
  }
}
```

## Scaling Considerations

### 1. Horizontal Scaling

```yaml
# k8s/trainloop-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: trainloop-evaluator-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: trainloop-evaluator
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Data Partitioning

```python
# scripts/partition_data.py
import os
from datetime import datetime, timedelta

def partition_data_by_date():
    """Partition event data by date for better performance"""
    
    data_dir = Path(os.environ['TRAINLOOP_DATA_FOLDER'])
    events_dir = data_dir / 'events'
    
    # Create date-based directories
    for event_file in events_dir.glob('*.jsonl'):
        file_date = datetime.fromtimestamp(event_file.stat().st_mtime)
        date_dir = events_dir / file_date.strftime('%Y/%m/%d')
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Move file to date directory
        event_file.rename(date_dir / event_file.name)

def cleanup_old_data():
    """Remove old data based on retention policy"""
    
    data_dir = Path(os.environ['TRAINLOOP_DATA_FOLDER'])
    retention_days = 30
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    for old_file in data_dir.rglob('*.jsonl'):
        if datetime.fromtimestamp(old_file.stat().st_mtime) < cutoff_date:
            old_file.unlink()
            print(f"Removed old file: {old_file}")
```

### 3. Distributed Evaluation

```python
# scripts/distributed_evaluation.py
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def evaluate_partition(partition_files):
    """Evaluate a partition of data files"""
    # Set up separate data folder for this partition
    partition_data_folder = f"/tmp/trainloop_partition_{mp.current_process().pid}"
    os.environ['TRAINLOOP_DATA_FOLDER'] = partition_data_folder
    
    # Copy files to partition folder
    for file in partition_files:
        shutil.copy(file, partition_data_folder)
    
    # Run evaluation
    subprocess.run(['trainloop', 'eval'], check=True)
    
    # Return results
    results_dir = Path(partition_data_folder) / 'results'
    return list(results_dir.glob('*.json'))

def distributed_evaluation():
    """Run evaluation across multiple processes"""
    
    # Get all event files
    data_dir = Path(os.environ['TRAINLOOP_DATA_FOLDER'])
    event_files = list((data_dir / 'events').glob('*.jsonl'))
    
    # Partition files
    num_partitions = mp.cpu_count()
    partitions = [event_files[i::num_partitions] for i in range(num_partitions)]
    
    # Run evaluation in parallel
    with ProcessPoolExecutor(max_workers=num_partitions) as executor:
        results = list(executor.map(evaluate_partition, partitions))
    
    # Combine results
    combined_results = combine_evaluation_results(results)
    return combined_results
```

## Security Best Practices

### 1. API Key Management

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: llm-api-keys
type: Opaque
stringData:
  openai-api-key: "your-openai-key"
  anthropic-api-key: "your-anthropic-key"
```

### 2. Network Security

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: trainloop-network-policy
spec:
  podSelector:
    matchLabels:
      app: trainloop-evaluator
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS for API calls
  - to: []
    ports:
    - protocol: TCP
      port: 53   # DNS
  - to: []
    ports:
    - protocol: UDP
      port: 53   # DNS
```

### 3. Data Protection

```python
# scripts/secure_data.py
import os
import hashlib
from cryptography.fernet import Fernet

def encrypt_sensitive_data():
    """Encrypt sensitive data in event files"""
    
    key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
    cipher = Fernet(key)
    
    data_dir = Path(os.environ['TRAINLOOP_DATA_FOLDER'])
    
    for event_file in data_dir.glob('events/*.jsonl'):
        # Read, encrypt, and write back
        with open(event_file, 'rb') as f:
            encrypted_data = cipher.encrypt(f.read())
        
        with open(event_file, 'wb') as f:
            f.write(encrypted_data)

def anonymize_data():
    """Remove or hash personally identifiable information"""
    
    data_dir = Path(os.environ['TRAINLOOP_DATA_FOLDER'])
    
    for event_file in data_dir.glob('events/*.jsonl'):
        anonymized_lines = []
        
        with open(event_file, 'r') as f:
            for line in f:
                event = json.loads(line)
                
                # Hash user IDs
                if 'user_id' in event:
                    event['user_id'] = hashlib.sha256(event['user_id'].encode()).hexdigest()[:8]
                
                # Remove IP addresses
                if 'ip_address' in event:
                    del event['ip_address']
                
                anonymized_lines.append(json.dumps(event))
        
        with open(event_file, 'w') as f:
            f.write('\n'.join(anonymized_lines))
```

## Operational Runbooks

### 1. Deployment Checklist

```markdown
# TrainLoop Evals Deployment Checklist

## Pre-Deployment
- [ ] API keys are configured and valid
- [ ] Configuration files are reviewed and approved
- [ ] Resource limits are set appropriately
- [ ] Monitoring and alerting are configured
- [ ] Backup strategy is in place

## Deployment
- [ ] Run canary deployment first
- [ ] Monitor system health during deployment
- [ ] Verify evaluation pipeline is running
- [ ] Check data collection is working
- [ ] Validate dashboard access

## Post-Deployment
- [ ] Run smoke tests
- [ ] Monitor performance metrics
- [ ] Check log files for errors
- [ ] Verify alerting is working
- [ ] Update documentation
```

### 2. Troubleshooting Guide

```markdown
# TrainLoop Evals Troubleshooting Guide

## Common Issues

### Evaluation Pipeline Failures
**Symptoms:** Evaluations not running or failing
**Causes:** API key issues, configuration errors, resource constraints
**Solutions:**
1. Check API key validity
2. Verify configuration syntax
3. Check resource utilization
4. Review error logs

### Data Collection Issues
**Symptoms:** No event data being collected
**Causes:** SDK not initialized, wrong data folder, network issues
**Solutions:**
1. Verify SDK initialization
2. Check TRAINLOOP_DATA_FOLDER environment variable
3. Test network connectivity
4. Review application logs

### Performance Issues
**Symptoms:** Slow evaluation, high resource usage
**Causes:** Large datasets, inefficient metrics, resource constraints
**Solutions:**
1. Optimize metrics for performance
2. Implement data partitioning
3. Scale resources horizontally
4. Use caching where appropriate
```

## Best Practices Summary

### 1. Configuration Management
- Use environment-specific configurations
- Store sensitive data in secure secret management
- Version control all configuration files
- Document configuration changes

### 2. Monitoring and Alerting
- Set up comprehensive monitoring
- Define appropriate alert thresholds
- Use structured logging
- Implement health checks

### 3. Performance Optimization
- Partition large datasets
- Use efficient metrics
- Implement caching strategies
- Monitor resource utilization

### 4. Security
- Encrypt sensitive data
- Use secure secret management
- Implement network security policies
- Regular security audits

## Congratulations! 🎉

You've completed the TrainLoop Evals tutorial series! You now have the knowledge to:

- Set up comprehensive LLM evaluation systems
- Write effective metrics and test suites
- Use advanced features like LLM Judge and benchmarking
- Deploy and monitor evaluations in production

## Next Steps

- Explore the [guides](../guides/index.md) for specific implementation patterns
- Check the [reference documentation](../reference/index.md) for detailed API information
- Join the community and share your experiences

Keep evaluating, keep improving! 🚀