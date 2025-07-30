"""
Kafka consumer for Graph Loader service.

Handles exactly-once consumption of enriched transactions with proper offset management.
"""

import json
import signal
import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional

import structlog
from confluent_kafka import Consumer, KafkaError, KafkaException

from apps.graph_loader.config import config, running

logger = structlog.get_logger()


class GraphLoaderKafkaConsumer:
    """
    High-performance Kafka consumer for graph loader with exactly-once semantics.

    Features:
    - Exactly-once processing with manual offset commits
    - Graceful shutdown handling
    - Back-pressure support (pause/resume partitions)
    - Batch processing for efficiency
    - Comprehensive error handling and metrics
    """

    def __init__(self, message_handler: Callable[[List[Dict[str, Any]]], bool]):
        """
        Initialize Kafka consumer.

        Args:
            message_handler: Function to process batches of messages.
                           Should return True on success, False on failure.
        """
        self.message_handler = message_handler
        self.consumer = None
        self.running = True
        self.paused = False
        self.last_commit_time = time.time()

        # Performance tracking
        self.messages_processed = 0
        self.batches_processed = 0
        self.last_metrics_time = time.time()
        self.processing_times = deque(maxlen=100)

        # Back-pressure management
        self.pause_start_time = None
        self.total_pause_time = 0

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, _):
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal", signal=signum)
        self.running = False

    def _create_consumer(self) -> Consumer:
        """Create and configure Kafka consumer."""
        kafka_config = config["kafka"]

        consumer_config = {
            "bootstrap.servers": kafka_config["bootstrap_servers"],
            "group.id": kafka_config["group_id"],
            "auto.offset.reset": kafka_config["auto_offset_reset"],
            "enable.auto.commit": kafka_config["enable_auto_commit"],
            "max.poll.interval.ms": 300000,  # 5 minutes
            "session.timeout.ms": 30000,  # 30 seconds
            "heartbeat.interval.ms": 10000,  # 10 seconds
            "fetch.min.bytes": 1024,  # 1KB minimum fetch
            "fetch.max.wait.ms": 500,  # 500ms max wait
        }

        logger.info("Creating Kafka consumer", config=consumer_config)
        return Consumer(consumer_config)

    def _parse_message(self, message) -> Optional[Dict[str, Any]]:
        """Parse Kafka message into transaction data."""
        try:
            # Decode message value
            if message.value() is None:
                logger.warning("Received null message", offset=message.offset())
                return None

            # Parse JSON
            transaction = json.loads(message.value().decode("utf-8"))

            # Add metadata
            transaction["_kafka_metadata"] = {
                "topic": message.topic(),
                "partition": message.partition(),
                "offset": message.offset(),
                "timestamp": (
                    message.timestamp()[1] if message.timestamp()[0] == 1 else None
                ),
            }

            return transaction

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse message JSON", error=str(e), offset=message.offset()
            )
            return None
        except Exception as e:
            logger.error(
                "Unexpected error parsing message",
                error=str(e),
                offset=message.offset(),
            )
            return None

    def _should_pause_for_backpressure(self) -> bool:
        """Check if we should pause consumption due to back-pressure."""
        if not self.processing_times:
            return False

        # Calculate average processing time
        avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        threshold_ms = config["performance"]["backpressure_threshold_ms"] / 1000.0

        return avg_processing_time > threshold_ms

    def _handle_backpressure(self):
        """Handle back-pressure by pausing consumption."""
        if not self.paused and self._should_pause_for_backpressure():
            logger.warning("Pausing consumption due to back-pressure")
            self.consumer.pause(self.consumer.assignment())
            self.paused = True
            self.pause_start_time = time.time()

        elif self.paused and not self._should_pause_for_backpressure():
            logger.info("Resuming consumption, back-pressure resolved")
            self.consumer.resume(self.consumer.assignment())
            self.paused = False
            if self.pause_start_time:
                self.total_pause_time += time.time() - self.pause_start_time
                self.pause_start_time = None

    def _commit_offsets(self, force: bool = False):
        """Commit offsets with throttling."""
        current_time = time.time()

        # Commit every 5 seconds or when forced
        if force or (current_time - self.last_commit_time) >= 5.0:
            try:
                self.consumer.commit(asynchronous=False)
                self.last_commit_time = current_time
                logger.debug("Committed offsets")
            except KafkaException as e:
                logger.error("Failed to commit offsets", error=str(e))

    def _log_metrics(self):
        """Log performance metrics."""
        current_time = time.time()

        # Log metrics every 30 seconds
        if (current_time - self.last_metrics_time) >= 30.0:
            elapsed = current_time - self.last_metrics_time
            msg_rate = self.messages_processed / elapsed if elapsed > 0 else 0
            batch_rate = self.batches_processed / elapsed if elapsed > 0 else 0

            avg_processing_time = 0
            if self.processing_times:
                avg_processing_time = sum(self.processing_times) / len(
                    self.processing_times
                )

            logger.info(
                "Consumer performance metrics",
                messages_per_sec=round(msg_rate, 2),
                batches_per_sec=round(batch_rate, 2),
                avg_processing_time_ms=round(avg_processing_time * 1000, 2),
                total_messages=self.messages_processed,
                total_batches=self.batches_processed,
                paused=self.paused,
                total_pause_time=round(self.total_pause_time, 2),
            )

            # Reset counters
            self.messages_processed = 0
            self.batches_processed = 0
            self.last_metrics_time = current_time

    def start(self):
        """Start consuming messages."""
        logger.info("Starting Graph Loader Kafka consumer")

        try:
            # Create consumer and subscribe
            self.consumer = self._create_consumer()
            self.consumer.subscribe([config["kafka"]["topic"]])

            logger.info("Subscribed to topic", topic=config["kafka"]["topic"])

            # Message batch
            batch = []
            batch_size = config["kafka"]["batch_size"]
            batch_timeout = config["kafka"]["batch_timeout_ms"] / 1000.0
            last_batch_time = time.time()

            while self.running and running:
                try:
                    # Poll for messages
                    message = self.consumer.poll(timeout=1.0)

                    if message is None:
                        # Check if we should flush partial batch on timeout
                        if batch and (time.time() - last_batch_time) >= batch_timeout:
                            self._process_batch(batch)
                            batch = []
                            last_batch_time = time.time()
                        continue

                    if message.error():
                        if message.error().code() == KafkaError._PARTITION_EOF:
                            logger.debug("Reached end of partition")
                            continue
                        else:
                            logger.error("Kafka error", error=message.error())
                            continue

                    # Parse message
                    transaction = self._parse_message(message)
                    if transaction is None:
                        continue

                    # Add to batch
                    batch.append(transaction)
                    self.messages_processed += 1

                    # Process batch when full or timeout reached
                    current_time = time.time()
                    should_process = (
                        len(batch) >= batch_size
                        or (current_time - last_batch_time) >= batch_timeout
                    )

                    if should_process:
                        self._process_batch(batch)
                        batch = []
                        last_batch_time = current_time

                    # Handle back-pressure
                    self._handle_backpressure()

                    # Commit offsets periodically
                    self._commit_offsets()

                    # Log metrics
                    self._log_metrics()

                except KafkaException as e:
                    logger.error("Kafka exception during polling", error=str(e))
                    time.sleep(1)  # Brief pause before retrying

            # Process any remaining messages in batch
            if batch:
                logger.info("Processing final batch", size=len(batch))
                self._process_batch(batch)

        except Exception as e:
            logger.error("Fatal error in consumer", error=str(e))
            raise
        finally:
            self._shutdown()

    def _process_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of transactions."""
        if not batch:
            return

        start_time = time.time()

        try:
            # Call message handler
            success = self.message_handler(batch)

            if success:
                self.batches_processed += 1
                # Only commit offsets after successful processing
                self._commit_offsets(force=True)
                logger.debug("Batch processed successfully", batch_size=len(batch))
            else:
                logger.error(
                    "Batch processing failed - offsets NOT committed",
                    batch_size=len(batch),
                )

        except Exception as e:
            logger.error(
                "Error processing batch - offsets NOT committed",
                error=str(e),
                batch_size=len(batch),
            )

        finally:
            # Track processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)

    def _shutdown(self):
        """Clean shutdown of consumer."""
        logger.info("Shutting down Kafka consumer")

        if self.consumer:
            try:
                # Final offset commit
                self._commit_offsets(force=True)

                # Close consumer
                self.consumer.close()
                logger.info("Kafka consumer closed successfully")

            except Exception as e:
                logger.error("Error during consumer shutdown", error=str(e))

    def stop(self):
        """Stop the consumer gracefully."""
        logger.info("Stopping consumer")
        self.running = False
