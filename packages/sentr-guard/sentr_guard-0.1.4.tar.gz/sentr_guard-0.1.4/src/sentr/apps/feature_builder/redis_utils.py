"""
Redis utilities module for Sentr Feature Loader.

Contains functions for Redis connection management and operations.
"""

import random
import time

import redis

from apps.feature_builder.circuit_breaker import RedisCircuitBreaker
from apps.feature_builder.config import config, logger
from apps.feature_builder.metrics import (
    EVICTION_ALERT_TRIGGERED,
    FEATURE_COUNT,
    MEMORY_ALERT_TRIGGERED,
    REDIS_ERRORS,
    REDIS_EVICTED_KEYS,
    REDIS_MEMORY_LIMIT,
    REDIS_MEMORY_USAGE,
)


def exponential_backoff_with_jitter(retry_number, base_delay=1.0, max_delay=60.0):
    """
    Calculate delay with exponential backoff and jitter for more resilient error handling
    """
    delay = min(max_delay, base_delay * (2**retry_number))
    jitter = random.uniform(0, 0.1 * delay)  # 10% jitter
    return delay + jitter


def connect_to_redis():
    """
    Connect to Redis with retry logic
    """
    redis_config = config["redis"]

    # Configure Redis client
    redis_client = redis.Redis(
        host=redis_config["host"],
        port=redis_config["port"],
        password=redis_config["password"],
        db=redis_config["db"],
        socket_timeout=redis_config["socket_timeout"],
        socket_connect_timeout=redis_config["socket_connect_timeout"],
        health_check_interval=redis_config["health_check_interval"],
        retry_on_timeout=True,
        decode_responses=True,
    )

    # Configure circuit breaker
    circuit_config = redis_config["circuit_breaker"]
    circuit_breaker = RedisCircuitBreaker(
        failure_threshold=circuit_config["failure_threshold"],
        recovery_timeout=circuit_config["recovery_timeout"],
        half_open_timeout=circuit_config["half_open_timeout"],
        max_timeout=60,  # Maximum 1 minute timeout
        excluded_exceptions=[
            (ConnectionError, TimeoutError)
        ],  # Common network errors to exclude
        circuit_name="redis_feature_store",  # Specific circuit name for logging
    )

    # Attach circuit breaker to Redis client for health monitoring
    redis_client.circuit_breaker = circuit_breaker
    redis_client.circuit_breaker_status = circuit_breaker.get_state_code()

    # Test connection with ping
    try:
        if not redis_client.ping():
            raise redis.RedisError("Redis ping failed")

        # Set initial memory metrics
        info = redis_client.info()
        memory_usage = info.get("used_memory", 0)
        memory_limit = redis_config["memory_limit_bytes"]
        evicted_keys = info.get("evicted_keys", 0)

        REDIS_MEMORY_USAGE.set(memory_usage)
        REDIS_MEMORY_LIMIT.set(memory_limit)
        REDIS_EVICTED_KEYS.inc(evicted_keys)

        # Set alert states
        memory_usage_pct = memory_usage / memory_limit if memory_limit > 0 else 0
        memory_alert = memory_usage_pct > redis_config["memory_alert_threshold"]
        MEMORY_ALERT_TRIGGERED.set(1 if memory_alert else 0)

        eviction_alert = evicted_keys > redis_config["eviction_alert_threshold"]
        EVICTION_ALERT_TRIGGERED.set(1 if eviction_alert else 0)

        logger.info(
            "Connected to Redis",
            host=redis_config["host"],
            port=redis_config["port"],
            memory_usage=f"{memory_usage} bytes",
            memory_limit=f"{memory_limit} bytes",
            memory_usage_pct=f"{memory_usage_pct:.2%}",
            evicted_keys=evicted_keys,
        )

        return redis_client

    except redis.RedisError as e:
        logger.error("Failed to connect to Redis", error=str(e))
        REDIS_ERRORS.inc()
        raise


def update_features_in_redis(redis_client, current_features, config):
    """
    Update features in Redis based on the current feature calculation using optimized pipeline.

    This implementation uses the optimized RedisPipeline which provides:
    1. Field batching (HMSET instead of multiple HSET calls)
    2. TTL deduplication (avoiding redundant EXPIRE calls)
    3. Automatic flushing based on size and time thresholds

    Args:
        redis_client: Redis client connection
        current_features: Dictionary of feature values to update
        config: System configuration

    Returns:
        bool: Whether the update was successful
    """
    from apps.feature_builder.redis_sink.pipeline import RedisPipeline

    try:
        # Get Redis configuration
        redis_config = config["redis"]
        feature_counts = {}

        # Create optimized pipeline with appropriate settings
        pipeline = RedisPipeline(
            redis_client=redis_client,
            pipeline_size=redis_config.get("pipeline_size", 100),
            flush_ms=redis_config.get("pipeline_flush_ms", 100),
            feature_ttl=redis_config.get("feature_ttl", 3600),
        )

        # Process all cards and features
        for card_id, features in current_features.items():
            for feature_name, value in features.items():
                # Update feature counts for metrics
                feature_counts[feature_name] = feature_counts.get(feature_name, 0) + 1

                # Add feature to pipeline - prefix is handled by add_feature method
                pipeline.add_feature(card_id, feature_name, str(value))

        # Force flush to ensure all data is written
        success = pipeline.flush_if_needed(force=True)

        # Update metrics for each feature type
        for feature_name, count in feature_counts.items():
            FEATURE_COUNT.labels(feature_type=feature_name).set(count)

        return success

    except Exception as e:
        logger.error("Error updating features in Redis", error=str(e))
        REDIS_ERRORS.inc()
        return False


def clean_expired_windows(redis_client, windows, config):
    """
    Clean expired windows from Redis

    Args:
        redis_client: Redis client connection
        windows: Dictionary of windows to clean
        config: System configuration

    Returns:
        tuple: (number of expired keys, updated windows)
    """
    try:
        expired_keys = 0
        current_time = time.time()
        feature_counts = {}

        # Get all card IDs from Redis for which we have windows
        all_card_ids = set()
        for window_type, window_map in windows.items():
            all_card_ids.update(window_map.keys())

        # Check each card and clean expired windows
        for card_id in all_card_ids:
            card_key = f"card:{card_id}"

            # Check if key exists in Redis
            if not redis_client.exists(card_key):
                # Card is expired in Redis, clean up windows
                for window_type, window_map in windows.items():
                    if card_id in window_map:
                        del window_map[card_id]
                        expired_keys += 1

        # Count remaining features for metrics
        for window_type, window_map in windows.items():
            feature_counts[window_type] = len(window_map)

        # Update metrics
        for feature_name, count in feature_counts.items():
            FEATURE_COUNT.labels(feature_type=feature_name).set(count)

        return expired_keys, windows

    except Exception as e:
        logger.error("Error cleaning expired windows", error=str(e))
        REDIS_ERRORS.inc()
        return 0, windows
