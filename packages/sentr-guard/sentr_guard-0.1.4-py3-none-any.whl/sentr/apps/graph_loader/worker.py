"""
Worker module for the Graph Loader service.
Consumes transaction events and loads them into the Neo4j graph database.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from confluent_kafka import Consumer, KafkaError, KafkaException
from prometheus_client import Counter, Gauge, Histogram

from apps.graph_loader.config import (
    BATCH_SIZE,
    BATCH_TIMEOUT_MS,
    CONSUMER_GROUP,
    EDGE_TYPES,
    KAFKA_BROKERS,
    TRANSACTION_TOPIC,
)
from apps.graph_loader.neo4j_client import LOADED_EDGES_TOTAL, Neo4jClient

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics
CONSUMER_LAG = Gauge(
    "kafka_consumer_lag_seconds",
    "Lag between current time and message timestamp in seconds",
    ["topic"],
)

PROCESSED_MESSAGES = Counter(
    "processed_messages_total",
    "Total number of messages processed",
    ["topic", "status"],
)

BATCH_PROCESSING_TIME = Histogram(
    "batch_processing_seconds", "Time to process a batch of messages", ["topic"]
)

BATCH_SIZE_METRIC = Histogram("batch_size", "Size of processed batches", ["topic"])


class GraphLoader:
    """Worker class that loads transaction data into Neo4j graph database."""

    def __init__(self, neo4j_client: Optional[Neo4jClient] = None):
        """Initialize the graph loader worker."""
        self.consumer = self._create_consumer()
        self.neo4j = neo4j_client or Neo4jClient()
        self.running = False

        # Set up the Neo4j indices on startup
        self.neo4j.create_indices()

        logger.info(f"Graph Loader initialized with edge types: {EDGE_TYPES}")

    def _create_consumer(self) -> Consumer:
        """Create and configure the Kafka consumer."""
        config = {
            "bootstrap.servers": KAFKA_BROKERS,
            "group.id": CONSUMER_GROUP,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "max.poll.interval.ms": 300000,  # 5 minutes
            "session.timeout.ms": 30000,  # 30 seconds
        }

        consumer = Consumer(config)
        consumer.subscribe([TRANSACTION_TOPIC])
        logger.info(f"Subscribed to topic: {TRANSACTION_TOPIC}")

        return consumer

    def process_transaction(self, transaction: Dict[str, Any]) -> None:
        """
        Process a single transaction and create edges in the graph.

        Args:
            transaction: Transaction data dictionary
        """
        try:
            # Extract key fields from transaction
            card_id = transaction.get("card_id")
            merchant_id = transaction.get("merchant_id")
            ip_address = transaction.get("ip_address")
            device_id = transaction.get("device_id")
            device_fingerprint = transaction.get("device_fingerprint")
            timestamp = transaction.get("timestamp", int(time.time()))

            # Validate required fields based on enabled edge types
            if "card_ip" in EDGE_TYPES and (not card_id or not ip_address):
                logger.warning(
                    f"Missing required fields for card_ip edge: card_id={card_id}, ip={ip_address}"
                )
                return

            # Create card-ip edge if enabled
            if "card_ip" in EDGE_TYPES and card_id and ip_address:
                query = """
                MERGE (c:Card {id: $card_id})
                MERGE (i:IP {addr: $ip_address})
                MERGE (c)-[r:USED_IP {ts: $timestamp}]->(i)
                RETURN r
                """
                self.neo4j.run(
                    query,
                    {
                        "card_id": card_id,
                        "ip_address": ip_address,
                        "timestamp": timestamp,
                    },
                    query_type="create_card_ip",
                )
                LOADED_EDGES_TOTAL.labels(edge_type="card_ip").inc()

            # Create card-merchant edge if enabled
            if "card_merchant" in EDGE_TYPES and card_id and merchant_id:
                query = """
                MERGE (c:Card {id: $card_id})
                MERGE (m:Merchant {id: $merchant_id})
                MERGE (c)-[r:USED_AT {ts: $timestamp}]->(m)
                RETURN r
                """
                self.neo4j.run(
                    query,
                    {
                        "card_id": card_id,
                        "merchant_id": merchant_id,
                        "timestamp": timestamp,
                    },
                    query_type="create_card_merchant",
                )
                LOADED_EDGES_TOTAL.labels(edge_type="card_merchant").inc()

            # Create card-device edge if enabled
            if (
                "card_device" in EDGE_TYPES
                and card_id
                and (device_id or device_fingerprint)
            ):
                device_props = {}
                if device_id:
                    device_props["id"] = device_id
                if device_fingerprint:
                    device_props["fp_hash"] = device_fingerprint

                if device_props:
                    query = """
                    MERGE (c:Card {id: $card_id})
                    MERGE (d:Device $device_props)
                    MERGE (c)-[r:USED_DEVICE {ts: $timestamp}]->(d)
                    RETURN r
                    """
                    self.neo4j.run(
                        query,
                        {
                            "card_id": card_id,
                            "device_props": device_props,
                            "timestamp": timestamp,
                        },
                        query_type="create_card_device",
                    )
                    LOADED_EDGES_TOTAL.labels(edge_type="card_device").inc()

        except Exception as e:
            logger.error(f"Error processing transaction: {e}", exc_info=True)

    def process_batch(self, messages: List[Dict[str, Any]]) -> None:
        """
        Process a batch of transaction messages.

        Args:
            messages: List of transaction dictionaries
        """
        start_time = time.time()
        batch_size = len(messages)

        try:
            for transaction in messages:
                self.process_transaction(transaction)

            # Record batch metrics
            processing_time = time.time() - start_time
            BATCH_PROCESSING_TIME.labels(topic=TRANSACTION_TOPIC).observe(
                processing_time
            )
            BATCH_SIZE_METRIC.labels(topic=TRANSACTION_TOPIC).observe(batch_size)

            if processing_time > 1.0:  # Log if batch takes more than 1 second
                logger.warning(
                    f"Slow batch processing: {batch_size} transactions in {processing_time:.2f}s"
                )

            logger.info(
                f"Processed batch of {batch_size} transactions in {processing_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Error processing batch: {e}", exc_info=True)
            PROCESSED_MESSAGES.labels(topic=TRANSACTION_TOPIC, status="error").inc(
                batch_size
            )
            return

        # Record success
        PROCESSED_MESSAGES.labels(topic=TRANSACTION_TOPIC, status="success").inc(
            batch_size
        )

    def consume_batch(self) -> bool:
        """
        Consume a batch of messages from Kafka, process them, and commit offsets.

        Returns:
            bool: True if processing was successful, False otherwise
        """
        batch = []
        batch_start_time = time.time()

        try:
            # Collect messages for the batch
            while (
                len(batch) < BATCH_SIZE
                and (time.time() - batch_start_time) * 1000 < BATCH_TIMEOUT_MS
            ):

                msg = self.consumer.poll(timeout=0.1)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(
                            f"Reached end of partition: {msg.topic()}/{msg.partition()}"
                        )
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                    continue

                try:
                    # Parse the message value
                    transaction = json.loads(msg.value().decode("utf-8"))

                    # Calculate and record consumer lag
                    msg_timestamp = transaction.get("timestamp")
                    if msg_timestamp:
                        lag = time.time() - msg_timestamp
                        CONSUMER_LAG.labels(topic=msg.topic()).set(lag)

                    # Add to batch
                    batch.append(transaction)

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value()}")
                    PROCESSED_MESSAGES.labels(topic=msg.topic(), status="error").inc()
                    continue

            # Process the collected batch
            if batch:
                self.process_batch(batch)
                # Commit offsets after successful processing
                self.consumer.commit()
                return True

            return True

        except KafkaException as e:
            logger.error(f"Kafka exception during batch consumption: {e}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error during batch consumption: {e}", exc_info=True
            )
            return False

    def run(self) -> None:
        """Run the graph loader worker."""
        self.running = True
        logger.info("Starting Graph Loader worker")

        try:
            while self.running:
                self.consume_batch()

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down")
        except Exception as e:
            logger.error(f"Error in Graph Loader worker: {e}", exc_info=True)
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Shutdown the graph loader worker."""
        self.running = False

        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

        if self.neo4j:
            self.neo4j.close()
            logger.info("Neo4j connection closed")

        logger.info("Graph Loader worker shutdown complete")
