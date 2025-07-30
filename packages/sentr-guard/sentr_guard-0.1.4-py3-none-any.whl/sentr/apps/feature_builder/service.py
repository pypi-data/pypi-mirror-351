"""
Service orchestration module for Sentr Feature Loader.

Coordinates the main service components and handles service lifecycle.
"""

import gc
import signal
import threading
import time

from confluent_kafka import Consumer, KafkaException

from apps.feature_builder.config import (
    config,
    init_metrics,
    logger,
    metrics,
    running,
    service_status,
)
from apps.feature_builder.health import start_health_check_server
from apps.feature_builder.metrics import (
    KAFKA_ERRORS,
    KAFKA_MESSAGES,
    KAFKA_PROCESSING_TIME,
    TX_PROCESSED,
)
from apps.feature_builder.redis_utils import connect_to_redis


def connect_to_kafka():
    """
    Connect to Kafka and create a consumer
    """
    kafka_config = config["kafka"]

    # Configure Kafka consumer
    consumer_config = {
        "bootstrap.servers": kafka_config["bootstrap_servers"],
        "group.id": kafka_config["group_id"],
        "auto.offset.reset": kafka_config["auto_offset_reset"],
        # Use batch-oriented processing for better throughput
        "max.poll.records": kafka_config["batch_size"],
        # Enable auto-commit for Kafka offsets
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,  # Commit every 5 seconds
        # Set session timeout to detect failed consumers quickly
        "session.timeout.ms": 30000,  # 30 seconds
    }

    # Create and return Kafka consumer
    try:
        consumer = Consumer(consumer_config)
        consumer.subscribe([kafka_config["topic"]])

        logger.info(
            "Connected to Kafka",
            bootstrap_servers=kafka_config["bootstrap_servers"],
            group_id=kafka_config["group_id"],
            topic=kafka_config["topic"],
        )

        return consumer

    except KafkaException as e:
        logger.error("Failed to connect to Kafka", error=str(e))
        KAFKA_ERRORS.inc()
        raise


def run_consumer(consumer, redis_client):
    """
    Run the main Kafka consumer processing loop

    Args:
        consumer: Kafka consumer instance
        redis_client: Redis client for feature updates
    """
    from apps.feature_builder.loader import process_batch

    # For metrics
    batch_time_start = time.time()
    batch_size = 0

    # Get configuration values
    batch_timeout_ms = config["kafka"]["batch_timeout_ms"]
    batch_size_limit = config["kafka"]["batch_size"]
    feature_update_interval = config["processing"]["feature_update_interval"]
    window_cleanup_frequency = config["processing"]["window_cleanup_frequency"]

    # Track feature update timing
    last_feature_update = time.time()
    last_window_cleanup = time.time()
    transaction_count = 0

    # Load batch of messages
    logger.info("Starting consumer loop")

    # Keep track of batch for processing
    messages = []

    # Main consumer loop
    while running:
        # Poll for a batch of messages
        batch = consumer.consume(
            num_messages=batch_size_limit,
            timeout=(batch_timeout_ms / 1000),  # Convert ms to seconds
        )

        if batch:
            # Process the batch
            batch_time = time.time() - batch_time_start
            batch_size = len(batch)

            # Log every 10,000 messages or every minute
            should_log = (metrics["processed"] % 10000 == 0 and batch_size > 0) or (
                time.time() - metrics["last_stats_time"] > 60
            )

            if should_log:
                logger.info(
                    "Processing batch",
                    batch_size=batch_size,
                    processed_total=metrics["processed"],
                    errors=metrics["errors"],
                    elapsed_time=f"{batch_time:.3f}s",
                )
                metrics["last_stats_time"] = time.time()

            # Add to metrics
            metrics["processed"] += batch_size
            TX_PROCESSED.inc(batch_size)
            KAFKA_MESSAGES.inc(batch_size)

            # Process the batch
            process_batch(batch, redis_client, config)
            transaction_count += batch_size

            # Record processing time
            KAFKA_PROCESSING_TIME.observe(time.time() - batch_time_start)

            # Check if it's time to clean up windows
            if transaction_count >= window_cleanup_frequency:
                transaction_count = 0
                # Window cleanup will be handled by loader.py

            # Start timing the next batch
            batch_time_start = time.time()

        # Check if it's time to update features
        if time.time() - last_feature_update > feature_update_interval:
            # Feature update will be handled by loader.py
            last_feature_update = time.time()


def handle_signals(signum, _):
    """
    Handle termination signals gracefully
    """
    global running

    logger.info(f"Received signal {signum}, initiating shutdown")
    running = False


def run_service():
    """
    Main service entry point
    """
    global running
    consumer = None
    redis_client = None
    health_server = None

    # Initialize metrics
    init_metrics()

    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTERM, handle_signals)

    try:
        # Connect to Redis with retry logic first
        redis_client = connect_to_redis()
        service_status["redis_connected"] = True

        # Start health check server with redis client
        health_server = start_health_check_server(redis_client)

        # Connect to Kafka and create consumer
        consumer = connect_to_kafka()
        service_status["kafka_connected"] = True

        # Update service status
        service_status["status"] = "running"

        # Memory optimization: add periodic garbage collection
        def periodic_gc():
            while running:
                # Every 5 minutes, force garbage collection
                time.sleep(300)
                if running:
                    logger.debug("Running garbage collection")
                    gc.collect()

        # Start garbage collection thread
        gc_thread = threading.Thread(target=periodic_gc)
        gc_thread.daemon = True
        gc_thread.start()
        logger.info("Started periodic garbage collection")

        # Start the main processing loop
        run_consumer(consumer, redis_client)

    except Exception as e:
        logger.error("Fatal error", error=str(e))
        service_status["status"] = "degraded"

    finally:
        # Clean shutdown
        logger.info("Shutting down feature loader service")
        service_status["status"] = "stopping"

        # Close Kafka consumer
        if consumer is not None:
            try:
                consumer.close()
                logger.info("Kafka consumer closed")
            except Exception as e:
                logger.error("Error closing Kafka consumer", error=str(e))
            service_status["kafka_connected"] = False

        # Close Redis client (no explicit close needed for Redis)
        service_status["redis_connected"] = False

        # Shutdown health check server if it was started
        if health_server is not None:
            try:
                health_server.shutdown()
                logger.info("Health check server stopped")
            except Exception as e:
                logger.warning("Error stopping health check server", error=str(e))

        logger.info("Shutdown complete")


def shutdown_handler(sig, _):
    """Handle shutdown gracefully."""
    logger.warning(f"Received signal {sig}, shutting down gracefully...")
    shutdown_event.set()
