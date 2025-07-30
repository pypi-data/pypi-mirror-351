"""
Main service for Graph Loader.

Integrates Kafka consumer, edge builder, and Neo4j writer for high-performance graph processing.
"""

import signal
import threading
import time
from typing import Any, Dict, List

import structlog

from apps.graph_loader.config import config, service_status
from apps.graph_loader.edge_builder.edge_builder import EdgeAggregator, EdgeBuilder
from apps.graph_loader.health_server import start_health_server
from apps.graph_loader.kafka_consumer.consumer import GraphLoaderKafkaConsumer
from apps.graph_loader.neo4j_writer.neo4j_driver import Neo4jBatchWriter

logger = structlog.get_logger()


class GraphLoaderService:
    """
    Main Graph Loader service that orchestrates all components.

    Features:
    - High-performance transaction processing
    - Exactly-once semantics
    - Comprehensive monitoring
    - Graceful shutdown
    """

    def __init__(self):
        """Initialize the Graph Loader service."""
        self.running = True
        self.edge_builder = EdgeBuilder()
        self.edge_aggregator = EdgeAggregator()
        self.neo4j_writer = Neo4jBatchWriter()
        self.kafka_consumer = None
        self.health_server = None

        # Performance tracking
        self.start_time = time.time()
        self.transactions_processed = 0
        self.edges_created = 0
        self.batches_written = 0
        self.last_metrics_time = time.time()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, _):
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal", signal=signum)
        self.running = False
        if self.kafka_consumer:
            self.kafka_consumer.stop()

    def start(self):
        """Start the Graph Loader service."""
        logger.info("Starting Graph Loader service")

        try:
            # Update service status
            service_status["status"] = "starting"

            # Connect to Neo4j
            logger.info("Connecting to Neo4j...")
            self.neo4j_writer.connect()

            # Create Kafka consumer with message handler
            logger.info("Initializing Kafka consumer...")
            self.kafka_consumer = GraphLoaderKafkaConsumer(
                self._process_transaction_batch
            )

            # Start health server
            logger.info("Starting health server...")
            self.health_server = start_health_server(self)

            # Update service status
            service_status["status"] = "running"
            service_status["start_time"] = self.start_time

            logger.info("Graph Loader service started successfully")

            # Start metrics reporting thread
            metrics_thread = threading.Thread(
                target=self._metrics_reporter, daemon=True
            )
            metrics_thread.start()

            # Start consuming messages
            self.kafka_consumer.start()

        except Exception as e:
            logger.error("Failed to start Graph Loader service", error=str(e))
            service_status["status"] = "error"
            service_status["error"] = str(e)
            raise
        finally:
            self._shutdown()

    def _process_transaction_batch(self, transactions: List[Dict[str, Any]]) -> bool:
        """
        Process a batch of transactions into graph edges.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            True if successful, False otherwise
        """
        if not transactions:
            return True

        try:
            batch_start_time = time.time()

            # Build edges from transactions
            edges = self.edge_builder.build_edges(transactions)

            if not edges:
                logger.debug(
                    "No edges generated from transaction batch",
                    batch_size=len(transactions),
                )
                return True

            # Aggregate edges by edge_id
            aggregated_edges = self.edge_aggregator.aggregate_edges(edges)

            # Format for Neo4j
            neo4j_edges = self.edge_aggregator.format_for_neo4j(aggregated_edges)

            # Write to Neo4j
            success = self.neo4j_writer.write_edges_batch(neo4j_edges)

            if success:
                # Update metrics
                self.transactions_processed += len(transactions)
                self.edges_created += len(edges)
                self.batches_written += 1

                # Update service status
                service_status["edges_processed"] = self.edges_created
                service_status["last_write"] = time.time()

                processing_time = time.time() - batch_start_time
                logger.debug(
                    "Successfully processed transaction batch",
                    transactions=len(transactions),
                    edges_created=len(edges),
                    aggregated_edges=len(aggregated_edges),
                    processing_time_ms=round(processing_time * 1000, 2),
                )

                return True
            else:
                logger.error(
                    "Failed to write edges to Neo4j", batch_size=len(transactions)
                )
                return False

        except Exception as e:
            logger.error(
                "Error processing transaction batch",
                error=str(e),
                batch_size=len(transactions),
            )
            return False

    def _metrics_reporter(self):
        """Background thread for reporting metrics."""
        while self.running:
            try:
                time.sleep(config["monitoring"]["metrics_interval"])

                if not self.running:
                    break

                current_time = time.time()
                elapsed = current_time - self.last_metrics_time

                if elapsed > 0:
                    # Calculate rates
                    tx_rate = self.transactions_processed / elapsed
                    edge_rate = self.edges_created / elapsed

                    # Get Neo4j performance stats
                    neo4j_stats = self.neo4j_writer.get_performance_stats()

                    # Log comprehensive metrics
                    logger.info(
                        "Graph Loader Performance Metrics",
                        uptime_minutes=round((current_time - self.start_time) / 60, 2),
                        transactions_per_sec=round(tx_rate, 2),
                        edges_per_sec=round(edge_rate, 2),
                        total_transactions=self.transactions_processed,
                        total_edges=self.edges_created,
                        total_batches=self.batches_written,
                        neo4j_avg_write_ms=neo4j_stats["avg_write_time_ms"],
                        neo4j_p95_write_ms=neo4j_stats["p95_write_time_ms"],
                        neo4j_circuit_breaker=neo4j_stats["circuit_breaker_state"],
                    )

                    # Reset counters for next interval
                    self.transactions_processed = 0
                    self.edges_created = 0
                    self.batches_written = 0
                    self.last_metrics_time = current_time

            except Exception as e:
                logger.error("Error in metrics reporter", error=str(e))

    def _shutdown(self):
        """Gracefully shutdown the service."""
        logger.info("🛑 Shutting down Graph Loader service")

        service_status["status"] = "shutting_down"

        try:
            # Stop Kafka consumer
            if self.kafka_consumer:
                self.kafka_consumer.stop()

            # Stop health server
            if self.health_server:
                self.health_server.stop()

            # Close Neo4j connection
            self.neo4j_writer.close()

            service_status["status"] = "stopped"
            logger.info("Graph Loader service stopped successfully")

        except Exception as e:
            logger.error("Error during shutdown", error=str(e))
            service_status["status"] = "error"
            service_status["error"] = str(e)

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        try:
            # Get Neo4j health
            neo4j_health = self.neo4j_writer.health_check()

            # Get performance stats
            neo4j_stats = self.neo4j_writer.get_performance_stats()

            # Calculate uptime
            uptime_seconds = time.time() - self.start_time

            # Determine overall health
            overall_status = "healthy"
            if neo4j_health["status"] != "healthy":
                overall_status = "unhealthy"
            elif neo4j_stats["circuit_breaker_state"] == "open":
                overall_status = "degraded"

            return {
                "status": overall_status,
                "uptime_seconds": round(uptime_seconds, 2),
                "service": service_status,
                "neo4j": neo4j_health,
                "performance": neo4j_stats,
                "config": {
                    "target_edges_per_sec": config["performance"][
                        "target_edges_per_sec"
                    ],
                    "enabled_edge_types": config["edge_processing"][
                        "enabled_edge_types"
                    ],
                    "batch_size": config["neo4j"]["batch_size"],
                },
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "service": service_status}


def main():
    """Main entry point for the Graph Loader service."""
    logger.info("Sentr Graph Loader v1.0.0")

    try:
        service = GraphLoaderService()
        service.start()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error("Service failed", error=str(e))
        raise


if __name__ == "__main__":
    main()
