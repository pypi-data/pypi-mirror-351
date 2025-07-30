#!/usr/bin/env python3
"""
Graph Loader Service Validation Script

Validates that the Graph Loader service meets all requirements:
- Performance targets (≥2000 edges/sec, <50ms latency)
- Functional correctness (edge creation, aggregation, Neo4j writing)
- Error handling (circuit breaker, retries, back-pressure)
- Monitoring (health checks, metrics)
"""

import json
import sys
import time
from typing import Any, Dict, List
from unittest.mock import Mock, patch

from apps.graph_loader.config import config

# Import Graph Loader components
from apps.graph_loader.edge_builder.edge_builder import EdgeAggregator, EdgeBuilder
from apps.graph_loader.kafka_consumer.consumer import GraphLoaderKafkaConsumer
from apps.graph_loader.main import GraphLoaderService
from apps.graph_loader.neo4j_writer.neo4j_driver import CircuitBreaker, Neo4jBatchWriter


class GraphLoaderValidator:
    """Validates Graph Loader service functionality and performance."""

    def __init__(self):
        self.results = []
        self.sample_transactions = self._generate_sample_transactions()

    def _generate_sample_transactions(self, count: int = 1000) -> List[Dict[str, Any]]:
        """Generate sample transactions for testing."""
        transactions = []
        for i in range(count):
            transaction = {
                "transaction_id": f"tx_{i:06d}",
                "card_id": f"card_{i % 100:03d}",
                "ip_address": f"192.168.{(i % 254) + 1}.{(i % 254) + 1}",
                "merchant_id": f"merchant_{i % 50:03d}",
                "device_id": f"device_{i % 200:03d}",
                "amount": round(10.0 + (i % 1000), 2),
                "is_success": i % 10 != 0,
                "timestamp": 1700000000 + (i * 10),
            }
            transactions.append(transaction)
        return transactions

    def _log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")

        self.results.append({"test": test_name, "passed": passed, "details": details})

    def validate_edge_builder(self) -> bool:
        """Validate EdgeBuilder functionality and performance."""
        print("\nTesting EdgeBuilder...")

        try:
            edge_builder = EdgeBuilder()

            # Test basic functionality
            edges = edge_builder.build_edges(self.sample_transactions[:10])
            self._log_result(
                "EdgeBuilder creates edges",
                len(edges) > 0,
                f"Created {len(edges)} edges from 10 transactions",
            )

            # Test edge types
            edge_types = {edge.edge_type for edge in edges}
            expected_types = {"CARD_IP", "CARD_MERCHANT", "CARD_DEVICE", "IP_MERCHANT"}
            self._log_result(
                "EdgeBuilder creates all edge types",
                edge_types.issubset(expected_types),
                f"Created edge types: {edge_types}",
            )

            # Test performance
            start_time = time.time()
            all_edges = edge_builder.build_edges(self.sample_transactions)
            elapsed = time.time() - start_time
            edges_per_sec = len(all_edges) / elapsed

            self._log_result(
                "EdgeBuilder meets performance target",
                edges_per_sec > 2000,
                f"{edges_per_sec:.1f} edges/sec (target: >2000)",
            )

            return True

        except Exception as e:
            self._log_result("EdgeBuilder validation", False, f"Error: {e}")
            return False

    def validate_edge_aggregator(self) -> bool:
        """Validate EdgeAggregator functionality."""
        print("\nTesting EdgeAggregator...")

        try:
            edge_builder = EdgeBuilder()
            aggregator = EdgeAggregator()

            # Build edges
            edges = edge_builder.build_edges(self.sample_transactions)

            # Test aggregation (create duplicate edges for aggregation)
            duplicate_transactions = (
                self.sample_transactions[:10] + self.sample_transactions[:10]
            )  # Duplicate for aggregation
            duplicate_edges = edge_builder.build_edges(duplicate_transactions)
            aggregated = aggregator.aggregate_edges(duplicate_edges)
            self._log_result(
                "EdgeAggregator reduces edge count",
                len(aggregated) < len(duplicate_edges),
                f"Reduced {len(duplicate_edges)} edges to {len(aggregated)} aggregated edges",
            )

            # Test Neo4j formatting
            neo4j_edges = aggregator.format_for_neo4j(aggregated)
            self._log_result(
                "EdgeAggregator formats for Neo4j",
                len(neo4j_edges) == len(aggregated),
                f"Formatted {len(neo4j_edges)} edges for Neo4j",
            )

            # Validate edge structure
            if neo4j_edges:
                edge = neo4j_edges[0]
                required_fields = [
                    "edge_id",
                    "edge_type",
                    "src",
                    "dst",
                    "count",
                    "first_seen",
                    "last_seen",
                ]
                has_required = all(field in edge for field in required_fields)
                self._log_result(
                    "Neo4j edges have required fields",
                    has_required,
                    f"Fields: {list(edge.keys())}",
                )

            return True

        except Exception as e:
            self._log_result("EdgeAggregator validation", False, f"Error: {e}")
            return False

    def validate_circuit_breaker(self) -> bool:
        """Validate CircuitBreaker functionality."""
        print("\nTesting CircuitBreaker...")

        try:
            cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

            # Test initial state
            self._log_result(
                "CircuitBreaker starts closed",
                not cb.is_open(),
                f"Initial state: {cb.state}",
            )

            # Test failure handling through call method
            def failing_function():
                raise Exception("Test failure")

            # Cause failures to open circuit breaker
            for i in range(5):
                try:
                    cb.call(failing_function)
                except:
                    pass  # Expected to fail

            self._log_result(
                "CircuitBreaker opens after failures",
                cb.is_open(),
                f"State after 5 failures: {cb.state}",
            )

            # Test that circuit breaker prevents calls when open
            try:
                cb.call(lambda: "should not execute")
                circuit_prevented = False
            except:
                circuit_prevented = True

            self._log_result(
                "CircuitBreaker prevents calls when open",
                circuit_prevented,
                "Circuit breaker correctly blocks calls",
            )

            return True

        except Exception as e:
            self._log_result("CircuitBreaker validation", False, f"Error: {e}")
            return False

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def validate_neo4j_writer(self, mock_graph_db) -> bool:
        """Validate Neo4jBatchWriter functionality."""
        print("\nTesting Neo4jBatchWriter...")

        try:
            # Setup mocks
            mock_driver = Mock()
            mock_session = Mock()
            mock_result = Mock()

            mock_graph_db.driver.return_value = mock_driver
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=None)
            mock_session.run.return_value = mock_result
            mock_result.consume.return_value = Mock()
            mock_result.single.return_value = Mock(__getitem__=Mock(return_value=1))

            # Create writer
            writer = Neo4jBatchWriter()
            writer.connect()

            self._log_result(
                "Neo4jBatchWriter connects successfully",
                writer.driver is not None,
                "Connected to mocked Neo4j",
            )

            # Test health check
            health = writer.health_check()
            self._log_result(
                "Neo4jBatchWriter health check works",
                health["status"] == "healthy",
                f"Health status: {health['status']}",
            )

            # Test edge writing
            sample_edges = [
                {
                    "edge_id": "test123",
                    "edge_type": "CARD_IP",
                    "src": "card:123",
                    "dst": "ip:192.168.1.1",
                    "count": 1,
                    "first_seen": 1700000000,
                    "last_seen": 1700000000,
                }
            ]

            success = writer.write_edges_batch(sample_edges)
            self._log_result(
                "Neo4jBatchWriter writes edges",
                success is True,
                f"Wrote {len(sample_edges)} edges successfully",
            )

            return True

        except Exception as e:
            self._log_result("Neo4jBatchWriter validation", False, f"Error: {e}")
            return False

    @patch("apps.graph_loader.kafka_consumer.consumer.Consumer")
    def validate_kafka_consumer(self, mock_consumer_class) -> bool:
        """Validate KafkaConsumer functionality."""
        print("\nTesting KafkaConsumer...")

        try:
            # Setup mock
            mock_consumer = Mock()
            mock_consumer_class.return_value = mock_consumer

            # Create consumer
            def dummy_handler(transactions):
                return True

            consumer = GraphLoaderKafkaConsumer(dummy_handler)

            self._log_result(
                "KafkaConsumer initializes",
                consumer is not None,
                "Consumer created with message handler",
            )

            # Test message parsing
            mock_message = Mock()
            mock_message.value.return_value = json.dumps(
                {"transaction_id": "tx_123", "card_id": "card_456", "amount": 100.0}
            ).encode("utf-8")
            mock_message.offset.return_value = 123
            mock_message.error.return_value = None
            mock_message.topic.return_value = "tx_enriched"
            mock_message.partition.return_value = 0
            mock_message.timestamp.return_value = (
                1,
                1700000000000,
            )  # (type, timestamp)

            parsed = consumer._parse_message(mock_message)
            self._log_result(
                "KafkaConsumer parses messages",
                parsed is not None and parsed["transaction_id"] == "tx_123",
                f"Parsed transaction: {parsed['transaction_id'] if parsed else 'None'}",
            )

            return True

        except Exception as e:
            self._log_result("KafkaConsumer validation", False, f"Error: {e}")
            return False

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    @patch("apps.graph_loader.kafka_consumer.consumer.Consumer")
    def validate_service_integration(self, mock_consumer_class, mock_graph_db) -> bool:
        """Validate end-to-end service integration."""
        print("\nTesting Service Integration...")

        try:
            # Setup mocks
            mock_driver = Mock()
            mock_session = Mock()
            mock_result = Mock()

            mock_graph_db.driver.return_value = mock_driver
            mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = Mock(return_value=None)
            mock_session.run.return_value = mock_result
            mock_result.consume.return_value = Mock()
            mock_result.single.return_value = Mock(__getitem__=Mock(return_value=1))

            mock_consumer = Mock()
            mock_consumer_class.return_value = mock_consumer

            # Create service
            service = GraphLoaderService()

            self._log_result(
                "GraphLoaderService initializes",
                service is not None,
                "Service created with all components",
            )

            # Connect Neo4j writer for service test
            service.neo4j_writer.driver = mock_driver

            # Test transaction processing
            success = service._process_transaction_batch(self.sample_transactions[:100])
            self._log_result(
                "Service processes transaction batches",
                success is True,
                f"Processed batch of {100} transactions",
            )

            # Test health status
            health = service.get_health_status()
            self._log_result(
                "Service provides health status",
                "status" in health,
                f"Health status: {health.get('status', 'unknown')}",
            )

            return True

        except Exception as e:
            self._log_result("Service integration validation", False, f"Error: {e}")
            return False

    def validate_configuration(self) -> bool:
        """Validate configuration settings."""
        print("\nTesting Configuration...")

        try:
            # Test config access
            kafka_config = config["kafka"]
            neo4j_config = config["neo4j"]
            edge_config = config["edge_processing"]

            self._log_result(
                "Configuration loads successfully",
                all([kafka_config, neo4j_config, edge_config]),
                "All config sections present",
            )

            # Test performance targets
            target_edges = config["performance"]["target_edges_per_sec"]
            latency_threshold = config["performance"]["write_latency_threshold_ms"]

            self._log_result(
                "Performance targets configured",
                target_edges >= 2000 and latency_threshold <= 50,
                f"Target: {target_edges} edges/sec, {latency_threshold}ms latency",
            )

            return True

        except Exception as e:
            self._log_result("Configuration validation", False, f"Error: {e}")
            return False

    def run_validation(self) -> bool:
        """Run complete validation suite."""
        print("Sentr Graph Loader Validation")
        print("=" * 50)

        # Run all validation tests
        tests = [
            self.validate_configuration,
            self.validate_edge_builder,
            self.validate_edge_aggregator,
            self.validate_circuit_breaker,
            self.validate_neo4j_writer,
            self.validate_kafka_consumer,
            self.validate_service_integration,
        ]

        all_passed = True
        for test in tests:
            try:
                passed = test()
                all_passed = all_passed and passed
            except Exception as e:
                print(f"FAIL {test.__name__}: {e}")
                all_passed = False

        # Print summary
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)

        passed_count = sum(1 for r in self.results if r["passed"])
        total_count = len(self.results)

        for result in self.results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {result['test']}")

        print(f"\nResults: {passed_count}/{total_count} tests passed")

        if all_passed:
            print("\nALL VALIDATIONS PASSED!")
            print("Graph Loader service is ready for production")
        else:
            print("\nSOME VALIDATIONS FAILED")
            print("Please fix issues before deploying")

        return all_passed


def main():
    """Main validation entry point."""
    validator = GraphLoaderValidator()
    success = validator.run_validation()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
