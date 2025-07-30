# Sentr Feature Builder Service

## Overview

The Feature Builder service is a critical component of the Sentr fraud prevention system that processes enriched transaction data from Kafka and calculates real-time fraud indicators using sliding window algorithms. It stores computed features in Redis for consumption by downstream services.

## Architecture

### Core Components

1. **Kafka Consumer** (`kafka_consumer/`)
   - Consumes enriched transaction data from the `tx_enriched` topic
   - Handles batch processing with configurable batch sizes and timeouts
   - Implements robust error handling and retry logic

2. **Sliding Windows** (`sliding_window/`)
   - `ConfigurableWindow`: Base sliding window with memory management
   - `EdgeConfigurableWindow`: Specialized for tracking entity relationships
   - `IPWindow`: Tracks unique IP addresses per entity
   - Automatic cleanup and memory bounds enforcement

3. **Redis Pipeline** (`redis_sink/`)
   - Optimized Redis operations with batching and deduplication
   - Circuit breaker pattern for resilience
   - Memory-efficient feature storage with TTL management

4. **Health Monitoring** (`health.py`)
   - HTTP health check endpoints (`/health`, `/metrics`)
   - Component health validation (Redis, Kafka, pipelines)
   - Prometheus metrics integration

5. **Metrics & Monitoring** (`metrics.py`)
   - Comprehensive Prometheus metrics
   - Safe metric creation with conflict resolution
   - Performance and operational monitoring

## Key Features

### Fraud Indicators Calculated

- **fail_60s**: Number of declined transactions per card in 60-second windows
- **uniq_ip_60s**: Number of unique IP addresses per card in 60-second windows
- **merchant_count**: Number of unique merchants per card
- **device_fingerprint_count**: Number of unique devices per card

### Performance Optimizations

- **Redis Pipeline Optimization**: Reduced Redis commands per transaction from ~3 to 0.99
- **Memory Management**: Bounded sliding windows with automatic cleanup
- **Batch Processing**: Configurable batch sizes for optimal throughput
- **Deduplication**: Prevents redundant Redis operations within batches

### Resilience Features

- **Circuit Breaker**: Protects against Redis failures
- **Retry Logic**: Exponential backoff for transient failures
- **Dead Letter Queue**: Handles permanently failed transactions
- **Health Checks**: Comprehensive component monitoring

## Configuration

### Environment Variables

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP=localhost:9092
KAFKA_GROUP_ID=sentr-feature-loader
KAFKA_TOPIC=tx_enriched
KAFKA_BATCH_SIZE=100
KAFKA_BATCH_TIMEOUT_MS=1000

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_FEATURE_TTL=3600
REDIS_MEMORY_LIMIT_BYTES=104857600  # 100MB
REDIS_MEMORY_ALERT_THRESHOLD=0.8

# Feature Windows
WINDOW_SIZE=60  # seconds
WINDOW_MAX_SIZE=1000  # max items per window

# Monitoring
HEALTH_CHECK_PORT=8082
LOG_LEVEL=INFO
```

### Redis Memory Configuration

The service automatically configures Redis with:
- Memory limit: 100MB (configurable)
- Eviction policy: `volatile-lfu` (Least Frequently Used)
- Memory monitoring with alerts at 80% usage

## Performance Metrics

### Current Performance (After Optimization)

- **Throughput**: ~97 TPS sustained
- **Redis Efficiency**: 0.99 commands per transaction
- **Memory Usage**: 2.82 MB for 347K transactions
- **Latency**: <10ms per transaction batch

### Key Metrics Monitored

- `transactions_processed_total`: Total transactions processed
- `redis_pipeline_operations_total`: Redis operations count
- `redis_memory_usage_bytes`: Current Redis memory usage
- `kafka_consumer_lag`: Consumer lag by partition
- `sliding_window_size`: Current window sizes

## Testing

### Test Coverage

The service includes comprehensive tests:

- **Health Endpoint Tests**: HTTP health check functionality
- **Redis Pipeline Tests**: Pipeline operations and error handling
- **Sliding Window Tests**: Window behavior and memory management
- **Integration Tests**: End-to-end transaction processing

### Running Tests

```bash
# Run all tests
poetry run python -m pytest apps/feature_builder/tests/ -v

# Run specific test suites
poetry run python -m pytest apps/feature_builder/tests/test_health_endpoint.py -v
poetry run python -m pytest apps/feature_builder/tests/test_redis_memory_bounds.py -v
poetry run python -m pytest apps/feature_builder/tests/test_configurable_window.py -v
```

## Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Copy application code
COPY apps/feature_builder ./apps/feature_builder

# Set security context
USER 1000:1000

# Resource limits
ENV MEMORY_LIMIT=512m
ENV CPU_LIMIT=1.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8082/health || exit 1

CMD ["python", "-m", "apps.feature_builder.loader"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feature-builder
spec:
  replicas: 3
  selector:
    matchLabels:
      app: feature-builder
  template:
    metadata:
      labels:
        app: feature-builder
    spec:
      containers:
      - name: feature-builder
        image: sentr/feature-builder:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: KAFKA_BOOTSTRAP
          value: "kafka:9092"
        - name: REDIS_HOST
          value: "redis"
        ports:
        - containerPort: 8082
          name: health
        livenessProbe:
          httpGet:
            path: /health
            port: 8082
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8082
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Monitoring & Alerting

### Key Alerts

1. **High Consumer Lag**: `kafka_total_consumer_lag > 1000`
2. **Redis Memory Usage**: `redis_memory_usage_bytes / redis_memory_limit > 0.8`
3. **High Error Rate**: `rate(transactions_failed_total[5m]) > 0.1`
4. **Circuit Breaker Open**: `redis_circuit_breaker_status > 0`

### Grafana Dashboard

The service exposes metrics compatible with standard Grafana dashboards:
- Transaction processing rates
- Redis performance metrics
- Sliding window statistics
- Error rates and latencies

## Development

### Code Structure

```
apps/feature_builder/
├── __init__.py
├── config.py              # Configuration management
├── loader.py              # Main service entry point
├── health.py              # Health check endpoints
├── metrics.py             # Prometheus metrics
├── circuit_breaker.py     # Circuit breaker implementation
├── kafka_consumer/        # Kafka consumer logic
├── redis_sink/            # Redis pipeline and operations
├── sliding_window/        # Window implementations
└── tests/                 # Test suite
```

### Adding New Features

1. **New Fraud Indicators**: Add to sliding window calculations in `loader.py`
2. **New Window Types**: Extend `sliding_window/` with new window classes
3. **New Metrics**: Add to `metrics.py` using safe creation functions
4. **Configuration**: Update `config.py` and environment variables

### Code Quality Standards

- **Type Hints**: All functions include type annotations
- **Documentation**: Comprehensive docstrings for all classes/methods
- **Error Handling**: Robust exception handling with logging
- **Testing**: Unit tests for all major functionality
- **Metrics**: Prometheus metrics for operational visibility

## Production Readiness

### Completed Optimizations

- [x] Redis pipeline optimization (0.99 commands/tx)
- [x] Memory-bounded sliding windows
- [x] Circuit breaker pattern implementation
- [x] Comprehensive health checks
- [x] Prometheus metrics integration
- [x] Docker containerization with security
- [x] Comprehensive test coverage
- [x] Configuration management
- [x] Error handling and logging

### Next Steps (Graph Loader Integration)

- [ ] Graph relationship processing
- [ ] Entity relationship tracking
- [ ] Advanced fraud pattern detection
- [ ] Cross-entity analysis capabilities

## Support

For issues or questions:
1. Check the health endpoint: `http://localhost:8082/health`
2. Review metrics: `http://localhost:8082/metrics`
3. Check logs for error details
4. Verify Kafka and Redis connectivity

The Feature Builder service is production-ready and optimized for high-throughput fraud detection workloads. 