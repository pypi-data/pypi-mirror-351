#!/usr/bin/env python3
"""
Feature Loader Service for Sentr

Consumes transaction events from Kafka, calculates real-time features,
and stores them in Redis for fraud detection lookups.

Instrumented with Prometheus metrics for monitoring and SLOs.
"""

import logging
import os
import sys
import time
from collections import deque

# Add project root to Python path if running standalone
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from confluent_kafka import Consumer, KafkaError
from prometheus_client import start_http_server

# Local imports
from apps.feature_builder.metrics import (
    BATCH_PROCESSING_LATENCY,
    FEATURE_COUNT,
    KAFKA_CONSUMER_LAG,
    KAFKA_TOTAL_LAG,
    REDIS_MEMORY_USAGE,
    SERVICE_LAST_SUCCESS,
    TX_FAILED,
    TX_PROCESSED,
)
from apps.feature_builder.redis_sink.pipeline import RedisPipeline
from infra.json_io import intern_features_dict
from infra.json_io import loads as json_loads

# Performance optimizations
from infra.redis_pool import create_redis_client_with_retry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("feature_loader")

# Configuration
config = {
    "kafka": {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        "group_id": os.getenv("KAFKA_GROUP_ID", "feature-loader"),
        "topic": os.getenv("KAFKA_TOPIC", "transactions"),
        "auto_commit_interval_ms": 5000,
        "session_timeout_ms": 30000,
        "max_poll_interval_ms": 300000,
        "max_poll_records": 500,
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
        "password": os.getenv("REDIS_PASSWORD", None),
        "key_prefix": "card:",
        "feature_ttl": 3600,  # 1 hour
    },
    "windows": {
        "size": int(os.getenv("WINDOW_SIZE", "60")),  # 60 seconds
        "max_size": int(os.getenv("WINDOW_MAX_SIZE", "10000")),  # Max elements
    },
    "metrics": {
        "port": int(os.getenv("METRICS_PORT", "8000")),
    },
    "service": {
        "lag_check_interval": 10,  # seconds between lag metric updates
        "stats_interval": 30,  # seconds between logging stats
        "feature_update_interval": 5,  # seconds between feature updates
    },
}


class TransactionWindow:
    """Memory-efficient sliding window for transaction data"""

    def __init__(self, window_size=60, max_size=10000):
        self.window_size = window_size
        self.max_size = max_size
        self.elements = deque()
        self._last_cleanup = time.time()

    @property
    def size(self):
        """Return the current number of elements in the window"""
        return len(self.elements)

    def add(self, item):
        """Add a new item to the window"""
        now = time.time()
        self.elements.append((now, item))

        # Enforce max size to prevent memory leaks
        if len(self.elements) > self.max_size:
            self.elements.popleft()

        # Periodic cleanup to remove expired items
        if now - self._last_cleanup > 10:  # Cleanup every 10 seconds
            self._clean_expired(now)
            self._last_cleanup = now

    def _clean_expired(self, current_time):
        """Remove expired elements efficiently"""
        cutoff = current_time - self.window_size

        # Optimization: if all elements are expired, clear all
        if self.elements and self.elements[-1][0] < cutoff:
            self.elements.clear()
            return

        # Remove expired elements from the front
        while self.elements and self.elements[0][0] < cutoff:
            self.elements.popleft()

    def count(self):
        """Count all elements in the window"""
        now = time.time()
        self._clean_expired(now)
        return len(self.elements)


class UniqueIPWindow(TransactionWindow):
    """Window that tracks unique IP addresses"""

    def count_unique(self):
        """Count unique IP addresses in the window"""
        now = time.time()
        self._clean_expired(now)
        unique_ips = set(item for _, item in self.elements)
        return len(unique_ips)


class FeatureLoaderService:
    """Main service that consumes transactions and updates features"""

    def __init__(self):
        self.config = config
        self.running = False
        self.windows = {
            "fail_60s": {},  # Card ID -> TransactionWindow for failed transactions
            "uniq_ip_60s": {},  # Card ID -> UniqueIPWindow for unique IPs
        }

        # Connect to Redis and create pipeline
        self.redis_client = self._connect_redis()
        self.redis_pipeline = RedisPipeline(
            redis_client=self.redis_client,
            pipeline_size=int(os.getenv("REDIS_PIPELINE_SIZE", "500")),
            flush_ms=int(os.getenv("REDIS_PIPELINE_FLUSH_MS", "100")),
            feature_ttl=int(os.getenv("FEATURE_TTL", "3600")),
        )

        # Set up Kafka consumer
        self.consumer = self._create_consumer()

        # Start metrics server
        metrics_port = self.config["metrics"]["port"]
        logger.info(f"Starting metrics server on port {metrics_port}")
        start_http_server(metrics_port)

        # Start health check server with component references
        from apps.feature_builder.health import start_health_check_server

        self.health_server = start_health_check_server(
            redis_client=self.redis_client,
            redis_pipeline=self.redis_pipeline,
            kafka_consumer=self.consumer,
        )

    def _connect_redis(self):
        """Connect to Redis server with connection pooling and retry logic"""
        redis_config = self.config["redis"]
        logger.info(
            f"Connecting to Redis at {redis_config['host']}:{redis_config['port']} with connection pooling"
        )

        # Use the optimized connection pooling utility
        return create_redis_client_with_retry(self.config)

    def _create_consumer(self):
        """Create Kafka consumer with proper configuration"""
        kafka_config = self.config["kafka"]
        logger.info(f"Creating Kafka consumer for {kafka_config['topic']}")

        consumer_config = {
            "bootstrap.servers": kafka_config["bootstrap_servers"],
            "group.id": kafka_config["group_id"],
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
            "auto.commit.interval.ms": kafka_config["auto_commit_interval_ms"],
            "session.timeout.ms": kafka_config["session_timeout_ms"],
            "max.poll.interval.ms": kafka_config["max_poll_interval_ms"],
        }

        consumer = Consumer(consumer_config)
        consumer.subscribe([kafka_config["topic"]])
        return consumer

    def process_transaction(self, transaction):
        """Process a single transaction and update windows"""
        try:
            card_id = transaction.get("card_id")
            ip_address = transaction.get("ip_address")
            is_success = transaction.get("is_success", True)

            if not card_id:
                logger.warning("Transaction missing card_id, skipping")
                return False

            # Initialize windows for this card if needed
            if card_id not in self.windows["fail_60s"]:
                self.windows["fail_60s"][card_id] = TransactionWindow(
                    window_size=self.config["windows"]["size"],
                    max_size=self.config["windows"]["max_size"],
                )

            if card_id not in self.windows["uniq_ip_60s"]:
                self.windows["uniq_ip_60s"][card_id] = UniqueIPWindow(
                    window_size=self.config["windows"]["size"],
                    max_size=self.config["windows"]["max_size"],
                )

            # Update windows based on transaction
            if not is_success:
                self.windows["fail_60s"][card_id].add(1)  # Add a failure

            if ip_address:
                self.windows["uniq_ip_60s"][card_id].add(ip_address)

            # Update metrics
            TX_PROCESSED.inc()
            return True

        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            TX_FAILED.inc()
            return False

    def calculate_features(self):
        """Calculate features from the current window state"""
        features = {}

        for card_id, fail_window in self.windows["fail_60s"].items():
            if card_id not in features:
                features[card_id] = {}
            features[card_id]["fail_60s"] = fail_window.count()

        for card_id, ip_window in self.windows["uniq_ip_60s"].items():
            if card_id not in features:
                features[card_id] = {}
            features[card_id]["uniq_ip_60s"] = ip_window.count_unique()

        return features

    def update_features_in_redis(self, features):
        """Store calculated features in Redis using optimized pipeline"""
        # Apply string interning to feature names for memory efficiency
        interned_features = {}
        for card_id, card_features in features.items():
            interned_features[card_id] = intern_features_dict(card_features)

        for card_id, card_features in interned_features.items():
            for feature_name, value in card_features.items():
                self.redis_pipeline.add_feature(card_id, feature_name, str(value))
                FEATURE_COUNT.inc()

        # Flush the pipeline
        return self.redis_pipeline.flush_if_needed(force=True)

    def consume_batch(self):
        """Consume a batch of messages from Kafka"""
        start_time = time.monotonic()
        status = "ok"

        try:
            # Poll for messages
            messages = self.consumer.poll(
                timeout=1.0, max_records=self.config["kafka"]["max_poll_records"]
            )
            message_count = 0

            if not messages:
                return 0

            # Process all messages
            for msg in messages:
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        continue

                try:
                    value = msg.value()
                    if not value:
                        continue

                    # Use optimized JSON parsing
                    transaction = json_loads(value.decode("utf-8"))
                    self.process_transaction(transaction)
                    message_count += 1

                except Exception as json_error:
                    logger.error(f"Failed to parse transaction JSON: {json_error}")
                    TX_FAILED.inc()
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    TX_FAILED.inc()

            # Calculate and update features if we processed messages
            if message_count > 0:
                features = self.calculate_features()
                self.update_features_in_redis(features)

            # Update service last success timestamp
            SERVICE_LAST_SUCCESS.set(time.time())
            return message_count

        except Exception as e:
            logger.error(f"Error consuming batch: {e}")
            status = "error"
            return 0
        finally:
            # Update batch latency metric
            processing_time = time.monotonic() - start_time
            BATCH_PROCESSING_LATENCY.labels(result=status).observe(processing_time)

    def update_lag_metrics(self):
        """Update Kafka consumer lag metrics"""
        try:
            assignments = self.consumer.assignment()
            if not assignments:
                return

            end_offsets = self.consumer.end_offsets(assignments)
            total_lag = 0

            for tp in assignments:
                current_offset = self.consumer.position([tp])[0].offset
                lag = max(0, end_offsets[tp] - current_offset)

                if len(assignments) <= 100:  # Avoid high cardinality
                    KAFKA_CONSUMER_LAG.labels(
                        topic=tp.topic, partition=str(tp.partition)
                    ).set(lag)

                total_lag += lag

            KAFKA_TOTAL_LAG.set(int(total_lag))

            if total_lag > 1000:
                logger.warning(f"High consumer lag detected: {total_lag} messages")

        except Exception as e:
            logger.error(f"Error updating lag metrics: {e}")

    def run(self):
        """Main service loop"""
        self.running = True
        last_stats_time = time.time()

        logger.info("Feature loader service started")

        try:
            while self.running:
                message_count = self.consume_batch()
                now = time.time()

                # Periodic stats and metrics updates
                if now - last_stats_time > self.config["service"]["stats_interval"]:
                    self.update_lag_metrics()

                    # Update Redis memory usage
                    try:
                        info = self.redis_client.info("memory")
                        REDIS_MEMORY_USAGE.set(info.get("used_memory", 0))
                    except Exception as e:
                        logger.error(f"Failed to get Redis memory usage: {e}")

                    # Log current status
                    total_windows = sum(len(w) for w in self.windows.values())
                    logger.info(
                        f"Processing status - messages: {message_count}, windows: {total_windows}"
                    )
                    last_stats_time = now

                # Don't hog CPU if no messages
                if message_count == 0:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Interrupted, shutting down...")
        finally:
            self.stop()

    def stop(self):
        """Stop the service gracefully"""
        logger.info("Stopping feature loader service")
        self.running = False

        # Flush any remaining data
        if hasattr(self, "redis_pipeline"):
            self.redis_pipeline.flush_if_needed(force=True)

        # Close connections
        if hasattr(self, "consumer"):
            self.consumer.close()

        logger.info("Service stopped")


def main():
    """Main entry point"""
    service = FeatureLoaderService()
    service.run()


if __name__ == "__main__":
    main()
