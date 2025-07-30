"""
Configuration module for Sentr Feature Loader.

Contains configuration settings loaded from environment variables.
"""

import logging
import os

import structlog

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger()

# Configuration dictionary
config = {
    "kafka": {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        "group_id": os.getenv("KAFKA_GROUP_ID", "sentr-feature-loader"),
        "auto_offset_reset": "earliest",
        "topic": os.getenv("KAFKA_TOPIC", "tx_enriched"),
        "batch_size": int(os.getenv("KAFKA_BATCH_SIZE", "100")),
        "batch_timeout_ms": int(os.getenv("KAFKA_BATCH_TIMEOUT_MS", "1000")),
    },
    "redis": {
        # In Docker Compose environment, use 'redis' as the host name
        # In development environments, use 'localhost'
        "host": os.getenv("REDIS_HOST", "redis"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "password": os.getenv("REDIS_PASSWORD", None),
        "db": int(os.getenv("REDIS_DB", "0")),
        "feature_ttl": int(os.getenv("REDIS_FEATURE_TTL", "3600")),  # 1 hour
        "socket_timeout": 5.0,
        "socket_connect_timeout": 5.0,
        "health_check_interval": 30,
        "max_retries": 5,
        "retry_delay": 1.0,
        "max_retry_delay": 30.0,
        # Performance optimization: connection pooling
        "pool_size": int(os.getenv("REDIS_POOL_SIZE", "32")),  # Connection pool size
        "decode_responses": True,
        "circuit_breaker": {
            "failure_threshold": int(os.getenv("REDIS_CIRCUIT_FAILURE_THRESHOLD", "5")),
            "recovery_timeout": int(os.getenv("REDIS_CIRCUIT_RECOVERY_TIMEOUT", "30")),
            "half_open_timeout": int(os.getenv("REDIS_CIRCUIT_HALF_OPEN_TIMEOUT", "5")),
        },
        "memory_alert_threshold": float(
            os.getenv("REDIS_MEMORY_ALERT_THRESHOLD", "0.8")
        ),  # 80% of max memory
        "memory_limit_bytes": int(os.getenv("REDIS_MEMORY_LIMIT_BYTES", "0"))
        or 100 * 1024 * 1024,  # Default 100MB if not set
        "eviction_alert_threshold": int(
            os.getenv("REDIS_EVICTION_ALERT_THRESHOLD", "100")
        ),  # Alert if more than 100 keys evicted
    },
    "features": {
        # Short-term window configuration (default: 60 seconds)
        "window_size": int(os.getenv("WINDOW_SIZE", "60")),  # seconds
        "window_max_size": int(
            os.getenv("WINDOW_MAX_SIZE", "1000")
        ),  # max items per window
    },
    "monitoring": {
        "port": int(os.getenv("HEALTH_CHECK_PORT", "8082")),
    },
    "processing": {
        "feature_update_interval": float(
            os.getenv("FEATURE_UPDATE_INTERVAL_MS", "1000")
        )
        / 1000,  # convert to seconds
        "window_cleanup_frequency": int(
            os.getenv("WINDOW_CLEANUP_FREQUENCY", "1000")
        ),  # transactions
    },
}

# Global state
running = True
service_status = {"status": "initializing"}

# Metrics for monitoring
metrics = {
    "start_time": 0,  # Will be set when service starts
    "last_stats_time": 0,
    "last_window_cleanup": 0,
    "last_memory_check": 0,
    "processed": 0,
    "errors": 0,
}


def init_metrics():
    """Initialize the metrics timestamps"""
    current_time = time.time()
    metrics["start_time"] = current_time
    metrics["last_stats_time"] = current_time
    metrics["last_window_cleanup"] = current_time
    metrics["last_memory_check"] = current_time


# Make sure we have time imported for the init_metrics function
import time

# Redis connection pool settings for better performance
REDIS_CONNECTION_POOL_SETTINGS = {
    "max_connections": int(os.environ.get("REDIS_MAX_CONNECTIONS", "50")),
    "retry_on_timeout": True,
    "socket_keepalive": True,
    "socket_keepalive_options": {},
    "health_check_interval": 30,
    "connection_pool_class_kwargs": {
        "max_connections": int(os.environ.get("REDIS_MAX_CONNECTIONS", "50")),
        "retry_on_timeout": True,
    },
}
