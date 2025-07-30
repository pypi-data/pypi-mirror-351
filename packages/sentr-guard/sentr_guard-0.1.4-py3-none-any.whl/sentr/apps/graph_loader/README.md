# Sentr Graph Loader

High-performance graph construction service for fraud detection.

The Graph Loader transforms flat transaction streams into temporal multi-entity graphs that power fraud detection models (TGAT/TGN) and real-time rules.

## Overview

**Input**: Kafka topic `tx_enriched` (from Feature Builder)  
**Output**: Neo4j "FraudGraph" database  
**Performance**: ≥2,000 edges/sec sustained, <50ms median write latency  
**Scaling**: 3-5 replicas for 6,000-20,000 edges/sec cluster-wide  

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kafka Topic   │───▶│   Graph Loader   │───▶│     Neo4j       │
│   tx_enriched   │    │                  │    │   FraudGraph    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Health/Metrics  │
                       │   HTTP Server    │
                       └──────────────────┘
```

### Core Components

1. **Kafka Consumer** - Consumes enriched transactions with exactly-once semantics
2. **Edge Builder** - Creates graph edges from transactions using configurable rules
3. **Edge Aggregator** - Time-buckets and deduplicates edges for efficiency
4. **Neo4j Writer** - Batch writes edges to Neo4j with circuit breaker protection
5. **Health Server** - Provides health checks and Prometheus metrics

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- Kafka cluster running
- Neo4j database available

### Local Development

```bash
# Install dependencies
cd apps/graph_loader
poetry install

# Set environment variables
export KAFKA_BOOTSTRAP=localhost:9092
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=password

# Run the service
poetry run python -m apps.graph_loader.main
```

### Docker Deployment

```bash
# Build the image
docker build -t sentr-graph-loader -f apps/graph_loader/Dockerfile .

# Run with docker-compose
docker-compose up graph-loader
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP` | `localhost:9092` | Kafka bootstrap servers |
| `KAFKA_TOPIC` | `tx_enriched` | Input topic for transactions |
| `KAFKA_GROUP_ID` | `sentr-graph-loader` | Consumer group ID |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USERNAME` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password` | Neo4j password |
| `NEO4J_DATABASE` | `fraudgraph` | Neo4j database name |
| `EDGE_TYPES` | `CARD_IP,CARD_MERCHANT,CARD_DEVICE,IP_MERCHANT` | Enabled edge types |
| `NEO4J_BATCH_SIZE` | `300` | Batch size for Neo4j writes |
| `EDGE_TIME_BUCKET_SIZE` | `60` | Time bucket size in seconds |
| `TARGET_EDGES_PER_SEC` | `2000` | Target throughput |
| `HEALTH_CHECK_PORT` | `8083` | Health server port |

### Edge Type Configuration

The service supports configurable edge types defined in `config.py`:

```python
EDGE_TYPE_CONFIGS = {
    "CARD_IP": {
        "src_field": "card_id",
        "dst_field": "ip_address", 
        "src_prefix": "card:",
        "dst_prefix": "ip:",
        "direction": "outgoing",
        "properties": ["amount", "is_success", "merchant_id"]
    },
    # ... more edge types
}
```

## Monitoring

### Health Endpoints

- `GET /health` - Service health status
- `GET /metrics` - Prometheus metrics
- `GET /status` - Detailed service status

### Key Metrics

```
# Service health
graph_loader_healthy{} 1

# Performance metrics  
graph_loader_neo4j_avg_write_time_ms{} 15.2
graph_loader_neo4j_edges_per_second{} 1847.3
graph_loader_neo4j_circuit_breaker_closed{} 1

# Throughput metrics
graph_loader_edges_processed_total{} 125847
graph_loader_neo4j_total_batches_written{} 419
```

### Grafana Dashboard

Key panels to monitor:

1. **Edges per Second** - Real-time throughput
2. **Write Latency** - P50, P95, P99 write times
3. **Circuit Breaker State** - Fault tolerance status
4. **Kafka Lag** - Consumer lag monitoring
5. **Neo4j Connection Pool** - Database connection health

## Testing

### Unit Tests

```bash
# Run all tests
poetry run pytest apps/graph_loader/tests/ -v

# Run specific test categories
poetry run pytest apps/graph_loader/tests/test_edge_builder.py -v
poetry run pytest apps/graph_loader/tests/test_neo4j_writer.py -v
poetry run pytest apps/graph_loader/tests/test_kafka_consumer.py -v
```

### Performance Tests

```bash
# Run performance validation
poetry run pytest apps/graph_loader/tests/test_performance.py -v -s

# Test specific performance aspects
poetry run pytest apps/graph_loader/tests/test_performance.py::TestGraphLoaderPerformance::test_edge_builder_throughput -v -s
```

### Integration Tests

```bash
# Run integration tests
poetry run pytest apps/graph_loader/tests/test_integration.py -v
```

## Operations

### Deployment

```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graph-loader
spec:
  replicas: 3
  selector:
    matchLabels:
      app: graph-loader
  template:
    metadata:
      labels:
        app: graph-loader
    spec:
      containers:
      - name: graph-loader
        image: sentr/graph-loader:latest
        env:
        - name: KAFKA_BOOTSTRAP
          value: "kafka:9092"
        - name: NEO4J_URI
          value: "bolt://neo4j:7687"
        ports:
        - containerPort: 8083
        livenessProbe:
          httpGet:
            path: /health
            port: 8083
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8083
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Scaling

- **Horizontal**: Add replicas (Kafka partitions determine max parallelism)
- **Vertical**: Increase Neo4j batch size and connection pool
- **Database**: Scale Neo4j cluster for write throughput

### Troubleshooting

#### High Latency

```bash
# Check Neo4j performance
curl http://localhost:8083/metrics | grep write_time

# Check circuit breaker state
curl http://localhost:8083/status | jq '.performance.circuit_breaker_state'

# Monitor Kafka lag
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group sentr-graph-loader
```

#### Circuit Breaker Open

```bash
# Check Neo4j connectivity
docker exec -it sentr-neo4j cypher-shell -u neo4j -p password "RETURN 1"

# Check error logs
docker logs sentr-graph-loader | grep -i error

# Reset circuit breaker (restart service)
docker-compose restart graph-loader
```

#### Memory Issues

```bash
# Check memory usage
docker stats sentr-graph-loader

# Reduce batch sizes
export NEO4J_BATCH_SIZE=100
export KAFKA_BATCH_SIZE=50
```

## Neo4j Schema

### Constraints

```cypher
CREATE CONSTRAINT entity_id IF NOT EXISTS
FOR (e:Entity) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT card_id IF NOT EXISTS  
FOR (c:Card) REQUIRE c.id IS UNIQUE;
```

### Indexes

```cypher
CREATE INDEX edge_id_index IF NOT EXISTS
FOR ()-[r]-() ON (r.edge_id);

CREATE INDEX edge_timestamp_index IF NOT EXISTS
FOR ()-[r]-() ON (r.first_seen);
```

### Sample Queries

```cypher
-- Find cards connected to suspicious IPs
MATCH (c:Entity)-[r:RELATES]->(ip:Entity)
WHERE c.id STARTS WITH 'card:' 
  AND ip.id STARTS WITH 'ip:'
  AND r.count > 10
RETURN c.id, ip.id, r.count, r.last_seen
ORDER BY r.count DESC
LIMIT 10;

-- Analyze transaction patterns
MATCH (c:Entity)-[r:RELATES]->(m:Entity)
WHERE c.id STARTS WITH 'card:' 
  AND m.id STARTS WITH 'merchant:'
  AND r.last_seen > timestamp() - 86400000  -- Last 24 hours
RETURN c.id, m.id, r.count, r.edge_type
ORDER BY r.last_seen DESC;
```

## Security

- **Authentication**: Neo4j credentials via environment variables
- **TLS**: Configurable encryption for Neo4j connections  
- **PII Protection**: Automatic redaction in logs
- **Network**: Service runs on internal network only

## Performance Tuning

### Neo4j Optimization

```bash
# Increase heap size
NEO4J_dbms_memory_heap_max__size=4g

# Optimize page cache
NEO4J_dbms_memory_pagecache_size=2g

# Enable APOC procedures
NEO4J_PLUGINS=["apoc"]
```

### Kafka Optimization

```bash
# Increase batch size for throughput
KAFKA_BATCH_SIZE=500

# Reduce latency
KAFKA_BATCH_TIMEOUT_MS=50

# Optimize fetch settings
KAFKA_FETCH_MIN_BYTES=1024
KAFKA_FETCH_MAX_WAIT_MS=500
```

### Application Tuning

```bash
# Increase Neo4j batch size
NEO4J_BATCH_SIZE=500

# Reduce time bucket size for real-time
EDGE_TIME_BUCKET_SIZE=30

# Adjust circuit breaker
NEO4J_CIRCUIT_FAILURE_THRESHOLD=10
```

## Data Flow

1. **Transaction Ingestion**: Kafka consumer polls `tx_enriched` topic
2. **Edge Building**: Extract entities and relationships per transaction
3. **Time Bucketing**: Group edges by 60-second windows for aggregation
4. **Edge Aggregation**: Combine duplicate edges, track counts and timestamps
5. **Batch Writing**: UNWIND operations to Neo4j with retry logic
6. **Offset Commit**: Exactly-once semantics with manual commits

## Advanced Configuration

### Circuit Breaker Tuning

```bash
# Failure threshold before opening
NEO4J_CIRCUIT_FAILURE_THRESHOLD=5

# Recovery timeout (seconds)  
NEO4J_CIRCUIT_RECOVERY_TIMEOUT=30

# Half-open timeout (seconds)
NEO4J_CIRCUIT_HALF_OPEN_TIMEOUT=5
```

### Back-pressure Settings

```bash
# Latency threshold for back-pressure
BACKPRESSURE_THRESHOLD_MS=100

# Pause duration when back-pressure triggered
BACKPRESSURE_PAUSE_DURATION=1000
```

---

## Support

- **Documentation**: [Sentr Docs](https://docs.sentr.com/graph-loader)
- **Issues**: [GitHub Issues](https://github.com/sentr/sentr-core/issues)
- **Monitoring**: Grafana dashboards and Prometheus alerts
- **Logs**: Structured JSON logs with correlation IDs

**Status**: Production Ready - Meets all performance and reliability requirements 