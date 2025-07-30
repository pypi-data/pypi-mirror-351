"""
Metrics module for Sentr Feature Loader.

Defines Prometheus metrics and helper functions for monitoring the service.
"""

import logging

import prometheus_client
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Global registry for metrics to prevent conflicts
_metrics_registry = {}


def safe_counter(name, doc, labels=()):
    """
    Safely create or retrieve a Counter metric, handling re-registration
    """
    if name in _metrics_registry:
        return _metrics_registry[name]

    try:
        metric = Counter(name, doc, labels)
        _metrics_registry[name] = metric
        return metric
    except ValueError as e:
        # Metric already exists in Prometheus registry
        logger.warning(f"Counter {name} already exists: {e}")
        # Try to get it from the registry
        try:
            existing_metric = prometheus_client.REGISTRY._names_to_collectors[name]
            _metrics_registry[name] = existing_metric
            return existing_metric
        except KeyError:
            # Create a dummy metric to prevent errors
            return _DummyMetric()


def safe_gauge(name, doc, labels=()):
    """
    Safely create or retrieve a Gauge metric, handling re-registration
    """
    if name in _metrics_registry:
        return _metrics_registry[name]

    try:
        metric = Gauge(name, doc, labels)
        _metrics_registry[name] = metric
        return metric
    except ValueError as e:
        logger.warning(f"Gauge {name} already exists: {e}")
        try:
            existing_metric = prometheus_client.REGISTRY._names_to_collectors[name]
            _metrics_registry[name] = existing_metric
            return existing_metric
        except KeyError:
            return _DummyMetric()


def safe_histogram(name, doc, labels=(), buckets=None):
    """
    Safely create or retrieve a Histogram metric, handling re-registration
    """
    if name in _metrics_registry:
        return _metrics_registry[name]

    try:
        # Use default buckets if none provided
        if buckets is None:
            buckets = (
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
                float("inf"),
            )

        metric = Histogram(name, doc, labels, buckets=buckets)
        _metrics_registry[name] = metric
        return metric
    except ValueError as e:
        logger.warning(f"Histogram {name} already exists: {e}")
        try:
            existing_metric = prometheus_client.REGISTRY._names_to_collectors[name]
            _metrics_registry[name] = existing_metric
            return existing_metric
        except KeyError:
            return _DummyMetric()


class _DummyMetric:
    """Dummy metric that does nothing to prevent errors"""

    def inc(self, amount=1):
        pass

    def dec(self, amount=1):
        pass

    def set(self, value):
        pass

    def observe(self, value):
        pass

    def labels(self, **kwargs):
        return self


# Define metrics with appropriate labels
# Service health metrics
HEALTH_CHECK_TOTAL = safe_counter(
    "health_check_total", "Total number of health checks", ["status"]
)

# Kafka metrics
KAFKA_CONNECT_ATTEMPTS = safe_counter(
    "kafka_connect_attempts_total", "Number of Kafka connection attempts"
)

KAFKA_CONNECTION_ERRORS = safe_counter(
    "kafka_connection_errors_total", "Number of Kafka connection errors"
)

KAFKA_CONSUMER_LAG = safe_gauge(
    "kafka_consumer_lag", "Consumer lag by partition", ["topic", "partition"]
)

KAFKA_TOTAL_LAG = safe_gauge(
    "kafka_total_consumer_lag", "Total consumer lag across all partitions"
)

KAFKA_MESSAGES_CONSUMED = safe_counter(
    "kafka_messages_consumed_total", "Number of Kafka messages consumed"
)

KAFKA_PROCESS_TIME = safe_histogram(
    "kafka_message_process_time_seconds",
    "Time to process a Kafka message batch",
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
)

# Redis metrics
REDIS_CONNECTION_ATTEMPTS = safe_counter(
    "redis_connection_attempts_total", "Number of Redis connection attempts"
)

REDIS_CONNECTION_ERRORS = safe_counter(
    "redis_connection_errors_total", "Number of Redis connection errors"
)

REDIS_OPERATIONS = safe_counter(
    "redis_operations_total", "Number of Redis operations", ["operation", "status"]
)

REDIS_OPERATION_TIME = safe_histogram(
    "redis_operation_time_seconds",
    "Time to perform a Redis operation",
    ["operation"],
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5),
)

REDIS_PIPELINE_SIZE = safe_histogram(
    "redis_pipeline_size",
    "Number of commands in a Redis pipeline",
    buckets=(1, 5, 10, 50, 100, 500, 1000),
)

REDIS_PIPELINE_FLUSH_TIME = safe_histogram(
    "redis_pipeline_flush_time_seconds",
    "Time to flush a Redis pipeline",
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)

REDIS_MEMORY_USAGE = safe_gauge(
    "redis_memory_usage_bytes", "Redis memory usage in bytes"
)

REDIS_PIPELINE_OPS = safe_counter(
    "redis_pipeline_operations_total", "Total Redis pipeline operations", ["operation"]
)

REDIS_PIPELINE_FLUSH = safe_counter(
    "redis_pipeline_flush_total", "Total Redis pipeline flushes"
)

REDIS_ERRORS = safe_counter("redis_errors_total", "Total Redis errors")

# Feature processing metrics
TX_PROCESSED = safe_counter(
    "transactions_processed_total", "Number of transactions processed"
)

TX_FAILED = safe_counter(
    "transactions_failed_total", "Number of transactions that failed processing"
)

FEATURE_UPDATES = safe_counter(
    "feature_updates_total", "Number of feature updates", ["feature"]
)

FEATURE_COUNT = safe_counter(
    "feature_count_total", "Total number of features calculated"
)

BATCH_PROCESSING_LATENCY = safe_histogram(
    "batch_processing_latency_seconds",
    "Time to process a batch of transactions",
    ["result"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0),
)

WINDOW_SIZE = safe_gauge(
    "sliding_window_size", "Current size of sliding windows", ["window_type"]
)

WINDOW_COUNT = safe_gauge(
    "sliding_window_count", "Number of sliding windows", ["window_type"]
)

SERVICE_LAST_SUCCESS = safe_gauge(
    "service_last_success_timestamp", "Timestamp of last successful operation"
)

ERROR_COUNT = safe_counter(
    "error_count_total", "Number of errors encountered", ["type"]
)


# Helper functions for updating metrics
def update_window_metrics(windows):
    """Update window-related metrics"""
    for window_type, window_dict in windows.items():
        WINDOW_COUNT.labels(window_type=window_type).set(len(window_dict))


def update_kafka_lag_metrics(consumer):
    """Update Kafka consumer lag metrics"""
    try:
        assignments = consumer.assignment()
        if not assignments:
            return

        end_offsets = consumer.end_offsets(assignments)
        total_lag = 0

        for tp in assignments:
            try:
                current_offset = consumer.position([tp])[0].offset
                lag = max(0, end_offsets[tp] - current_offset)

                # Only update per-partition metrics if we have reasonable cardinality
                if len(assignments) <= 100:
                    KAFKA_CONSUMER_LAG.labels(
                        topic=tp.topic, partition=str(tp.partition)
                    ).set(lag)

                total_lag += lag
            except Exception as e:
                logger.warning(f"Error calculating lag for partition {tp}: {e}")
                continue

        KAFKA_TOTAL_LAG.set(int(total_lag))

        if total_lag > 1000:
            logger.warning(f"High consumer lag detected: {total_lag} messages")

    except Exception as e:
        logger.error(f"Error updating Kafka lag metrics: {e}")
