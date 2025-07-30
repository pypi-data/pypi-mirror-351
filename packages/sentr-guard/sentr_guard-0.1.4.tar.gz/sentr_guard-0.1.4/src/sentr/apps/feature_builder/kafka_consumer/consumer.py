"""
Kafka consumer implementation with exactly-once semantics.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import prometheus_client as prom
from confluent_kafka import Consumer, KafkaError, KafkaException
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Configure module logger
logger = logging.getLogger(__name__)

# Default configuration from environment variables
DEFAULT_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
DEFAULT_GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "feature-loader")
DEFAULT_AUTO_OFFSET_RESET = os.environ.get("KAFKA_AUTO_OFFSET_RESET", "earliest")
DEFAULT_BATCH_SIZE = int(os.environ.get("KAFKA_BATCH_SIZE", "100"))
DEFAULT_BATCH_TIMEOUT_MS = int(os.environ.get("KAFKA_BATCH_TIMEOUT_MS", "100"))
DEFAULT_RETRY_ATTEMPTS = int(os.environ.get("KAFKA_RETRY_ATTEMPTS", "5"))
DEFAULT_STATS_INTERVAL_MS = int(os.environ.get("KAFKA_STATS_INTERVAL_MS", "30000"))

# Prometheus metrics
KAFKA_MESSAGES_CONSUMED = prom.Counter(
    "kafka_messages_consumed_total",
    "Total number of messages consumed from Kafka",
    ["topic"],
)

KAFKA_MESSAGES_FAILED = prom.Counter(
    "kafka_messages_failed_total",
    "Total number of messages that failed to process",
    ["topic", "error_type"],
)

KAFKA_BATCH_SIZE = prom.Histogram(
    "kafka_batch_size",
    "Size of batches processed from Kafka",
    buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000),
)

KAFKA_BATCH_DURATION = prom.Histogram(
    "kafka_batch_processing_duration_seconds",
    "Time taken to process a batch of Kafka messages",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

# Per-partition lag
KAFKA_PARTITION_LAG = prom.Gauge(
    "kafka_partition_lag",
    "Lag in messages for Kafka consumer per partition",
    ["topic", "partition"],
)

# Total lag per topic as required by PR #46
KAFKA_CONSUMER_LAG = prom.Gauge(
    "kafka_consumer_lag",
    "Total lag in messages for Kafka consumer per topic",
    ["topic"],
)


@dataclass
class KafkaConsumerConfig:
    """Configuration for a Kafka consumer."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "feature-loader",
        auto_offset_reset: str = "earliest",
        topic: str = "tx_enriched",
        batch_size: int = int(os.getenv("KAFKA_BATCH_SIZE", "100")),
        batch_timeout_ms: int = int(os.getenv("KAFKA_BATCH_TIMEOUT_MS", "1000")),
        fetch_min_bytes: int = int(os.getenv("KAFKA_FETCH_MIN_BYTES", "1")),
        fetch_wait_max_ms: int = int(os.getenv("KAFKA_FETCH_WAIT_MAX_MS", "500")),
        max_poll_interval_ms: int = int(
            os.getenv("KAFKA_MAX_POLL_INTERVAL_MS", "300000")
        ),
        retry_attempts: int = int(os.getenv("KAFKA_RETRY_ATTEMPTS", "5")),
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.topic = topic
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self.fetch_min_bytes = fetch_min_bytes
        self.fetch_wait_max_ms = fetch_wait_max_ms
        self.max_poll_interval_ms = max_poll_interval_ms
        self.retry_attempts = retry_attempts

    def to_consumer_config(self) -> Dict[str, Any]:
        """Convert to a consumer configuration dict for librdkafka."""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": self.group_id,
            "auto.offset.reset": self.auto_offset_reset,
            "enable.auto.commit": False,  # We'll commit offsets manually
            "fetch.min.bytes": self.fetch_min_bytes,
            "fetch.wait.max.ms": self.fetch_wait_max_ms,
            "max.poll.interval.ms": self.max_poll_interval_ms,
        }


class FeatureConsumer:
    """
    Kafka consumer with exactly-once semantics for feature processing.

    Features:
    - Batched message consumption for efficiency
    - Exactly-once processing with manual commits
    - Error handling with exponential backoff
    - Metrics for monitoring consumer lag and processing performance
    """

    def __init__(
        self,
        config: KafkaConsumerConfig,
        processor: Callable[[List[Dict[str, Any]]], bool],
    ):
        """
        Initialize the feature consumer.

        Args:
            config: Kafka consumer configuration
            processor: Function to process batches of messages, returns True if successful
        """
        self.config = config
        self.processor = processor
        self.consumer = None
        self.running = False
        self.poll_timeout = 0.1  # seconds

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type((KafkaException, ConnectionError)),
    )
    def connect(self) -> None:
        """
        Connect to Kafka with retry logic.

        Raises:
            KafkaException: If connection fails after retries
        """
        try:
            logger.info(f"Connecting to Kafka: {self.config.bootstrap_servers}")
            self.consumer = Consumer(self.config.to_consumer_config())
            self.consumer.subscribe([self.config.topic])
            logger.info(f"Subscribed to topic: {self.config.topic}")
        except (KafkaException, ConnectionError) as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            raise  # Will be retried by decorator

    def _parse_message(self, msg: Any) -> Optional[Dict[str, Any]]:
        """
        Parse a Kafka message into a dictionary.

        Args:
            msg: Kafka message object

        Returns:
            Parsed message as dict, or None if parsing failed
        """
        try:
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition, not an error
                    logger.debug("Reached end of partition")
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    KAFKA_MESSAGES_FAILED.labels(
                        topic=self.config.topic, error_type=str(msg.error().code())
                    ).inc()
                return None

            # Parse message value
            value_str = msg.value().decode("utf-8")
            data = json.loads(value_str)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {str(e)}")
            KAFKA_MESSAGES_FAILED.labels(
                topic=self.config.topic, error_type="JSONDecodeError"
            ).inc()
            return None

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            KAFKA_MESSAGES_FAILED.labels(
                topic=self.config.topic, error_type=type(e).__name__
            ).inc()
            return None

    def _update_lag_metrics(self) -> None:
        """Update consumer lag metrics from Kafka metadata."""
        if not self.consumer:
            return

        try:
            metrics = self.consumer.metrics()

            # Extract consumer lag from metrics if available
            if "consumer" in metrics:
                # Track total lag per topic for the required kafka_consumer_lag{topic} metric
                topic_lag = {}

                for topic, partitions in metrics["consumer"].items():
                    if isinstance(partitions, dict):
                        # Initialize topic total lag
                        if topic not in topic_lag:
                            topic_lag[topic] = 0

                        for partition, details in partitions.items():
                            if isinstance(details, dict) and "lag" in details:
                                lag = details["lag"]

                                # Update per-partition lag metric
                                KAFKA_PARTITION_LAG.labels(
                                    topic=topic, partition=partition
                                ).set(lag)

                                # Add to total for this topic
                                topic_lag[topic] += lag

                # Set total lag per topic metrics
                for topic, total_lag in topic_lag.items():
                    KAFKA_CONSUMER_LAG.labels(topic=topic).set(total_lag)
                    logger.debug(
                        f"Consumer lag for topic {topic}: {total_lag} messages"
                    )
        except Exception as e:
            logger.warning(f"Failed to update lag metrics: {str(e)}")

    def consume_batch(self) -> bool:
        """
        Consume a batch of messages from Kafka.

        Returns:
            True if messages were consumed and processed successfully
        """
        if not self.consumer:
            logger.error("Cannot consume: Consumer not connected")
            return False

        batch = []
        raw_messages = []
        batch_start_time = time.monotonic()

        # Collect a batch of messages
        while (
            len(batch) < self.config.batch_size
            and (time.monotonic() - batch_start_time) * 1000
            < self.config.batch_timeout_ms
        ):

            msg = self.consumer.poll(self.poll_timeout)
            if not msg:
                continue

            parsed = self._parse_message(msg)
            if parsed:
                batch.append(parsed)
                raw_messages.append(msg)
                KAFKA_MESSAGES_CONSUMED.labels(topic=self.config.topic).inc()

        # Process the collected batch
        if batch:
            KAFKA_BATCH_SIZE.observe(len(batch))

            start_time = time.monotonic()
            success = False

            try:
                # Process the batch (without committing yet)
                success = self.processor(batch)

                if success:
                    # Commit offsets only if processing succeeded
                    self.consumer.commit()
                    logger.debug(
                        f"Successfully processed batch of {len(batch)} messages"
                    )
                else:
                    logger.warning(f"Failed to process batch of {len(batch)} messages")
            except Exception as e:
                logger.error(f"Error in batch processing: {str(e)}")
                success = False

            # Record batch processing duration
            duration = time.monotonic() - start_time
            KAFKA_BATCH_DURATION.observe(duration)

            return success

        return True  # No messages to process is not a failure

    def run(self) -> None:
        """Run the consumer loop until stopped."""
        if not self.consumer:
            self.connect()

        self.running = True

        try:
            last_metrics_update = time.monotonic()

            while self.running:
                self.consume_batch()

                # Update metrics periodically
                now = time.monotonic()
                if now - last_metrics_update > 5:  # Every 5 seconds
                    self._update_lag_metrics()
                    last_metrics_update = now

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the consumer and clean up resources."""
        self.running = False

        if self.consumer:
            try:
                self.consumer.close()
                logger.info("Kafka consumer closed")
            except Exception as e:
                logger.error(f"Error closing consumer: {str(e)}")

            self.consumer = None
