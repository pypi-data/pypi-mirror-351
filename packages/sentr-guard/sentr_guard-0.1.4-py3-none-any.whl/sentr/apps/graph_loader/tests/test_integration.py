"""
Integration tests for Graph Loader service.

Tests the full service integration with mocked external dependencies.
"""

import time
from unittest.mock import Mock, patch

import pytest

from apps.graph_loader.edge_builder.edge_builder import EdgeAggregator, EdgeBuilder
from apps.graph_loader.main import GraphLoaderService


class TestGraphLoaderServiceIntegration:
    """Test full Graph Loader service integration."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            "kafka": {
                "bootstrap_servers": "localhost:9092",
                "topic": "tx_enriched",
                "group_id": "test-group",
                "auto_offset_reset": "earliest",
                "enable_auto_commit": False,
                "batch_size": 5,
                "batch_timeout_ms": 1000,
            },
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "password",
                "database": "fraudgraph",
                "batch_size": 10,
                "batch_timeout_ms": 1000,
                "max_connection_lifetime": 3600,
                "max_connection_pool_size": 50,
                "connection_acquisition_timeout": 60,
                "encrypted": False,
                "trust": "TRUST_ALL_CERTIFICATES",
                "retry_attempts": 3,
                "retry_delay_ms": 1000,
                "circuit_breaker": {
                    "failure_threshold": 5,
                    "recovery_timeout": 30,
                    "half_open_timeout": 5,
                },
            },
            "edge_processing": {
                "enabled_edge_types": ["CARD_IP", "CARD_MERCHANT"],
                "time_bucket_size": 60,
                "max_txn_ids": 100,
            },
            "edge_types": {
                "CARD_IP": {
                    "src_field": "card_id",
                    "dst_field": "ip_address",
                    "src_prefix": "card:",
                    "dst_prefix": "ip:",
                    "direction": "outgoing",
                    "properties": ["amount", "is_success"],
                },
                "CARD_MERCHANT": {
                    "src_field": "card_id",
                    "dst_field": "merchant_id",
                    "src_prefix": "card:",
                    "dst_prefix": "merchant:",
                    "direction": "outgoing",
                    "properties": ["amount", "currency"],
                },
            },
            "performance": {
                "target_edges_per_sec": 1000,
                "backpressure_threshold_ms": 100,
            },
            "monitoring": {"metrics_interval": 1},
        }

    @pytest.fixture
    def sample_transactions(self):
        """Sample transaction data for testing."""
        return [
            {
                "transaction_id": "tx_001",
                "card_id": "card_123",
                "ip_address": "192.168.1.1",
                "merchant_id": "merchant_456",
                "amount": 100.50,
                "currency": "USD",
                "is_success": True,
                "timestamp": int(time.time()),
            },
            {
                "transaction_id": "tx_002",
                "card_id": "card_123",
                "ip_address": "192.168.1.2",
                "merchant_id": "merchant_789",
                "amount": 250.00,
                "currency": "USD",
                "is_success": True,
                "timestamp": int(time.time()),
            },
            {
                "transaction_id": "tx_003",
                "card_id": "card_456",
                "ip_address": "192.168.1.1",
                "merchant_id": "merchant_456",
                "amount": 75.25,
                "currency": "EUR",
                "is_success": False,
                "timestamp": int(time.time()),
            },
        ]

    @pytest.fixture
    def service(self, mock_config):
        """Create Graph Loader service with mocked config."""
        with patch("apps.graph_loader.main.config", mock_config):
            with patch("apps.graph_loader.main.service_status", {}):
                with patch("apps.graph_loader.main.running", True):
                    return GraphLoaderService()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.running is True
        assert service.edge_builder is not None
        assert service.edge_aggregator is not None
        assert service.neo4j_writer is not None
        assert service.transactions_processed == 0
        assert service.edges_created == 0

    def test_process_transaction_batch_success(self, service, sample_transactions):
        """Test successful transaction batch processing."""
        # Mock Neo4j writer
        service.neo4j_writer.write_edges_batch = Mock(return_value=True)

        result = service._process_transaction_batch(sample_transactions)

        assert result is True
        assert service.transactions_processed == 3
        assert service.edges_created > 0  # Should create edges
        assert service.batches_written == 1

        # Verify Neo4j writer was called
        service.neo4j_writer.write_edges_batch.assert_called_once()

    def test_process_transaction_batch_empty(self, service):
        """Test processing empty transaction batch."""
        result = service._process_transaction_batch([])

        assert result is True
        assert service.transactions_processed == 0
        assert service.edges_created == 0

    def test_process_transaction_batch_no_edges(self, service):
        """Test processing transactions that generate no edges."""
        # Transactions missing required fields
        invalid_transactions = [
            {"transaction_id": "tx_001"},  # Missing card_id, ip_address, etc.
            {"transaction_id": "tx_002", "card_id": "card_123"},  # Missing other fields
        ]

        result = service._process_transaction_batch(invalid_transactions)

        assert result is True
        # When no edges are created, transaction count is not updated (correct behavior)
        assert service.transactions_processed == 0
        assert service.edges_created == 0  # No valid edges created

    def test_process_transaction_batch_neo4j_failure(
        self, service, sample_transactions
    ):
        """Test transaction processing with Neo4j write failure."""
        # Mock Neo4j writer to fail
        service.neo4j_writer.write_edges_batch = Mock(return_value=False)

        result = service._process_transaction_batch(sample_transactions)

        assert result is False
        # Metrics should still be updated for processing attempt
        assert service.transactions_processed == 0  # Not updated on failure

    def test_process_transaction_batch_exception(self, service, sample_transactions):
        """Test transaction processing with exception."""
        # Mock edge builder to raise exception
        service.edge_builder.build_edges = Mock(
            side_effect=Exception("Edge building failed")
        )

        result = service._process_transaction_batch(sample_transactions)

        assert result is False

    def test_get_health_status_healthy(self, service):
        """Test health status when service is healthy."""
        # Mock healthy Neo4j
        service.neo4j_writer.health_check = Mock(return_value={"status": "healthy"})
        service.neo4j_writer.get_performance_stats = Mock(
            return_value={
                "circuit_breaker_state": "closed",
                "avg_write_time_ms": 25.0,
                "p95_write_time_ms": 45.0,
            }
        )

        health = service.get_health_status()

        assert health["status"] == "healthy"
        assert "uptime_seconds" in health
        assert "neo4j" in health
        assert "performance" in health
        assert "config" in health

    def test_get_health_status_unhealthy_neo4j(self, service):
        """Test health status when Neo4j is unhealthy."""
        # Mock unhealthy Neo4j
        service.neo4j_writer.health_check = Mock(return_value={"status": "unhealthy"})
        service.neo4j_writer.get_performance_stats = Mock(
            return_value={"circuit_breaker_state": "closed"}
        )

        health = service.get_health_status()

        assert health["status"] == "unhealthy"

    def test_get_health_status_degraded_circuit_open(self, service):
        """Test health status when circuit breaker is open."""
        # Mock healthy Neo4j but open circuit breaker
        service.neo4j_writer.health_check = Mock(return_value={"status": "healthy"})
        service.neo4j_writer.get_performance_stats = Mock(
            return_value={"circuit_breaker_state": "open"}
        )

        health = service.get_health_status()

        assert health["status"] == "degraded"

    def test_get_health_status_exception(self, service):
        """Test health status with exception."""
        # Mock Neo4j to raise exception
        service.neo4j_writer.health_check = Mock(
            side_effect=Exception("Health check failed")
        )

        health = service.get_health_status()

        assert health["status"] == "error"
        assert "error" in health


class TestEdgeProcessingIntegration:
    """Test edge processing pipeline integration."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for edge processing."""
        return {
            "edge_processing": {
                "enabled_edge_types": ["CARD_IP", "CARD_MERCHANT"],
                "time_bucket_size": 60,
                "max_txn_ids": 100,
            },
            "edge_types": {
                "CARD_IP": {
                    "src_field": "card_id",
                    "dst_field": "ip_address",
                    "src_prefix": "card:",
                    "dst_prefix": "ip:",
                    "direction": "outgoing",
                    "properties": ["amount", "is_success"],
                },
                "CARD_MERCHANT": {
                    "src_field": "card_id",
                    "dst_field": "merchant_id",
                    "src_prefix": "card:",
                    "dst_prefix": "merchant:",
                    "direction": "outgoing",
                    "properties": ["amount", "currency"],
                },
            },
        }

    @pytest.fixture
    def edge_builder(self, mock_config):
        """Create edge builder with mocked config."""
        with patch("apps.graph_loader.edge_builder.edge_builder.config", mock_config):
            with patch(
                "apps.graph_loader.edge_builder.edge_builder.get_enabled_edge_types",
                return_value=["CARD_IP", "CARD_MERCHANT"],
            ):
                with patch(
                    "apps.graph_loader.edge_builder.edge_builder.get_edge_config"
                ) as mock_get_config:
                    mock_get_config.side_effect = lambda edge_type: mock_config[
                        "edge_types"
                    ].get(edge_type)
                    return EdgeBuilder()

    @pytest.fixture
    def edge_aggregator(self, mock_config):
        """Create edge aggregator with mocked config."""
        with patch("apps.graph_loader.edge_builder.edge_builder.config", mock_config):
            return EdgeAggregator()

    def test_edge_processing_pipeline(self, edge_builder, edge_aggregator):
        """Test complete edge processing pipeline."""
        # Sample transaction
        transactions = [
            {
                "transaction_id": "tx_001",
                "card_id": "card_123",
                "ip_address": "192.168.1.1",
                "merchant_id": "merchant_456",
                "amount": 100.50,
                "currency": "USD",
                "is_success": True,
                "timestamp": 1234567890,
            }
        ]

        # Build edges
        edges = edge_builder.build_edges(transactions)

        # Should create 2 edges: CARD_IP and CARD_MERCHANT
        assert len(edges) == 2

        edge_types = [edge.edge_type for edge in edges]
        assert "CARD_IP" in edge_types
        assert "CARD_MERCHANT" in edge_types

        # Aggregate edges
        aggregated_edges = edge_aggregator.aggregate_edges(edges)

        assert len(aggregated_edges) == 2

        # Format for Neo4j
        neo4j_edges = edge_aggregator.format_for_neo4j(aggregated_edges)

        assert len(neo4j_edges) == 2

        # Verify edge structure
        for edge in neo4j_edges:
            assert "edge_id" in edge
            assert "edge_type" in edge
            assert "src" in edge
            assert "dst" in edge
            assert "first_seen" in edge
            assert "last_seen" in edge
            assert "count" in edge
            assert "txn_ids" in edge

    def test_edge_aggregation_duplicate_edges(self, edge_builder, edge_aggregator):
        """Test edge aggregation with duplicate edges."""
        # Create transactions that will generate duplicate edges
        transactions = [
            {
                "transaction_id": "tx_001",
                "card_id": "card_123",
                "ip_address": "192.168.1.1",
                "merchant_id": "merchant_456",
                "amount": 100.50,
                "timestamp": 1234567890,
            },
            {
                "transaction_id": "tx_002",
                "card_id": "card_123",
                "ip_address": "192.168.1.1",  # Same card-IP combination
                "merchant_id": "merchant_456",  # Same card-merchant combination
                "amount": 200.00,
                "timestamp": 1234567890,  # Same time bucket
            },
        ]

        # Build edges
        edges = edge_builder.build_edges(transactions)

        # Should create 4 edges total (2 per transaction)
        assert len(edges) == 4

        # Aggregate edges
        aggregated_edges = edge_aggregator.aggregate_edges(edges)

        # Should aggregate to 2 unique edges
        assert len(aggregated_edges) == 2

        # Each aggregated edge should have count = 2
        for edge in aggregated_edges:
            assert edge["count"] == 2
            assert len(edge["txn_ids"]) == 2

    def test_edge_processing_missing_fields(self, edge_builder, edge_aggregator):
        """Test edge processing with missing required fields."""
        transactions = [
            {
                "transaction_id": "tx_001",
                "card_id": "card_123",
                # Missing ip_address and merchant_id
                "amount": 100.50,
                "timestamp": 1234567890,
            },
            {
                "transaction_id": "tx_002",
                "card_id": "card_456",
                "ip_address": "192.168.1.1",
                # Missing merchant_id
                "amount": 200.00,
                "timestamp": 1234567890,
            },
        ]

        # Build edges
        edges = edge_builder.build_edges(transactions)

        # Should only create 1 edge (CARD_IP from tx_002)
        assert len(edges) == 1
        assert edges[0].edge_type == "CARD_IP"
        assert edges[0].src == "card:card_456"
        assert edges[0].dst == "ip:192.168.1.1"


if __name__ == "__main__":
    pytest.main([__file__])
