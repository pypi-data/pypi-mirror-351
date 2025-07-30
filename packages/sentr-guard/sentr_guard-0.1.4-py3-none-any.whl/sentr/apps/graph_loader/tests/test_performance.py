"""
Performance tests for Graph Loader service.

Tests throughput, latency, and scalability under load.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

import pytest

from apps.graph_loader.edge_builder.edge_builder import EdgeAggregator, EdgeBuilder
from apps.graph_loader.main import GraphLoaderService
from apps.graph_loader.neo4j_writer.neo4j_driver import Neo4jBatchWriter


class TestGraphLoaderPerformance:
    """Performance tests for Graph Loader components."""

    @pytest.fixture
    def sample_transactions(self):
        """Generate sample transactions for performance testing."""
        transactions = []
        for i in range(1000):
            transaction = {
                "transaction_id": f"tx_{i:06d}",
                "card_id": f"card_{i % 100:03d}",  # 100 unique cards
                "ip_address": f"192.168.{(i % 254) + 1}.{(i % 254) + 1}",  # Varied IPs
                "merchant_id": f"merchant_{i % 50:03d}",  # 50 unique merchants
                "device_id": f"device_{i % 200:03d}",  # 200 unique devices
                "amount": round(10.0 + (i % 1000), 2),
                "is_success": i % 10 != 0,  # 90% success rate
                "timestamp": 1700000000 + (i * 10),  # 10 second intervals
            }
            transactions.append(transaction)
        return transactions

    def test_edge_builder_throughput(self, sample_transactions):
        """Test EdgeBuilder can process transactions at target rate."""
        edge_builder = EdgeBuilder()

        # Warm up
        edge_builder.build_edges(sample_transactions[:10])

        # Measure throughput
        start_time = time.time()
        edges = edge_builder.build_edges(sample_transactions)
        end_time = time.time()

        elapsed = end_time - start_time
        edges_per_sec = len(edges) / elapsed

        print("EdgeBuilder Performance:")
        print(f"  Transactions: {len(sample_transactions)}")
        print(f"  Edges created: {len(edges)}")
        print(f"  Time elapsed: {elapsed:.3f}s")
        print(f"  Edges/sec: {edges_per_sec:.1f}")

        # Should be able to create edges at >2000/sec
        assert (
            edges_per_sec > 2000
        ), f"EdgeBuilder too slow: {edges_per_sec:.1f} edges/sec"

    def test_edge_aggregator_throughput(self, sample_transactions):
        """Test EdgeAggregator can process edges at target rate."""
        edge_builder = EdgeBuilder()
        aggregator = EdgeAggregator()

        # Build edges first
        edges = edge_builder.build_edges(sample_transactions)

        # Warm up
        aggregator.aggregate_edges(edges[:100])

        # Measure aggregation throughput
        start_time = time.time()
        aggregated = aggregator.aggregate_edges(edges)
        end_time = time.time()

        elapsed = end_time - start_time
        edges_per_sec = len(edges) / elapsed

        print("EdgeAggregator Performance:")
        print(f"  Input edges: {len(edges)}")
        print(f"  Aggregated edges: {len(aggregated)}")
        print(f"  Time elapsed: {elapsed:.3f}s")
        print(f"  Edges/sec: {edges_per_sec:.1f}")

        # Should be able to aggregate at >2000/sec
        assert (
            edges_per_sec > 2000
        ), f"EdgeAggregator too slow: {edges_per_sec:.1f} edges/sec"

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    def test_neo4j_writer_throughput(self, mock_graph_db, sample_transactions):
        """Test Neo4jBatchWriter can write edges at target rate."""
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

        # Create writer and connect
        writer = Neo4jBatchWriter()
        writer.connect()

        # Build and aggregate edges
        edge_builder = EdgeBuilder()
        aggregator = EdgeAggregator()
        edges = edge_builder.build_edges(sample_transactions)
        aggregated = aggregator.aggregate_edges(edges)
        neo4j_edges = aggregator.format_for_neo4j(aggregated)

        # Warm up
        writer.write_edges_batch(neo4j_edges[:10])

        # Measure write throughput
        start_time = time.time()
        success = writer.write_edges_batch(neo4j_edges)
        end_time = time.time()

        elapsed = end_time - start_time
        edges_per_sec = len(neo4j_edges) / elapsed

        print("Neo4jBatchWriter Performance:")
        print(f"  Edges written: {len(neo4j_edges)}")
        print(f"  Time elapsed: {elapsed:.3f}s")
        print(f"  Edges/sec: {edges_per_sec:.1f}")
        print(f"  Success: {success}")

        assert success is True
        # Should be able to write at >2000/sec (mocked, so should be very fast)
        assert (
            edges_per_sec > 2000
        ), f"Neo4jBatchWriter too slow: {edges_per_sec:.1f} edges/sec"

    def test_concurrent_processing(self, sample_transactions):
        """Test concurrent processing of transaction batches."""
        edge_builder = EdgeBuilder()
        aggregator = EdgeAggregator()

        # Split transactions into batches
        batch_size = 100
        batches = [
            sample_transactions[i : i + batch_size]
            for i in range(0, len(sample_transactions), batch_size)
        ]

        def process_batch(batch):
            """Process a single batch of transactions."""
            start_time = time.time()
            edges = edge_builder.build_edges(batch)
            aggregated = aggregator.aggregate_edges(edges)
            end_time = time.time()
            return {
                "batch_size": len(batch),
                "edges_created": len(edges),
                "aggregated_edges": len(aggregated),
                "processing_time": end_time - start_time,
            }

        # Process batches concurrently
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_batch, batch) for batch in batches]
            results = [future.result() for future in as_completed(futures)]
        end_time = time.time()

        # Calculate metrics
        total_transactions = sum(r["batch_size"] for r in results)
        total_edges = sum(r["edges_created"] for r in results)
        total_time = end_time - start_time

        edges_per_sec = total_edges / total_time
        transactions_per_sec = total_transactions / total_time

        print("Concurrent Processing Performance:")
        print(f"  Batches: {len(batches)}")
        print(f"  Total transactions: {total_transactions}")
        print(f"  Total edges: {total_edges}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Transactions/sec: {transactions_per_sec:.1f}")
        print(f"  Edges/sec: {edges_per_sec:.1f}")

        # Should achieve target throughput with concurrency
        assert (
            edges_per_sec > 2000
        ), f"Concurrent processing too slow: {edges_per_sec:.1f} edges/sec"

    def test_memory_usage_stability(self, sample_transactions):
        """Test that memory usage remains stable during processing."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        edge_builder = EdgeBuilder()
        aggregator = EdgeAggregator()

        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process transactions multiple times
        for iteration in range(10):
            edges = edge_builder.build_edges(sample_transactions)
            aggregated = aggregator.aggregate_edges(edges)

            # Force garbage collection
            import gc

            gc.collect()

            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = current_memory - initial_memory

            print(
                f"Iteration {iteration + 1}: Memory = {current_memory:.1f}MB (+{memory_growth:.1f}MB)"
            )

            # Memory growth should be reasonable (< 100MB)
            assert (
                memory_growth < 100
            ), f"Excessive memory growth: {memory_growth:.1f}MB"

    def test_latency_percentiles(self, sample_transactions):
        """Test processing latency percentiles."""
        edge_builder = EdgeBuilder()
        aggregator = EdgeAggregator()

        # Process small batches and measure latency
        batch_size = 50
        latencies = []

        for i in range(0, min(500, len(sample_transactions)), batch_size):
            batch = sample_transactions[i : i + batch_size]

            start_time = time.time()
            edges = edge_builder.build_edges(batch)
            aggregated = aggregator.aggregate_edges(edges)
            end_time = time.time()

            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate percentiles
        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]

        print(f"Latency Percentiles (batch size {batch_size}):")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")

        # P95 should be under target latency (50ms)
        assert p95 < 50, f"P95 latency too high: {p95:.2f}ms"

    @patch("apps.graph_loader.neo4j_writer.neo4j_driver.GraphDatabase")
    @patch("apps.graph_loader.kafka_consumer.consumer.Consumer")
    def test_end_to_end_throughput(
        self, mock_consumer_class, mock_graph_db, sample_transactions
    ):
        """Test end-to-end service throughput."""
        # Setup Neo4j mocks
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()

        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = Mock(return_value=None)
        mock_session.run.return_value = mock_result
        mock_result.consume.return_value = Mock()
        mock_result.single.return_value = Mock(__getitem__=Mock(return_value=1))

        # Setup Kafka consumer mock
        mock_consumer = Mock()
        mock_consumer_class.return_value = mock_consumer

        # Create service and connect Neo4j
        service = GraphLoaderService()
        service.neo4j_writer.driver = mock_driver  # Connect the mocked driver

        # Process batches and measure throughput
        batch_size = 200
        batches = [
            sample_transactions[i : i + batch_size]
            for i in range(0, len(sample_transactions), batch_size)
        ]

        total_edges = 0
        start_time = time.time()

        for batch in batches:
            success = service._process_transaction_batch(batch)
            assert success is True

            # Estimate edges created (4 edge types per transaction on average)
            total_edges += len(batch) * 4

        end_time = time.time()

        elapsed = end_time - start_time
        edges_per_sec = total_edges / elapsed

        print("End-to-End Performance:")
        print(f"  Transactions: {len(sample_transactions)}")
        print(f"  Estimated edges: {total_edges}")
        print(f"  Time elapsed: {elapsed:.3f}s")
        print(f"  Edges/sec: {edges_per_sec:.1f}")

        # Should meet target throughput
        assert (
            edges_per_sec > 2000
        ), f"End-to-end throughput too low: {edges_per_sec:.1f} edges/sec"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])
