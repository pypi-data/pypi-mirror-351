"""
Redis pipeline implementation with enhanced error handling and automatic flushing.
"""

import logging
import os
import random
import threading
import time
from collections import deque
from typing import Any, Dict, List, Optional

import prometheus_client as prom
import redis
from confluent_kafka import Consumer
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Import safe metric creation helpers
from apps.feature_builder.metrics import safe_counter, safe_histogram

# Configure module logger
logger = logging.getLogger(__name__)

# Re-export Redis errors for convenience
RedisError = redis.RedisError


# Define a unified dummy metric class for when metrics can't be created
class DummyMetric:
    """A unified dummy metric class that implements all required metric interfaces"""

    def __init__(self, *args, **kwargs):
        pass

    def set(self, value):
        pass

    def inc(self, value=1):
        pass

    def dec(self, value=1):
        pass

    def observe(self, value):
        pass

    def labels(self, *args, **kwargs):
        return self


# Default configuration
DEFAULT_PIPELINE_SIZE = int(
    os.environ.get("REDIS_PIPELINE_SIZE", "500")
)  # 5x larger than before
DEFAULT_PIPELINE_FLUSH_MS = int(
    os.environ.get("REDIS_PIPELINE_FLUSH_MS", "100")
)  # Increased flush interval
DEFAULT_RETRY_ATTEMPTS = int(os.environ.get("REDIS_RETRY_ATTEMPTS", "5"))
DEFAULT_RETRY_DELAY_MIN_MS = int(os.environ.get("REDIS_RETRY_DELAY_MIN_MS", "100"))
DEFAULT_RETRY_DELAY_MAX_MS = int(os.environ.get("REDIS_RETRY_DELAY_MAX_MS", "5000"))
DEFAULT_FEATURE_TTL = int(os.environ.get("FEATURE_TTL", "3600"))  # 1 hour default

# Use direct Gauge creation to avoid registry conflicts
try:
    # Try to unregister if it exists to prevent conflicts
    try:
        prom.REGISTRY.unregister(
            prom.REGISTRY._names_to_collectors.get("redis_pipeline_size")
        )
    except:
        pass
    # Create a new Gauge
    PIPELINE_SIZE = prom.Gauge(
        "redis_pipeline_size", "Current number of operations in the Redis pipeline"
    )
except Exception as e:
    # Fallback: use the dummy metric
    logger.warning(f"Could not create pipeline size metric: {e}")
    PIPELINE_SIZE = DummyMetric()

# New metrics for A1: Tracking pipeline efficiency
PIPELINE_BUFFERED_TOTAL = safe_counter(
    "redis_pipeline_buffered_total",
    "Total number of individual field updates buffered",
    (),
)

PIPELINE_EXECUTE_TOTAL = safe_counter(
    "redis_pipeline_execute_total", "Total number of actual Redis commands executed", ()
)

PIPELINE_TTL_SKIPPED_TOTAL = safe_counter(
    "redis_pipeline_ttl_skipped_total",
    "Total number of TTL operations skipped due to deduplication",
    (),
)

# A4: Metrics for tracking card update deduplication
CARD_UPDATES_TOTAL = safe_counter(
    "redis_card_updates_total", "Total number of card update requests", ()
)

CARD_UPDATES_UNIQUE = safe_counter(
    "redis_card_updates_unique", "Number of unique card updates after deduplication", ()
)

# Apply same direct creation approach to avoid registry conflicts
try:
    # Try to unregister if it exists to prevent conflicts
    try:
        prom.REGISTRY.unregister(
            prom.REGISTRY._names_to_collectors.get("redis_pipeline_flush_sec")
        )
    except:
        pass

    # Create a new Gauge
    PIPELINE_FLUSH_SEC = prom.Gauge(
        "redis_pipeline_flush_sec", "Seconds since the last pipeline flush"
    )
except Exception as e:
    # Fallback: use the dummy metric
    logger.warning(f"Could not create pipeline flush sec metric: {e}")
    PIPELINE_FLUSH_SEC = DummyMetric()

PIPELINE_FLUSH_DURATION = safe_histogram(
    "redis_pipeline_flush_duration_seconds",
    "Time taken to flush the Redis pipeline",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    labels=(),
)

PIPELINE_OPS_TOTAL = safe_counter(
    "redis_pipeline_operations_total",
    "Total number of operations sent through the Redis pipeline",
    ["operation_type"],
)

REDIS_ERRORS_TOTAL = safe_counter(
    "redis_pipeline_errors_total",
    "Total number of Redis pipeline errors encountered",
    ("error_type",),
)

REDIS_RETRIES_TOTAL = safe_counter(
    "redis_retries_total", "Total number of Redis operation retries", ()
)

REDIS_DLQ_MESSAGES = safe_counter(
    "redis_dlq_messages_total",
    "Number of messages sent to dead letter queue due to Redis errors",
    (),
)


class RedisPipeline:
    """
    Enhanced Redis pipeline with automatic flushing and error handling.

    Features:
    - Field buffering with HMSET for reduced command count
    - Size-based and time-based automatic flushing
    - Error handling with exponential backoff retry
    - Dead letter queue for unrecoverable errors
    - Prometheus metrics for monitoring
    - Optimized EXPIRE handling to skip redundant TTL settings
    - Thread safety for concurrent access

    Example:
        pipe = RedisPipeline(redis_client, pipeline_size=500)
        pipe.add_feature("card-123", "fail_60s", "7")
        pipe.flush_if_needed(force=True)
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        kafka_consumer: Optional[Consumer] = None,
        kafka_dlq_topic: Optional[str] = None,
        pipeline_size: int = DEFAULT_PIPELINE_SIZE,
        flush_ms: int = DEFAULT_PIPELINE_FLUSH_MS,
        feature_ttl: int = DEFAULT_FEATURE_TTL,
    ):
        """
        Initialize the Redis pipeline handler.

        Args:
            redis_client: Redis client instance
            kafka_consumer: Optional Kafka consumer for exactly-once semantics
            kafka_dlq_topic: Optional Kafka topic for dead letter queue
            pipeline_size: Maximum number of operations before auto-flush
            flush_ms: Maximum time in milliseconds before auto-flush
            feature_ttl: TTL in seconds for Redis feature keys
        """
        self.redis = redis_client
        self.consumer = kafka_consumer
        self.dlq_topic = kafka_dlq_topic
        self.pipeline_size = pipeline_size
        self.flush_ms = flush_ms / 1000.0  # Convert ms to seconds for time comparisons
        self.feature_ttl = feature_ttl

        # Active pipeline
        self.pipeline = self.redis.pipeline(transaction=False)
        self._queued = 0  # Count of operations queued in the pipeline
        self.last_flush_time = time.monotonic()
        self.pending_messages = []  # Kafka messages that will be committed on flush

        # Field buffer for batching HMSET operations
        self._buff = {}
        self._buffered_fields = 0  # Count of fields in buffer (fixed issue #1)

        # Set of keys that already have TTLs set (A3: Skip redundant EXPIRE)
        self._ttl_keys = set()
        self._ttl_keys_max_size = 100000  # Maximum size before clearing

        # For A4: Track cards seen in current batch for deduplication
        self._batch_card_ids = set()
        self._total_card_updates = 0
        self._unique_card_updates = 0

        # A5: Add thread safety for potential future multithreaded use
        self._lock = threading.RLock()

        # Adaptive batch sizing for optimal performance
        self._adaptive_sizing = True
        self._recent_flush_times = deque(maxlen=10)  # Track recent flush performance
        self._optimal_pipeline_size = pipeline_size
        self._min_pipeline_size = max(50, pipeline_size // 4)
        self._max_pipeline_size = pipeline_size * 2

    def _handle_redis_error(self, exception: redis.RedisError) -> None:
        """
        Handle Redis errors with appropriate logging and metrics.

        Args:
            exception: The Redis exception that occurred
        """
        error_type = type(exception).__name__
        logger.error(f"Redis error: {error_type}", exc_info=exception)
        REDIS_ERRORS_TOTAL.labels(error_type=error_type).inc()

    def _send_to_dlq(self, message_batch: List[Dict[str, Any]]) -> None:
        """
        Send failed messages to dead letter queue.

        Args:
            message_batch: List of messages that failed to process
        """
        if not message_batch:
            return

        # Count messages sent to DLQ for monitoring
        batch_size = len(message_batch)
        REDIS_DLQ_MESSAGES.inc(batch_size)

        # Fix for Issue #5: Log message batch content for recovery
        import json

        try:
            # Log a truncated view of the failed messages to aid recovery
            truncated_json = json.dumps(message_batch)[:4096]  # Limit to 4KB
            logger.error(
                "Messages sent to DLQ", count=batch_size, payload_sample=truncated_json
            )

            # Send to Kafka DLQ topic if configured
            if self.dlq_topic and self.consumer:
                # TODO: Implement actual Kafka DLQ integration
                pass
        except Exception as e:
            logger.error(
                "Failed to process DLQ messages", error=str(e), count=batch_size
            )

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=DEFAULT_RETRY_DELAY_MIN_MS / 1000,
            max=DEFAULT_RETRY_DELAY_MAX_MS / 1000,
        ),
        retry=retry_if_exception_type(redis.RedisError),
        reraise=True,
    )
    def _execute_with_retry(self) -> List[Any]:
        """
        Execute pipeline with retry logic.

        Returns:
            List of results from pipeline execution

        Raises:
            redis.RedisError: If all retries fail
        """
        try:
            return self.pipeline.execute()
        except redis.RedisError as e:
            REDIS_RETRIES_TOTAL.inc()
            logger.warning(f"Redis operation failed, retrying: {str(e)}")
            raise  # Will be caught by retry decorator

    def add_feature(self, card_id: str, feature_name: str, value: str) -> None:
        """
        Add a feature to the pipeline for a card.

        Args:
            card_id: Card identifier
            feature_name: Name of the feature
            value: Feature value as string
        """
        # Use thread safety lock to prevent race conditions (A5)
        with self._lock:
            # Implement A4: Skip if we've already seen this card in the current batch
            CARD_UPDATES_TOTAL.inc()
            if card_id in self._batch_card_ids:
                return

            self._batch_card_ids.add(card_id)
            CARD_UPDATES_UNIQUE.inc()
            self._total_card_updates += 1
            self._unique_card_updates += 1

            redis_key = f"card:{card_id}"

            # Buffer the field instead of immediate HSET (optimized with setdefault)
            mapping = self._buff.setdefault(redis_key, {})
            mapping[feature_name] = value
            self._buffered_fields += 1  # Fixed Issue #1: Track buffered fields count

            # Increment operations counter for monitoring
            PIPELINE_OPS_TOTAL.labels("hset").inc()

            # Track buffered operations for pipeline efficiency monitoring (A1)
            PIPELINE_BUFFERED_TOTAL.inc()

            # Update pipeline size metric for live monitoring
            PIPELINE_SIZE.set(self._queued + self._buffered_fields)

            # Check for flush conditions periodically
            self.flush_if_needed()

    def add_message_to_batch(self, message: Any) -> None:
        """
        Add a Kafka message to the current batch for commit on successful flush.

        Args:
            message: Kafka message to commit after flush
        """
        if self.consumer:
            self.pending_messages.append(message)

    def _enqueue_hmset(self, key: str, mapping: Dict[str, str]) -> None:
        """
        Add a HMSET operation to the pipeline with proper batching.

        Args:
            key: Redis key
            mapping: Field-value mapping for the hash
        """
        # Use hset with mapping for modern redis-py compatibility (Fix for deprecation warning)
        self.pipeline.hset(key, mapping=mapping)

        # Check TTL set size and clear if needed to bound memory usage
        if len(self._ttl_keys) > self._ttl_keys_max_size:
            self._ttl_keys.clear()  # Prevent unbounded growth (Fix for Issue #3)

        # A3: Skip redundant EXPIRE commands if key already has TTL set
        if key not in self._ttl_keys:
            self.pipeline.expire(key, self.feature_ttl)
            self._ttl_keys.add(key)  # Mark this key as having a TTL
            self._queued += 2  # Count both HMSET and EXPIRE
            PIPELINE_EXECUTE_TOTAL.inc(2)  # Track both commands
        else:
            self._queued += 1  # Only count HMSET
            PIPELINE_EXECUTE_TOTAL.inc(1)  # Only track HMSET command
            PIPELINE_TTL_SKIPPED_TOTAL.inc()  # Count skipped TTL operations

        # Decrease the buffered fields counter since we've moved them to the pipeline
        self._buffered_fields -= len(mapping)  # Fix for Issue #1

    def flush_if_needed(self, force: bool = False) -> bool:
        """
        Check if pipeline should be flushed and do so if needed.

        Args:
            force: Force flush regardless of conditions

        Returns:
            True if flush was successful or not needed, False if flush failed
        """
        # Use thread safety lock to prevent race conditions (A5)
        with self._lock:
            now = time.monotonic()
            time_elapsed = now - self.last_flush_time

            # Update the time since last flush metric (in seconds)
            PIPELINE_FLUSH_SEC.set(time_elapsed)

            # Fix for issue #1: Consider buffered fields in flush condition
            should_flush = (
                force
                or (self._queued + self._buffered_fields) >= self.pipeline_size
                or time_elapsed >= self.flush_ms / 1000
            )  # Convert ms to seconds

            if should_flush:
                # Process buffered fields
                buffered_fields_count = 0
                for key, mapping in self._buff.items():
                    if mapping:  # Only process if there are fields
                        buffered_fields_count += len(mapping)
                        self._enqueue_hmset(key, mapping)

                # Note: _buff.clear() moved to after successful flush (fixes issue #4)
                # Only reset batch tracking here, buff clearing happens in flush() on success
                self._batch_card_ids.clear()

                # Flush if we have any operations queued
                if self._queued > 0:
                    return self.flush()
                return True  # Nothing to flush, consider it successful

            return True  # No flush needed, consider it successful

    def flush(self) -> bool:
        """
        Flush the pipeline and handle errors with proper recovery.

        Returns:
            True if flush was successful, False otherwise
        """
        with self._lock:
            if self._queued == 0:
                return True

            start_time = time.monotonic()
            success = False
            retry_count = 0
            max_retries = 3

            try:
                # Try to execute with retries
                while retry_count < max_retries:
                    try:
                        self._execute_with_retry()
                        success = True
                        break
                    except redis.RedisError as e:
                        retry_count += 1
                        self._handle_redis_error(e)

                        if retry_count < max_retries:
                            # Exponential backoff
                            wait_time = (2**retry_count) * 0.1  # 0.1, 0.2, 0.4 seconds
                            logger.warning(
                                f"Redis flush failed, retrying in {wait_time}s (attempt {retry_count}/{max_retries})"
                            )
                            time.sleep(wait_time)
                        else:
                            logger.error(
                                f"Redis flush failed after {max_retries} attempts, sending to DLQ"
                            )
                            # Send to DLQ if all retries failed
                            if self.pending_messages:
                                self._send_to_dlq(self.pending_messages)
                            break

                # Handle Kafka commits only on successful Redis flush
                if success and self.consumer and self.pending_messages:
                    try:
                        # Commit Kafka offsets synchronously to ensure exactly-once semantics
                        if hasattr(self.consumer, "commit"):
                            self.consumer.commit(asynchronous=False)
                    except Exception as e:
                        logger.error(f"Failed to commit Kafka offsets: {e}")
                        # Don't mark as failure since Redis succeeded

            except Exception as e:
                logger.error(f"Unexpected error during pipeline flush: {e}")
                success = False

            finally:
                # Always reset pipeline state
                self.pipeline = self.redis.pipeline(transaction=False)
                PIPELINE_SIZE.set(0)
                self._queued = 0
                self.last_flush_time = time.monotonic()

                if success:
                    # Only clear buffers and messages on successful flush
                    self._buff.clear()
                    self._buffered_fields = 0
                    self.pending_messages.clear()

                    # Periodically reset TTL tracking to handle key expirations
                    if (
                        len(self._ttl_keys) > self._ttl_keys_max_size
                        or random.random() < 0.1
                    ):
                        self._ttl_keys.clear()
                else:
                    # On failure, keep the buffered data for next flush attempt
                    logger.warning(
                        f"Pipeline flush failed, keeping {self._buffered_fields} buffered fields for retry"
                    )

                # Always measure flush duration
                flush_duration = time.monotonic() - start_time
                PIPELINE_FLUSH_DURATION.observe(flush_duration)

                # Adaptive batch sizing based on performance
                if success and self._adaptive_sizing:
                    self._recent_flush_times.append(flush_duration)
                    self._adjust_pipeline_size()

                return success

    def _adjust_pipeline_size(self) -> None:
        """
        Automatically adjust pipeline size based on recent performance.

        This method analyzes recent flush times and adjusts the pipeline size
        to optimize for throughput while maintaining low latency.
        """
        if len(self._recent_flush_times) < 5:
            return  # Need enough samples

        avg_flush_time = sum(self._recent_flush_times) / len(self._recent_flush_times)

        # Target flush time: 10ms for optimal balance of throughput and latency
        target_flush_time = 0.01

        if avg_flush_time > target_flush_time * 1.5:  # Too slow, reduce batch size
            new_size = max(self._min_pipeline_size, int(self.pipeline_size * 0.8))
            if new_size != self.pipeline_size:
                logger.debug(
                    f"Reducing pipeline size from {self.pipeline_size} to {new_size} (avg flush: {avg_flush_time:.3f}s)"
                )
                self.pipeline_size = new_size

        elif (
            avg_flush_time < target_flush_time * 0.5
        ):  # Too fast, can increase batch size
            new_size = min(self._max_pipeline_size, int(self.pipeline_size * 1.2))
            if new_size != self.pipeline_size:
                logger.debug(
                    f"Increasing pipeline size from {self.pipeline_size} to {new_size} (avg flush: {avg_flush_time:.3f}s)"
                )
                self.pipeline_size = new_size
