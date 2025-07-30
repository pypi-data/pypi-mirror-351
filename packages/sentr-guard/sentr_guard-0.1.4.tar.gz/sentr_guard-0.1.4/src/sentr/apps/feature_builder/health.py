"""
Health monitoring module for Sentr Feature Loader.

Implements HTTP health check server and endpoints for monitoring.
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from apps.feature_builder.config import config, logger, metrics, service_status

# Import metrics for health validation
try:
    from apps.feature_builder.metrics import (
        KAFKA_TOTAL_LAG,
        REDIS_ERRORS,
        REDIS_MEMORY_USAGE,
        SERVICE_LAST_SUCCESS,
        TX_FAILED,
        TX_PROCESSED,
    )
except ImportError:
    # Fallback if metrics not available
    REDIS_MEMORY_USAGE = None
    REDIS_ERRORS = None
    KAFKA_TOTAL_LAG = None
    SERVICE_LAST_SUCCESS = None
    TX_PROCESSED = None
    TX_FAILED = None


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check and metrics endpoints"""

    def do_GET(self):
        """Handle GET requests for health check and metrics"""
        # Parse the URL to get the path
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Get components from the server
        redis_client = getattr(self.server, "redis_client", None)
        redis_pipeline = getattr(self.server, "redis_pipeline", None)
        kafka_consumer = getattr(self.server, "kafka_consumer", None)

        # Handle health check endpoint
        if path == "/health":
            self._handle_health_check(redis_client, redis_pipeline, kafka_consumer)

        # Handle metrics endpoint
        elif path == "/metrics":
            self.send_response(200)
            self.send_header("Content-type", CONTENT_TYPE_LATEST)
            self.end_headers()

            # Get latest Prometheus metrics
            metrics_data = generate_latest()
            self.wfile.write(metrics_data)

        # Handle unknown paths
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found\n")

    def _handle_health_check(self, redis_client, redis_pipeline, kafka_consumer):
        """Handle health check logic"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # Basic health check response
        health_data = {
            "status": service_status.get("status", "unknown"),
            "uptime": time.time() - metrics.get("start_time", time.time()),
            "processedCount": metrics.get("processed", 0),
            "errorCount": metrics.get("errors", 0),
            "checks": {},
        }

        # Check Redis health
        redis_healthy = self._check_redis_health(
            redis_client, redis_pipeline, health_data
        )

        # Check Kafka health
        kafka_healthy = self._check_kafka_health(kafka_consumer, health_data)

        # Overall health status
        health_data["healthy"] = redis_healthy and kafka_healthy

        self.wfile.write(json.dumps(health_data).encode())

    def _check_redis_health(self, redis_client, redis_pipeline, health_data):
        """Check Redis health and add to health data"""
        if not redis_client:
            health_data["checks"]["redis"] = {
                "connected": False,
                "error": "Redis client not available",
            }
            return False

        try:
            # Test Redis connection
            redis_client.ping()

            # Test pipeline if available
            pipeline_healthy = True
            if redis_pipeline:
                try:
                    # Test pipeline functionality
                    pipeline_healthy = redis_pipeline.flush_if_needed(force=False)
                except Exception as e:
                    pipeline_healthy = False
                    logger.warning("Pipeline health check failed", error=str(e))

            # Get Redis info
            info = redis_client.info()
            memory_usage = info.get("used_memory", 0)

            # Update Redis metrics if available
            if REDIS_MEMORY_USAGE:
                REDIS_MEMORY_USAGE.set(memory_usage)

            health_data["checks"]["redis"] = {
                "connected": True,
                "pipeline_healthy": pipeline_healthy,
                "memory_usage": memory_usage,
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0),
            }

            return True

        except Exception as e:
            # Catch all exceptions since we're mocking Redis
            health_data["checks"]["redis"] = {
                "connected": False,
                "pipeline_healthy": False,
                "error": str(e),
            }
            return False

    def _check_kafka_health(self, kafka_consumer, health_data):
        """Check Kafka health and add to health data"""
        if not kafka_consumer:
            health_data["checks"]["kafka"] = {
                "connected": False,
                "error": "Kafka consumer not available",
            }
            return False

        try:
            # Check if consumer has assignments
            assignments = kafka_consumer.assignment()

            health_data["checks"]["kafka"] = {
                "connected": True,
                "assignments": len(assignments) if assignments else 0,
            }

            return True

        except Exception as e:
            health_data["checks"]["kafka"] = {"connected": False, "error": str(e)}
            return False

    def log_message(self, format, *args):
        """Override to use structlog instead of print"""
        logger.info("Health server", message=format % args)


class RedisAwareHTTPServer(HTTPServer):
    """HTTPServer subclass that holds component references"""

    def __init__(
        self,
        server_address,
        RequestHandlerClass,
        redis_client=None,
        redis_pipeline=None,
        kafka_consumer=None,
    ):
        super().__init__(server_address, RequestHandlerClass)
        self.redis_client = redis_client
        self.redis_pipeline = redis_pipeline
        self.kafka_consumer = kafka_consumer


def start_health_check_server(
    redis_client=None, redis_pipeline=None, kafka_consumer=None
):
    """Start the health check HTTP server in a separate thread"""
    server_address = ("", config["monitoring"]["port"])
    httpd = RedisAwareHTTPServer(
        server_address,
        HealthCheckHandler,
        redis_client=redis_client,
        redis_pipeline=redis_pipeline,
        kafka_consumer=kafka_consumer,
    )

    # Start server in a new thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    logger.info("Health check server started", port=config["monitoring"]["port"])
    return httpd
