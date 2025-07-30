"""
Unit tests for Neo4j writer component.

Tests circuit breaker, retry logic, and batch writing functionality.
"""

import time
from unittest.mock import Mock, patch

import pytest
from neo4j.exceptions import ServiceUnavailable, TransientError

from apps.graph_loader.neo4j_writer.neo4j_driver import (
    CircuitBreaker,
    CircuitBreakerState,
    Neo4jBatchWriter,
)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_closed_initially(self):
        """Test circuit breaker starts in closed state."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitBreakerState.CLOSED
        assert not cb.is_open()

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        cb = CircuitBreaker(failure_threshold=3)

        # Simulate failures
        for _ in range(3):
            try:
                cb.call(lambda: exec('raise Exception("test error")'))
            except:
                pass

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.is_open()

    def test_circuit_breaker_prevents_calls_when_open(self):
        """Test circuit breaker prevents calls when open."""
        cb = CircuitBreaker(failure_threshold=1)

        # Cause failure to open circuit
        try:
            cb.call(lambda: exec('raise Exception("test error")'))
        except:
            pass

        # Should prevent subsequent calls
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(lambda: "success")

    def test_circuit_breaker_transitions_to_half_open(self):
        """Test circuit breaker transitions to half-open after recovery timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        # Cause failure
        try:
            cb.call(lambda: exec('raise Exception("test error")'))
        except:
            pass

        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        time.sleep(0.2)

        # Next call should transition to half-open
        try:
            cb.call(lambda: exec('raise Exception("test error")'))
        except:
            pass

        # Should have transitioned through half-open

    def test_circuit_breaker_closes_on_success(self):
        """Test circuit breaker closes on successful operation."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        # Cause failure
        try:
            cb.call(lambda: exec('raise Exception("test error")'))
        except:
            pass

        # Wait for recovery
        time.sleep(0.2)

        # Successful call should close circuit
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED


class TestNeo4jBatchWriter:
    """Test Neo4j batch writer functionality."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "password",
                "database": "fraudgraph",
                "batch_size": 100,
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
            }
        }

    @pytest.fixture
    def writer(self, mock_config):
        """Create Neo4j writer with mocked config."""
        with patch("apps.graph_loader.neo4j_writer.neo4j_driver.config", mock_config):
            return Neo4jBatchWriter()

    def test_writer_initialization(self, writer):
        """Test writer initializes correctly."""
        assert writer.driver is None
        assert writer.circuit_breaker.state == CircuitBreakerState.CLOSED
        assert writer.batch_size == 100
        assert writer.total_edges_written == 0

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_connect_success(self, mock_graph_db, writer):
        """Test successful connection to Neo4j."""
        # Mock driver and session
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()

        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        mock_session.run.return_value = mock_result
        mock_result.single.return_value = mock_record
        mock_record.__getitem__ = Mock(return_value=1)

        # Test connection
        writer.connect()

        assert writer.driver == mock_driver
        mock_graph_db.driver.assert_called_once()

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_connect_failure(self, mock_graph_db, writer):
        """Test connection failure handling."""
        mock_graph_db.driver.side_effect = Exception("Connection failed")

        with pytest.raises(Exception, match="Connection failed"):
            writer.connect()

    def test_write_edges_batch_empty(self, writer):
        """Test writing empty edge batch."""
        result = writer.write_edges_batch([])
        assert result is True

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_write_edges_batch_success(self, mock_graph_db, writer):
        """Test successful edge batch write."""
        # Setup mocks
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()

        writer.driver = mock_driver
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        mock_session.run.return_value = mock_result
        mock_result.consume.return_value = Mock()

        # Test data
        edges = [
            {
                "edge_id": "test123",
                "edge_type": "CARD_IP",
                "src": "card:123",
                "dst": "ip:192.168.1.1",
                "first_seen": 1234567890,
                "last_seen": 1234567890,
                "bucket_timestamp": 1234567800,
                "count": 1,
                "txn_ids": ["tx_123"],
            }
        ]

        # Test write
        result = writer.write_edges_batch(edges)

        assert result is True
        assert writer.total_edges_written == 1
        assert writer.total_batches_written == 1
        mock_session.run.assert_called()

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_write_edges_batch_with_retry(self, mock_graph_db, writer):
        """Test edge batch write with retry on transient error."""
        # Setup mocks
        mock_driver = Mock()
        mock_session = Mock()

        writer.driver = mock_driver
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)

        # First call fails, second succeeds
        mock_session.run.side_effect = [
            TransientError("Temporary failure"),
            Mock(consume=Mock(return_value=Mock())),
        ]

        edges = [{"edge_id": "test123", "src": "card:123", "dst": "ip:1.1.1.1"}]

        result = writer.write_edges_batch(edges)

        assert result is True
        assert mock_session.run.call_count == 2

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_write_edges_batch_circuit_breaker_opens(self, mock_graph_db, writer):
        """Test circuit breaker opens after repeated failures."""
        # Setup mocks
        mock_driver = Mock()
        mock_session = Mock()

        writer.driver = mock_driver
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        mock_session.run.side_effect = ServiceUnavailable("Service down")

        edges = [{"edge_id": "test123"}]

        # Cause enough failures to open circuit breaker
        for _ in range(6):  # More than failure threshold (5)
            result = writer.write_edges_batch(edges)
            assert result is False

        # Circuit breaker should be open
        assert writer.circuit_breaker.state == CircuitBreakerState.OPEN

    def test_get_performance_stats_empty(self, writer):
        """Test performance stats with no data."""
        stats = writer.get_performance_stats()

        expected = {
            "avg_write_time_ms": 0,
            "p95_write_time_ms": 0,
            "total_edges_written": 0,
            "total_batches_written": 0,
            "edges_per_second": 0,
            "circuit_breaker_state": "closed",
        }

        assert stats == expected

    def test_get_performance_stats_with_data(self, writer):
        """Test performance stats with write time data."""
        # Add some write times
        writer.write_times.extend([0.01, 0.02, 0.03, 0.04, 0.05])
        writer.total_edges_written = 100
        writer.total_batches_written = 5
        writer.last_write_time = time.time()

        stats = writer.get_performance_stats()

        assert stats["avg_write_time_ms"] == 30.0  # Average of 0.03 seconds
        assert stats["p95_write_time_ms"] == 50.0  # 95th percentile
        assert stats["total_edges_written"] == 100
        assert stats["total_batches_written"] == 5
        assert stats["circuit_breaker_state"] == "closed"

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_health_check_success(self, mock_graph_db, writer):
        """Test successful health check."""
        # Setup mocks
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()

        writer.driver = mock_driver
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        mock_session.run.return_value = mock_result
        mock_result.single.return_value = mock_record
        mock_record.__getitem__ = Mock(return_value=1)

        health = writer.health_check()

        assert health["status"] == "healthy"
        assert "response_time_ms" in health
        assert health["circuit_breaker_state"] == "closed"

    def test_health_check_no_driver(self, writer):
        """Test health check with no driver."""
        health = writer.health_check()

        assert health["status"] == "unhealthy"
        assert health["error"] == "Driver not connected"

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_health_check_failure(self, mock_graph_db, writer):
        """Test health check failure."""
        mock_driver = Mock()
        mock_session = Mock()

        writer.driver = mock_driver
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        mock_session.run.side_effect = Exception("Database error")

        health = writer.health_check()

        assert health["status"] == "unhealthy"
        assert "Database error" in health["error"]

    def test_close_driver(self, writer):
        """Test closing driver connection."""
        mock_driver = Mock()
        writer.driver = mock_driver

        writer.close()

        mock_driver.close.assert_called_once()

    def test_close_no_driver(self, writer):
        """Test closing when no driver exists."""
        # Should not raise exception
        writer.close()


if __name__ == "__main__":
    pytest.main([__file__])
