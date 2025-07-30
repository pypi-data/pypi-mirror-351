"""
Sentr Ingest Service
======================

Consumes Avro-encoded 'CardAttempt' events from the 'card_attempts' topic,
enriches each record with GeoIP information, and publishes a JSON document to
the 'tx_enriched' topic for further feature engineering.

Environment variables
---------------------
KAFKA_BOOTSTRAP        Bootstrap brokers (default "kafka:9092" in containers, "localhost:29092" on host) 
KAFKA_CONSUMER_GROUP   Consumer group id (default "sentr-ingest")
KAFKA_SRC_TOPIC        Source topic to consume from (default "card_attempts")
KAFKA_DST_TOPIC        Destination topic to produce to (default "tx_enriched")
KAFKA_RETRIES          Number of connection retry attempts (default 3)
KAFKA_RETRY_BACKOFF    Seconds between retries (default 2)
GEOIP_DB_PATH          Path to MaxMind GeoLite DB (default "/geoip/GeoLite2-City.mmdb")
GEOIP_CACHE_SIZE       Size of GeoIP lookup cache (default 1000)
LOG_LEVEL              Logging level (default "INFO")
POISON_PILL_THRESHOLD  Number of poison pills before alerting (default 10)

Usage
-----
python -m apps.ingest.main
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import signal
import socket
import threading
import time
from datetime import datetime, timezone
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import geoip2.database
import geoip2.errors
import structlog
from confluent_kafka import Consumer, KafkaError, KafkaException, Producer
from pydantic import ValidationError
from sentr.common.config import get_config
from sentr.common.logging import configure_logging
from sentr.schemas.card_attempt import CardAttempt
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

# Configuration with smart defaults (container vs local)
DEFAULT_BOOTSTRAP = (
    "localhost:29092" if os.environ.get("HOSTNAME") != "kafka" else "kafka:9092"
)

config = get_config(
    {
        "kafka": {
            "bootstrap": os.getenv("KAFKA_BOOTSTRAP", DEFAULT_BOOTSTRAP),
            "consumer_group": os.getenv("KAFKA_CONSUMER_GROUP", "sentr-ingest"),
            "src_topic": os.getenv("KAFKA_SRC_TOPIC", "card_attempts"),
            "dst_topic": os.getenv("KAFKA_DST_TOPIC", "tx_enriched"),
            "retries": int(os.getenv("KAFKA_RETRIES", "3")),
            "retry_backoff": int(os.getenv("KAFKA_RETRY_BACKOFF", "2")),
            "client_id": f"sentr-ingest-{socket.gethostname()}",
            "poll_timeout": 1.0,  # seconds
            "max_poll_interval_ms": 300000,  # 5 minutes
            "session_timeout_ms": 30000,  # 30 seconds
        },
        "geoip": {
            "db_path": os.getenv("GEOIP_DB_PATH", "./geoip/GeoLite2-City.mmdb"),
            "cache_size": int(os.getenv("GEOIP_CACHE_SIZE", "1000")),
            "required": os.getenv("GEOIP_REQUIRED", "false").lower() == "true",
        },
        "monitoring": {
            "poison_pill_threshold": int(os.getenv("POISON_PILL_THRESHOLD", "10")),
            "stats_interval": 60,  # seconds
        },
        "health_check": {
            "enabled": os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true",
            "port": int(os.getenv("HEALTH_CHECK_PORT", "8080")),
            "host": os.getenv("HEALTH_CHECK_HOST", "0.0.0.0"),
            "path": os.getenv("HEALTH_CHECK_PATH", "/health"),
        },
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }
)

# Configure structured logging
log_level = getattr(logging, config["log_level"])
configure_logging(level=log_level)
logger = structlog.get_logger("sentr.ingest")


# Thread-safe cache for GeoIP lookups
from functools import wraps
from threading import RLock


# Create a singleton GeoIP reader
class GeoIPSingleton:
    _instance = None
    _lock = RLock()
    _db_missing = False

    @classmethod
    def get_instance(cls) -> Optional[geoip2.database.Reader]:
        with cls._lock:
            if cls._instance is None and not cls._db_missing:
                try:
                    # Check if file exists first
                    if not os.path.exists(config["geoip"]["db_path"]):
                        logger.warning(
                            "GeoIP database file not found",
                            path=config["geoip"]["db_path"],
                            required=config["geoip"]["required"],
                        )
                        cls._db_missing = True
                        if config["geoip"]["required"]:
                            raise FileNotFoundError(
                                f"Required GeoIP database not found: {config['geoip']['db_path']}"
                            )
                        return None

                    # Load the database
                    cls._instance = geoip2.database.Reader(config["geoip"]["db_path"])
                    logger.info(
                        "GeoIP database loaded", path=config["geoip"]["db_path"]
                    )
                except Exception as e:
                    logger.error(
                        "Failed to load GeoIP database",
                        error=str(e),
                        path=config["geoip"]["db_path"],
                    )
                    cls._db_missing = True
                    if config["geoip"]["required"]:
                        raise
                    return None
            return cls._instance

    @classmethod
    def close(cls) -> None:
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
                cls._instance = None
                logger.info("GeoIP database closed")


# Thread-safe LRU cache decorator
def thread_safe_lru_cache(maxsize=128):
    """Thread-safe version of lru_cache"""

    def decorator(func):
        cache = lru_cache(maxsize=maxsize)(func)
        lock = RLock()

        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return cache(*args, **kwargs)

        wrapper.cache_info = cache.cache_info
        wrapper.cache_clear = cache.cache_clear
        return wrapper

    return decorator


# Create a cached version of the GeoIP lookup function
@thread_safe_lru_cache(maxsize=config["geoip"]["cache_size"])
def lookup_geoip(ip_addr: str) -> Tuple[str, str]:
    """Look up GeoIP information with thread-safe caching

    Args:
        ip_addr: IP address to look up

    Returns:
        Tuple of (country_code, city_name)
    """
    try:
        reader = GeoIPSingleton.get_instance()
        if reader is None:
            # GeoIP database not available
            return ("", "")

        response = reader.city(ip_addr)
        return (response.country.iso_code or "", response.city.name or "")
    except geoip2.errors.AddressNotFoundError:
        return ("", "")
    except Exception as e:
        logger.warning("GeoIP lookup failed", ip=ip_addr, error=str(e))
        return ("", "")


# Global service status for health checks
service_status = {
    "status": "initializing",  # initializing, running, degraded, stopping
    "start_time": time.time(),
    "metrics": {
        "processed": 0,
        "errors": 0,
        "poison_pills": 0,
    },
    "kafka_connected": False,
    "geoip_loaded": False,
}


# Health check HTTP server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == config["health_check"]["path"]:
            # Basic health check
            status_code = (
                200 if service_status["status"] in ["running", "initializing"] else 503
            )

            # Calculate uptime and processing rate
            uptime = time.time() - service_status["start_time"]
            rate = service_status["metrics"]["processed"] / uptime if uptime > 0 else 0

            # Prepare response
            response = {
                "status": service_status["status"],
                "uptime_seconds": round(uptime, 1),
                "rate_per_second": round(rate, 2),
                "kafka_connected": service_status["kafka_connected"],
                "geoip_loaded": service_status["geoip_loaded"],
                "metrics": service_status["metrics"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0",
            }

            # Send response
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            # Not found
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Redirect logs to our logger
        logger.debug(
            "Health check request", path=self.path, client=self.client_address[0]
        )


def start_health_check_server():
    """Start the health check HTTP server in a background thread"""
    if not config["health_check"]["enabled"]:
        logger.info("Health check server disabled")
        return None

    try:
        server = HTTPServer(
            (config["health_check"]["host"], config["health_check"]["port"]),
            HealthCheckHandler,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        logger.info(
            "Health check server started",
            host=config["health_check"]["host"],
            port=config["health_check"]["port"],
            path=config["health_check"]["path"],
        )
        return server
    except Exception as e:
        logger.error("Failed to start health check server", error=str(e))
        return None


def delivery_report(err, msg) -> None:
    """Kafka delivery callback function"""
    if err is not None:
        logger.error(
            "Message delivery failed",
            error=str(err),
            topic=msg.topic(),
            partition=msg.partition(),
        )
    else:
        logger.debug(
            "Message delivered",
            topic=msg.topic(),
            partition=msg.partition(),
            offset=msg.offset(),
        )


@retry(
    retry=retry_if_exception_type((KafkaException, ConnectionError, socket.gaierror)),
    stop=stop_after_attempt(config["kafka"]["retries"]),
    wait=wait_fixed(config["kafka"]["retry_backoff"]),
    reraise=True,
)
def create_kafka_clients() -> Tuple[Consumer, Producer]:
    """Create Kafka consumer and producer with retry logic"""
    try:
        logger.info("Connecting to Kafka", bootstrap=config["kafka"]["bootstrap"])

        # Create consumer
        consumer = Consumer(
            {
                "bootstrap.servers": config["kafka"]["bootstrap"],
                "group.id": config["kafka"]["consumer_group"],
                "client.id": f"{config['kafka']['client_id']}-consumer",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
                "max.poll.interval.ms": config["kafka"]["max_poll_interval_ms"],
                "session.timeout.ms": config["kafka"]["session_timeout_ms"],
            }
        )

        # Create producer
        producer = Producer(
            {
                "bootstrap.servers": config["kafka"]["bootstrap"],
                "client.id": f"{config['kafka']['client_id']}-producer",
                "retries": 3,  # Internal retries for produce requests
                "retry.backoff.ms": 500,
                "acks": "all",  # Wait for all replicas
            }
        )

        return consumer, producer
    except Exception as e:
        logger.error("Failed to create Kafka clients", error=str(e))
        raise


def main() -> None:
    """Main processing loop for the ingest service"""
    # Initialize metrics
    metrics = {
        "processed": 0,
        "errors": 0,
        "poison_pills": 0,
        "geoip_hits": 0,
        "geoip_misses": 0,
        "start_time": time.time(),
        "last_stats_time": time.time(),
    }

    # Update global service status
    service_status["start_time"] = time.time()
    service_status["status"] = "initializing"

    # Set up graceful shutdown
    running = True

    def _stop(*_: object) -> None:
        nonlocal running
        running = False
        service_status["status"] = "stopping"
        logger.info("Shutdown signal received, will exit after current message")

    # Register signal handlers
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    # Start health check server
    health_server = start_health_check_server()

    # Initialize Kafka clients and GeoIP reader
    consumer = None
    producer = None

    try:
        # Create Kafka clients with retry logic
        logger.info(
            "Starting ingest service",
            bootstrap=config["kafka"]["bootstrap"],
            src_topic=config["kafka"]["src_topic"],
            dst_topic=config["kafka"]["dst_topic"],
        )

        # Initialize GeoIP reader (will be loaded on first use)
        try:
            # Pre-load GeoIP database to verify it works
            reader = GeoIPSingleton.get_instance()
            service_status["geoip_loaded"] = True
        except Exception as e:
            logger.error("Failed to initialize GeoIP database", error=str(e))
            service_status["status"] = "degraded"

        # Connect to Kafka
        try:
            consumer, producer = create_kafka_clients()
            consumer.subscribe([config["kafka"]["src_topic"]])
            service_status["kafka_connected"] = True
        except Exception as e:
            logger.error("Failed to connect to Kafka", error=str(e))
            service_status["status"] = "degraded"
            raise

        # Update service status to running
        service_status["status"] = "running"

        # Main processing loop
        while running:
            # Check if it's time to log stats
            current_time = time.time()
            if (
                current_time - metrics["last_stats_time"]
                >= config["monitoring"]["stats_interval"]
            ):
                # Calculate rates and log metrics
                duration = current_time - metrics["start_time"]
                rate = metrics["processed"] / duration if duration > 0 else 0

                # Report cache efficiency
                cache_info = lookup_geoip.cache_info()
                cache_hit_ratio = (
                    cache_info.hits / (cache_info.hits + cache_info.misses)
                    if (cache_info.hits + cache_info.misses) > 0
                    else 0
                )

                logger.info(
                    "Processing statistics",
                    uptime_seconds=f"{duration:.1f}",
                    rate_per_second=f"{rate:.2f}",
                    processed=metrics["processed"],
                    errors=metrics["errors"],
                    poison_pills=metrics["poison_pills"],
                    geoip_cache_hits=cache_info.hits,
                    geoip_cache_misses=cache_info.misses,
                    geoip_cache_hit_ratio=f"{cache_hit_ratio:.2f}",
                )

                # Check if we've exceeded poison pill threshold
                if (
                    metrics["poison_pills"]
                    >= config["monitoring"]["poison_pill_threshold"]
                ):
                    logger.warning(
                        "Poison pill threshold exceeded",
                        threshold=config["monitoring"]["poison_pill_threshold"],
                        count=metrics["poison_pills"],
                    )

                # Reset stats timer
                metrics["last_stats_time"] = current_time

            # Poll for messages with timeout
            msg = consumer.poll(config["kafka"]["poll_timeout"])

            # Handle poll result
            if msg is None:
                continue

            if msg.error():
                error_code = msg.error().code()
                if error_code == KafkaError._PARTITION_EOF:
                    # End of partition, not an error
                    logger.debug("Reached end of partition")
                else:
                    logger.warning(
                        "Kafka error", error=str(msg.error()), code=error_code
                    )
                    metrics["errors"] += 1
                continue

            # Process the message
            try:
                # Deserialize the Avro message
                try:
                    attempt = CardAttempt.from_avro_bytes(msg.value())
                except (ValidationError, ValueError) as exc:
                    logger.error(
                        "Deserialization failed",
                        error=str(exc),
                        topic=msg.topic(),
                        partition=msg.partition(),
                        offset=msg.offset(),
                    )
                    metrics["poison_pills"] += 1
                    consumer.commit(msg, asynchronous=False)  # Skip poison pill
                    continue

                # GeoIP enrichment with caching
                ip_addr = attempt.ip.addr
                country, city = lookup_geoip(ip_addr)
                attempt.ip.geo_country = country
                attempt.ip.geo_city = city

                # Update metrics based on cache result
                if lookup_geoip.cache_info().hits > metrics["geoip_hits"]:
                    metrics["geoip_hits"] = lookup_geoip.cache_info().hits
                if lookup_geoip.cache_info().misses > metrics["geoip_misses"]:
                    metrics["geoip_misses"] = lookup_geoip.cache_info().misses

                # Serialize the enriched message
                enriched_json = attempt.model_dump_json(by_alias=True).encode()

                # Implement robust producer with retries and backoff
                max_retries = config["kafka"].get("retries", 5)
                retry_count = 0
                success = False

                while not success and retry_count <= max_retries:
                    try:
                        # Produce to destination topic
                        producer.produce(
                            topic=config["kafka"]["dst_topic"],
                            key=attempt.card_id,
                            value=enriched_json,
                            callback=delivery_report,
                        )
                        # If we got here, the produce was successful
                        success = True
                    except (BufferError, KafkaException) as e:
                        # Increment retry count
                        retry_count += 1

                        if retry_count > max_retries:
                            # We've exhausted our retries, log and propagate the error
                            logger.error(
                                "Failed to produce message after retries",
                                error=str(e),
                                retries=retry_count,
                                card_id=attempt.card_id,
                            )
                            # Update error metrics
                            metrics["errors"] += 1
                            service_status["metrics"]["errors"] = metrics["errors"]
                            # We'll continue and let the main loop handle the error
                            break

                        # Log the error
                        error_type = (
                            "BufferError"
                            if isinstance(e, BufferError)
                            else "KafkaException"
                        )
                        logger.warning(
                            f"Kafka producer {error_type}, retrying",
                            retry=retry_count,
                            max_retries=max_retries,
                            error=str(e),
                        )

                        # Call poll to serve delivery callbacks and make room in the queue
                        producer.poll(1.0)

                        # Calculate backoff with jitter to prevent all retries happening at once
                        # Exponential backoff: base_delay * (2^retry_count) + random jitter
                        base_delay = config["kafka"].get("retry_backoff", 1.0)
                        max_delay = 30.0  # Cap the maximum delay at 30 seconds
                        delay = min(base_delay * (2**retry_count), max_delay)
                        jitter = random.uniform(0, 0.1 * delay)  # Add up to 10% jitter
                        backoff = delay + jitter

                        logger.debug(
                            f"Backing off for {backoff:.2f} seconds before retry"
                        )
                        time.sleep(backoff)

                # Serve delivery callbacks if production was successful
                if success:
                    producer.poll(0)

                    # Commit the offset on success
                    consumer.commit(msg, asynchronous=True)

                    # Update success metrics
                    metrics["processed"] += 1
                    service_status["metrics"]["processed"] = metrics["processed"]

                    # Log successful processing at debug level
                    logger.debug(
                        "Successfully processed and produced message",
                        card_id=attempt.card_id,
                        topic=config["kafka"]["dst_topic"],
                    )
                else:
                    # We failed to produce the message after all retries
                    # Commit the offset anyway to prevent getting stuck on this message
                    consumer.commit(msg, asynchronous=False)

                    # Check if we should degrade service status
                    if metrics["errors"] > config["monitoring"].get(
                        "error_threshold", 10
                    ):
                        service_status["status"] = "degraded"

            except Exception as e:
                # Catch any other processing errors
                logger.error(
                    "Error processing message",
                    error=str(e),
                    topic=msg.topic(),
                    partition=msg.partition(),
                    offset=msg.offset(),
                )
                metrics["errors"] += 1
                service_status["metrics"]["errors"] = metrics["errors"]

                # Check if we should degrade service status
                if metrics["errors"] > 10:
                    service_status["status"] = "degraded"

                # Still commit to avoid getting stuck on a bad message
                consumer.commit(msg, asynchronous=False)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error("Fatal error", error=str(e))
        service_status["status"] = "degraded"
    finally:
        # Clean shutdown
        logger.info("Shutting down ingest service")
        service_status["status"] = "stopping"

        # Close Kafka clients
        if producer is not None:
            producer.flush(timeout=5.0)
            logger.info("Producer flushed")
            service_status["kafka_connected"] = False

        if consumer is not None:
            consumer.close()
            logger.info("Consumer closed")

        # Close GeoIP reader
        try:
            GeoIPSingleton.close()
            service_status["geoip_loaded"] = False
        except Exception as e:
            logger.warning("Error closing GeoIP reader", error=str(e))

        # Shutdown health check server if it was started
        if health_server is not None:
            try:
                health_server.shutdown()
                logger.info("Health check server stopped")
            except Exception as e:
                logger.warning("Error stopping health check server", error=str(e))

        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
