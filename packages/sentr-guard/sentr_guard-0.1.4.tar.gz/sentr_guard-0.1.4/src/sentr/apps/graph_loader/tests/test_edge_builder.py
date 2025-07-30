"""
Unit tests for Edge Builder.

Tests edge creation, aggregation, and formatting functionality.
"""

from unittest.mock import patch

from apps.graph_loader.edge_builder.edge_builder import (
    Edge,
    EdgeAggregator,
    EdgeBuilder,
)


class TestEdgeBuilder:
    """Test cases for EdgeBuilder class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.edge_builder = EdgeBuilder()

    def test_build_edges_single_transaction(self):
        """Test building edges from a single transaction."""
        transaction = {
            "transaction_id": "tx_123",
            "card_id": "card_456",
            "ip_address": "192.168.1.1",
            "merchant_id": "merchant_789",
            "device_id": "device_abc",
            "amount": 100.50,
            "is_success": True,
            "timestamp": 1700000000,
        }

        edges = self.edge_builder.build_edges([transaction])

        # Should create 4 edges (CARD_IP, CARD_MERCHANT, CARD_DEVICE, IP_MERCHANT)
        assert len(edges) == 4

        # Check edge types
        edge_types = {edge.edge_type for edge in edges}
        expected_types = {"CARD_IP", "CARD_MERCHANT", "CARD_DEVICE", "IP_MERCHANT"}
        assert edge_types == expected_types

        # Check CARD_IP edge specifically
        card_ip_edge = next(edge for edge in edges if edge.edge_type == "CARD_IP")
        assert card_ip_edge.src == "card:card_456"
        assert card_ip_edge.dst == "ip:192.168.1.1"
        assert card_ip_edge.txn_id == "tx_123"
        assert card_ip_edge.timestamp == 1700000000
        assert card_ip_edge.properties["amount"] == 100.50
        assert card_ip_edge.properties["is_success"] is True

    def test_build_edges_missing_fields(self):
        """Test handling of transactions with missing required fields."""
        transaction = {
            "transaction_id": "tx_123",
            "card_id": "card_456",
            # Missing ip_address
            "merchant_id": "merchant_789",
            "amount": 100.50,
            "timestamp": 1700000000,
        }

        edges = self.edge_builder.build_edges([transaction])

        # Should only create edges that have all required fields
        edge_types = {edge.edge_type for edge in edges}

        # CARD_IP should be missing due to missing ip_address
        assert "CARD_IP" not in edge_types
        assert "CARD_MERCHANT" in edge_types

    def test_edge_id_deterministic(self):
        """Test that edge IDs are deterministic for same inputs."""
        transaction = {
            "transaction_id": "tx_123",
            "card_id": "card_456",
            "ip_address": "192.168.1.1",
            "timestamp": 1700000000,
        }

        # Build edges twice
        edges1 = self.edge_builder.build_edges([transaction])
        edges2 = self.edge_builder.build_edges([transaction])

        # Find CARD_IP edges
        card_ip_edge1 = next(edge for edge in edges1 if edge.edge_type == "CARD_IP")
        card_ip_edge2 = next(edge for edge in edges2 if edge.edge_type == "CARD_IP")

        # Edge IDs should be identical
        assert card_ip_edge1.edge_id == card_ip_edge2.edge_id

    def test_time_bucketing(self):
        """Test that timestamps are properly bucketed."""
        # Use 60-second buckets (default)
        # 1700000000 is exactly on a bucket boundary
        transaction1 = {
            "transaction_id": "tx_1",
            "card_id": "card_456",
            "ip_address": "192.168.1.1",
            "timestamp": 1700000010,  # 10 seconds into bucket
        }

        transaction2 = {
            "transaction_id": "tx_2",
            "card_id": "card_456",
            "ip_address": "192.168.1.1",
            "timestamp": 1700000030,  # 30 seconds into same bucket
        }

        edges1 = self.edge_builder.build_edges([transaction1])
        edges2 = self.edge_builder.build_edges([transaction2])

        card_ip_edge1 = next(edge for edge in edges1 if edge.edge_type == "CARD_IP")
        card_ip_edge2 = next(edge for edge in edges2 if edge.edge_type == "CARD_IP")

        # Should have same bucket timestamp and edge_id
        assert card_ip_edge1.bucket_timestamp == card_ip_edge2.bucket_timestamp
        assert card_ip_edge1.edge_id == card_ip_edge2.edge_id

    def test_timestamp_extraction_fallback(self):
        """Test timestamp extraction with fallback to current time."""
        transaction = {
            "transaction_id": "tx_123",
            "card_id": "card_456",
            "ip_address": "192.168.1.1",
            # No timestamp field
        }

        with patch("time.time", return_value=1700000000):
            edges = self.edge_builder.build_edges([transaction])

        card_ip_edge = next(edge for edge in edges if edge.edge_type == "CARD_IP")
        assert card_ip_edge.timestamp == 1700000000

    def test_property_sanitization(self):
        """Test that properties are properly sanitized."""
        transaction = {
            "transaction_id": "tx_123",
            "card_id": "card_456",
            "ip_address": "192.168.1.1",
            "merchant_id": "merchant_456",
            "amount": 100.50,
            "is_success": True,
            "complex_data": {"nested": "value"},
            "list_data": [1, 2, 3, 4, 5],
            "timestamp": 1700000000,
        }

        edges = self.edge_builder.build_edges([transaction])
        card_ip_edge = next(edge for edge in edges if edge.edge_type == "CARD_IP")

        # Check property sanitization - only configured properties are extracted
        assert card_ip_edge.properties["amount"] == 100.50
        assert card_ip_edge.properties["is_success"] is True
        assert card_ip_edge.properties["merchant_id"] == "merchant_456"
        # Complex data is not in configured properties, so it shouldn't be included
        assert "complex_data" not in card_ip_edge.properties
        assert "list_data" not in card_ip_edge.properties


class TestEdgeAggregator:
    """Test cases for EdgeAggregator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.aggregator = EdgeAggregator()

    def test_aggregate_same_edge_id(self):
        """Test aggregation of edges with same edge_id."""
        edge1 = Edge(
            edge_type="CARD_IP",
            src="card:123",
            dst="ip:192.168.1.1",
            edge_id="edge_abc",
            timestamp=1700000000,
            bucket_timestamp=1700000000,
            properties={"amount": 100.0},
            txn_id="tx_1",
        )

        edge2 = Edge(
            edge_type="CARD_IP",
            src="card:123",
            dst="ip:192.168.1.1",
            edge_id="edge_abc",  # Same edge_id
            timestamp=1700000030,
            bucket_timestamp=1700000000,
            properties={"amount": 200.0},
            txn_id="tx_2",
        )

        aggregated = self.aggregator.aggregate_edges([edge1, edge2])

        assert len(aggregated) == 1

        agg_edge = aggregated[0]
        assert agg_edge["edge_id"] == "edge_abc"
        assert agg_edge["count"] == 2
        assert agg_edge["first_seen"] == 1700000000
        assert agg_edge["last_seen"] == 1700000030
        assert len(agg_edge["txn_ids"]) == 2
        assert "tx_1" in agg_edge["txn_ids"]
        assert "tx_2" in agg_edge["txn_ids"]

    def test_aggregate_different_edge_ids(self):
        """Test aggregation of edges with different edge_ids."""
        edge1 = Edge(
            edge_type="CARD_IP",
            src="card:123",
            dst="ip:192.168.1.1",
            edge_id="edge_abc",
            timestamp=1700000000,
            bucket_timestamp=1700000000,
            properties={},
            txn_id="tx_1",
        )

        edge2 = Edge(
            edge_type="CARD_IP",
            src="card:456",
            dst="ip:192.168.1.1",
            edge_id="edge_def",  # Different edge_id
            timestamp=1700000000,
            bucket_timestamp=1700000000,
            properties={},
            txn_id="tx_2",
        )

        aggregated = self.aggregator.aggregate_edges([edge1, edge2])

        assert len(aggregated) == 2

        edge_ids = {edge["edge_id"] for edge in aggregated}
        assert edge_ids == {"edge_abc", "edge_def"}

    def test_txn_id_limit(self):
        """Test that transaction ID list is limited."""
        # Create many edges with same edge_id
        edges = []
        for i in range(150):  # More than max_txn_ids (100)
            edge = Edge(
                edge_type="CARD_IP",
                src="card:123",
                dst="ip:192.168.1.1",
                edge_id="edge_abc",
                timestamp=1700000000 + i,
                bucket_timestamp=1700000000,
                properties={},
                txn_id=f"tx_{i}",
            )
            edges.append(edge)

        aggregated = self.aggregator.aggregate_edges(edges)

        assert len(aggregated) == 1
        agg_edge = aggregated[0]
        assert agg_edge["count"] == 150
        assert len(agg_edge["txn_ids"]) == 100  # Limited to max_txn_ids

    def test_format_for_neo4j(self):
        """Test formatting aggregated edges for Neo4j."""
        aggregated_edges = [
            {
                "edge_type": "CARD_IP",
                "src": "card:123",
                "dst": "ip:192.168.1.1",
                "edge_id": "edge_abc",
                "first_seen": 1700000000,
                "last_seen": 1700000030,
                "bucket_timestamp": 1700000000,
                "count": 2,
                "txn_ids": ["tx_1", "tx_2"],
                "properties": {"amount": 100.0, "is_success": True},
            }
        ]

        neo4j_edges = self.aggregator.format_for_neo4j(aggregated_edges)

        assert len(neo4j_edges) == 1

        neo4j_edge = neo4j_edges[0]
        assert neo4j_edge["edge_id"] == "edge_abc"
        assert neo4j_edge["edge_type"] == "CARD_IP"
        assert neo4j_edge["src"] == "card:123"
        assert neo4j_edge["dst"] == "ip:192.168.1.1"
        assert neo4j_edge["count"] == 2
        assert neo4j_edge["amount"] == 100.0  # Properties flattened
        assert neo4j_edge["is_success"] is True


class TestEdgeBuilderIntegration:
    """Integration tests for edge building workflow."""

    def test_full_workflow(self):
        """Test complete edge building and aggregation workflow."""
        edge_builder = EdgeBuilder()
        aggregator = EdgeAggregator()

        # Create transactions that should create duplicate edges
        transactions = [
            {
                "transaction_id": "tx_1",
                "card_id": "card_123",
                "ip_address": "192.168.1.1",
                "merchant_id": "merchant_456",
                "amount": 100.0,
                "is_success": True,
                "timestamp": 1700000000,
            },
            {
                "transaction_id": "tx_2",
                "card_id": "card_123",
                "ip_address": "192.168.1.1",  # Same card-ip combination
                "merchant_id": "merchant_456",  # Same card-merchant combination
                "amount": 200.0,
                "is_success": False,
                "timestamp": 1700000030,  # Same time bucket
            },
        ]

        # Build edges
        edges = edge_builder.build_edges(transactions)

        # Should create 6 edges total (3 types × 2 transactions)
        # But some will have same edge_id due to time bucketing
        assert len(edges) == 6

        # Aggregate edges
        aggregated = aggregator.aggregate_edges(edges)

        # Should have fewer aggregated edges due to deduplication
        assert len(aggregated) < len(edges)

        # Format for Neo4j
        neo4j_edges = aggregator.format_for_neo4j(aggregated)

        # Verify structure
        for edge in neo4j_edges:
            assert "edge_id" in edge
            assert "edge_type" in edge
            assert "src" in edge
            assert "dst" in edge
            assert "count" in edge
            assert "first_seen" in edge
            assert "last_seen" in edge
            assert isinstance(edge["txn_ids"], list)

        # Find CARD_IP edge and verify aggregation
        card_ip_edges = [e for e in neo4j_edges if e["edge_type"] == "CARD_IP"]
        assert len(card_ip_edges) == 1

        card_ip_edge = card_ip_edges[0]
        assert card_ip_edge["count"] == 2
        assert len(card_ip_edge["txn_ids"]) == 2
        assert card_ip_edge["first_seen"] == 1700000000
        assert card_ip_edge["last_seen"] == 1700000030
