"""
Health and metrics server for Graph Loader service.

Provides HTTP endpoints for health checks and Prometheus metrics.
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import structlog

from apps.graph_loader.config import config

logger = structlog.get_logger()


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health and metrics endpoints."""

    def __init__(self, graph_service, *args, **kwargs):
        """Initialize handler with reference to graph service."""
        self.graph_service = graph_service
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == "/health":
                self._handle_health()
            elif path == "/metrics":
                self._handle_metrics()
            elif path == "/status":
                self._handle_status()
            else:
                self._send_response(404, {"error": "Not found"})

        except Exception as e:
            logger.error("Error handling request", error=str(e), path=self.path)
            self._send_response(500, {"error": "Internal server error"})

    def _handle_health(self):
        """Handle health check endpoint."""
        try:
            health_status = self.graph_service.get_health_status()

            # Determine HTTP status code based on health
            if health_status["status"] == "healthy":
                status_code = 200
            elif health_status["status"] == "degraded":
                status_code = 200  # Still operational
            else:
                status_code = 503  # Service unavailable

            self._send_response(status_code, health_status)

        except Exception as e:
            logger.error("Error getting health status", error=str(e))
            self._send_response(503, {"status": "error", "error": str(e)})

    def _handle_metrics(self):
        """Handle Prometheus metrics endpoint."""
        try:
            health_status = self.graph_service.get_health_status()
            performance = health_status.get("performance", {})

            # Generate Prometheus metrics format
            metrics = []

            # Service status (1 = healthy, 0 = unhealthy)
            status_value = 1 if health_status["status"] == "healthy" else 0
            metrics.append(f"graph_loader_healthy {status_value}")

            # Uptime
            uptime = health_status.get("uptime_seconds", 0)
            metrics.append(f"graph_loader_uptime_seconds {uptime}")

            # Neo4j metrics
            if performance:
                metrics.append(
                    f"graph_loader_neo4j_avg_write_time_ms {performance.get('avg_write_time_ms', 0)}"
                )
                metrics.append(
                    f"graph_loader_neo4j_p95_write_time_ms {performance.get('p95_write_time_ms', 0)}"
                )
                metrics.append(
                    f"graph_loader_neo4j_total_edges_written {performance.get('total_edges_written', 0)}"
                )
                metrics.append(
                    f"graph_loader_neo4j_total_batches_written {performance.get('total_batches_written', 0)}"
                )
                metrics.append(
                    f"graph_loader_neo4j_edges_per_second {performance.get('edges_per_second', 0)}"
                )

                # Circuit breaker state (1 = closed, 0 = open)
                cb_state = performance.get("circuit_breaker_state", "closed")
                cb_value = 1 if cb_state == "closed" else 0
                metrics.append(f"graph_loader_neo4j_circuit_breaker_closed {cb_value}")

            # Service info
            service_info = health_status.get("service", {})
            edges_processed = service_info.get("edges_processed", 0)
            metrics.append(f"graph_loader_edges_processed_total {edges_processed}")

            # Configuration metrics
            config_info = health_status.get("config", {})
            target_eps = config_info.get("target_edges_per_sec", 0)
            batch_size = config_info.get("batch_size", 0)
            metrics.append(f"graph_loader_target_edges_per_second {target_eps}")
            metrics.append(f"graph_loader_batch_size {batch_size}")

            # Send as plain text
            metrics_text = "\n".join(metrics) + "\n"
            self._send_text_response(200, metrics_text)

        except Exception as e:
            logger.error("Error generating metrics", error=str(e))
            self._send_text_response(500, "# Error generating metrics\n")

    def _handle_status(self):
        """Handle detailed status endpoint."""
        try:
            health_status = self.graph_service.get_health_status()

            # Add additional status information
            status = {
                **health_status,
                "timestamp": time.time(),
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics",
                    "status": "/status",
                },
            }

            self._send_response(200, status)

        except Exception as e:
            logger.error("Error getting status", error=str(e))
            self._send_response(500, {"error": str(e)})

    def _send_response(self, status_code: int, data: dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode("utf-8"))

    def _send_text_response(self, status_code: int, text: str):
        """Send plain text response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(text.encode("utf-8"))

    def log_message(self, format, *args):
        """Override to use structured logging."""
        logger.debug("HTTP request", message=format % args)


class HealthServer:
    """
    HTTP server for health checks and metrics.

    Provides endpoints for monitoring the Graph Loader service.
    """

    def __init__(self, graph_service, port: int = None):
        """
        Initialize health server.

        Args:
            graph_service: Reference to the main GraphLoaderService
            port: Port to listen on (defaults to config value)
        """
        self.graph_service = graph_service
        self.port = port or config["monitoring"]["port"]
        self.server = None
        self.server_thread = None
        self.running = False

    def start(self):
        """Start the health server in a background thread."""
        try:
            # Create handler class with service reference
            def handler_factory(*args, **kwargs):
                return HealthHandler(self.graph_service, *args, **kwargs)

            # Create HTTP server
            self.server = HTTPServer(("0.0.0.0", self.port), handler_factory)
            self.running = True

            # Start server in background thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()

            logger.info("Health server started", port=self.port)

        except Exception as e:
            logger.error("Failed to start health server", error=str(e), port=self.port)
            raise

    def _run_server(self):
        """Run the HTTP server."""
        try:
            while self.running:
                self.server.handle_request()
        except Exception as e:
            if self.running:  # Only log if we're supposed to be running
                logger.error("Health server error", error=str(e))

    def stop(self):
        """Stop the health server."""
        if self.running:
            logger.info("Stopping health server")
            self.running = False

            if self.server:
                try:
                    self.server.shutdown()
                    self.server.server_close()
                except Exception as e:
                    logger.error("Error stopping health server", error=str(e))

            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)

            logger.info("Health server stopped")


def start_health_server(graph_service, port: int = None) -> HealthServer:
    """
    Start health server for the graph loader service.

    Args:
        graph_service: Reference to the main GraphLoaderService
        port: Port to listen on

    Returns:
        HealthServer instance
    """
    health_server = HealthServer(graph_service, port)
    health_server.start()
    return health_server
