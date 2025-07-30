"""
Universal Prometheus metrics registry for Sentr fraud detection system.

Provides singleton CollectorRegistry with optimized histogram buckets for 
P95 ≤ 300µs SLO monitoring and burn-rate alerts.
"""

import logging
from typing import Any, Dict

import prometheus_client as prom

logger = logging.getLogger(__name__)

# Singleton collector registry - both FastAPI app and CLI tools can use this
REGISTRY = prom.CollectorRegistry()

# Feature store latency histogram with narrow buckets for SLO burn-rate alerts
sentr_feature_latency_seconds = prom.Histogram(
    "sentr_feature_latency_seconds",
    "Time to compute features in seconds",
    buckets=(
        0.0001,
        0.00025,
        0.0005,
        0.001,
        0.005,
    ),  # 100µs to 5ms for P95 ≤ 300µs monitoring
    registry=REGISTRY,
)

# Redis operation metrics for circuit breaker monitoring
redis_connections = prom.Gauge(
    "redis_connections",
    "Number of Redis connections",
    ["pool", "state"],  # state: in_use, free
    registry=REGISTRY,
)

redis_operations = prom.Histogram(
    "redis_operations_duration_seconds",
    "Redis operation duration",
    ["command", "status"],  # status: success, error
    buckets=(0.00005, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005),  # 50µs to 5ms
    registry=REGISTRY,
)

# Circuit breaker metrics
circuit_breaker_state = prom.Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=half_open, 2=open)",
    ["service"],
    registry=REGISTRY,
)

circuit_breaker_failures = prom.Counter(
    "circuit_breaker_failures_total",
    "Number of circuit breaker failures",
    ["service"],
    registry=REGISTRY,
)

# Feature operation tracking
feature_operations = prom.Counter(
    "feature_operations_total",
    "Number of feature operations",
    ["operation", "status"],  # operation: get_features, store_features, etc.
    registry=REGISTRY,
)

feature_cache_hits = prom.Counter(
    "feature_cache_hits_total",
    "Number of feature cache hits vs misses",
    ["status"],  # status: hit, miss
    registry=REGISTRY,
)

# Sliding window metrics
window_size_current = prom.Gauge(
    "window_size_current",
    "Current number of items in sliding window",
    ["window_type", "entity_type"],
    registry=REGISTRY,
)

window_truncations_total = prom.Counter(
    "window_truncations_total",
    "Number of times a window was truncated due to max size",
    ["window_type"],
    registry=REGISTRY,
)

# JSON operation metrics (from json_io.py)
json_fallback_total = prom.Counter(
    "json_fallback_total",
    "Number of times stdlib JSON was used instead of orjson",
    ["operation", "reason"],
    registry=REGISTRY,
)

json_operation_duration = prom.Histogram(
    "json_operation_duration_seconds",
    "Time spent on JSON operations",
    ["operation", "engine"],
    buckets=(0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01),  # 10µs to 10ms
    registry=REGISTRY,
)

# Request processing metrics
request_duration = prom.Histogram(
    "request_duration_seconds",
    "Time spent processing requests",
    ["endpoint", "method", "status"],
    buckets=(
        0.0001,
        0.0002,
        0.0005,
        0.001,
        0.002,
        0.005,
        0.01,
        0.02,
        0.05,
        0.1,
    ),  # 100µs to 100ms
    registry=REGISTRY,
)

request_count = prom.Counter(
    "requests_total",
    "Total number of requests",
    ["endpoint", "method", "status"],
    registry=REGISTRY,
)

# Memory and resource tracking
memory_usage_bytes = prom.Gauge(
    "memory_usage_bytes",
    "Memory usage in bytes",
    ["type"],  # type: rss, vms, shared
    registry=REGISTRY,
)

garbage_collection_duration = prom.Histogram(
    "garbage_collection_duration_seconds",
    "Time spent in garbage collection",
    ["generation"],
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05),  # 100µs to 50ms
    registry=REGISTRY,
)

# Redis RTT monitoring for Lua scripts (targeting P95 ≤ 300µs)
redis_rtt_seconds = prom.Summary(
    "redis_rtt_seconds",
    "Redis round-trip time for atomic operations",
    ["script_name"],
    registry=REGISTRY,
)


def track_feature_operation(
    operation: str, duration: float, success: bool = True
) -> None:
    """
    Track feature store operations with timing and success metrics.

    Args:
        operation: Operation name (e.g., 'get_features', 'store_features')
        duration: Operation duration in seconds
        success: Whether the operation succeeded
    """
    status = "success" if success else "error"

    # Track operation count
    feature_operations.labels(operation=operation, status=status).inc()

    # Track latency
    sentr_feature_latency_seconds.observe(duration)


def track_cache_hit(hit: bool) -> None:
    """
    Track feature cache hit/miss ratio.

    Args:
        hit: Whether this was a cache hit
    """
    status = "hit" if hit else "miss"
    feature_cache_hits.labels(status=status).inc()


def track_circuit_breaker_state(service: str, state: str) -> None:
    """
    Track circuit breaker state changes.

    Args:
        service: Service name (e.g., 'redis')
        state: Circuit breaker state ('closed', 'half_open', 'open')
    """
    state_value = {"closed": 0, "half_open": 1, "open": 2}.get(state, 0)
    circuit_breaker_state.labels(service=service).set(state_value)

    if state == "open":
        circuit_breaker_failures.labels(service=service).inc()


def track_request(
    endpoint: str, method: str, duration: float, status_code: int
) -> None:
    """
    Track HTTP request metrics.

    Args:
        endpoint: Request endpoint
        method: HTTP method
        duration: Request duration in seconds
        status_code: HTTP status code
    """
    status = str(status_code)

    request_count.labels(endpoint=endpoint, method=method, status=status).inc()
    request_duration.labels(endpoint=endpoint, method=method, status=status).observe(
        duration
    )


def get_metrics_for_export() -> Dict[str, Any]:
    """
    Get current metrics values for export/logging.

    Returns:
        Dictionary with current metric values
    """
    from prometheus_client import generate_latest

    try:
        # Generate metrics in Prometheus format
        metrics_output = generate_latest(REGISTRY).decode("utf-8")

        # Parse key metrics for structured logging
        return {
            "registry_collectors": len(REGISTRY._collector_to_names),
            "metrics_available": True,
            "sample_metrics": _extract_sample_metrics(),
        }
    except Exception as e:
        logger.error(f"Error extracting metrics: {e}")
        return {"registry_collectors": 0, "metrics_available": False, "error": str(e)}


def _extract_sample_metrics() -> Dict[str, Any]:
    """Extract a few key metrics for monitoring."""
    try:
        samples = {}

        # Get some sample metric values
        for collector in REGISTRY._collector_to_names:
            metric_families = collector.collect()
            for family in metric_families:
                if family.name in [
                    "sentr_feature_latency_seconds",
                    "redis_connections",
                    "circuit_breaker_state",
                ]:
                    for sample in family.samples:
                        samples[f"{family.name}_{sample.name}"] = sample.value
                        if len(samples) >= 10:  # Limit sample size
                            break
                if len(samples) >= 10:
                    break

        return samples
    except Exception:
        return {}


def reset_metrics() -> None:
    """
    Reset all metrics (useful for testing).

    Warning: This clears all metric state!
    """
    global REGISTRY
    REGISTRY = prom.CollectorRegistry()
    logger.warning("All metrics have been reset")


def get_registry() -> prom.CollectorRegistry:
    """
    Get the singleton Prometheus collector registry.

    Returns:
        CollectorRegistry instance for use by FastAPI app and CLI tools
    """
    return REGISTRY


# Pre-register some initial metric values to ensure they appear in scrapes
def _initialize_metrics():
    """Initialize metrics with default values."""
    try:
        # Initialize circuit breaker state as closed
        circuit_breaker_state.labels(service="redis").set(0)

        # Initialize Redis connection gauges
        redis_connections.labels(pool="default", state="in_use").set(0)
        redis_connections.labels(pool="default", state="free").set(0)

        logger.debug("Metrics initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize metrics: {e}")


# Initialize metrics on import
_initialize_metrics()
