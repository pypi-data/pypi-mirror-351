"""
Integration test for feature builder services with memory bounds and metrics.
This test simulates real transaction processing and verifies all components work together.
"""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Redis module before importing loader
redis_mock = MagicMock()
sys.modules["redis"] = redis_mock


# Mock RedisPipeline
class MockRedisPipeline:
    def __init__(self, client):
        self.operation_count = 0
        self.operations = []
        self.client = client

    def hmset(self, key, values):
        self.operations.append(("hmset", key, values))
        self.operation_count += 1
        return self

    def expire(self, key, ttl):
        self.operations.append(("expire", key, ttl))
        self.operation_count += 1
        return self

    def execute(self):
        return ["OK"] * self.operation_count


sys.modules["apps.feature_builder.redis_sink"] = MagicMock()
sys.modules["apps.feature_builder.redis_sink"].RedisPipeline = MockRedisPipeline

import loader
from sliding_window.edge_window import EdgeConfigurableWindow
from sliding_window.window import make_window


class TestFeatureBuilderIntegration(unittest.TestCase):
    """Integration test suite for feature builder with real window handling."""

    def setUp(self):
        """Set up the test environment with real windows."""
        # Create real window instances
        self.card_id = "test_card_123"
        self.merchant_id = "test_merchant_456"
        self.device_id = "test_device_789"
        self.ip = "192.168.1.1"

        # Mock Redis for verification
        self.mock_redis = MagicMock()

        # Create a pipeline mock that stores operations for verification
        self.mock_pipeline = MagicMock()
        self.mock_pipeline.operation_count = 0
        self.pipeline_operations = []

        def mock_hmset(key, values):
            self.pipeline_operations.append(("hmset", key, values))
            self.mock_pipeline.operation_count += 1

        def mock_expire(key, ttl):
            self.pipeline_operations.append(("expire", key, ttl))
            self.mock_pipeline.operation_count += 1

        def mock_execute():
            return ["OK"] * self.mock_pipeline.operation_count

        self.mock_pipeline.hmset = mock_hmset
        self.mock_pipeline.expire = mock_expire
        self.mock_pipeline.execute = mock_execute

        # Save original feature windows and metrics
        self.original_windows = loader.feature_windows
        self.original_active_edges = loader.ACTIVE_EDGES

        # Initialize real windows for testing
        loader.feature_windows = {
            "declines": {},
            "unique_ips": {},
            "long_declines": {},
            "long_unique_ips": {},
            "unique_merchants": {},
            "unique_devices": {},
        }

        # Activate all edge types for testing
        loader.ACTIVE_EDGES = {"card_ip", "card_merchant", "card_device"}

        # Initialize the windows for our test card
        loader.feature_windows["declines"][self.card_id] = make_window(
            kind="decline", long=False
        )
        loader.feature_windows["unique_ips"][self.card_id] = make_window(
            kind="ip", long=False
        )
        loader.feature_windows["long_declines"][self.card_id] = make_window(
            kind="decline", long=True
        )
        loader.feature_windows["long_unique_ips"][self.card_id] = make_window(
            kind="ip", long=True
        )
        loader.feature_windows["unique_merchants"][self.card_id] = (
            EdgeConfigurableWindow(window_span=60, max_size=100)
        )
        loader.feature_windows["unique_devices"][self.card_id] = EdgeConfigurableWindow(
            window_span=60, max_size=100
        )

        # Mock metrics for verification
        self.mock_window_items = MagicMock()
        self.mock_edge_per_node = MagicMock()
        self.mock_feature_count = MagicMock()

        # Replace metrics with mocks
        self.original_window_items = loader.WINDOW_ITEMS
        self.original_edge_per_node = loader.EDGE_PER_NODE
        self.original_feature_count = loader.FEATURE_COUNT

        loader.WINDOW_ITEMS = self.mock_window_items
        loader.EDGE_PER_NODE = self.mock_edge_per_node
        loader.FEATURE_COUNT = self.mock_feature_count

        # Create metrics containers
        self.mock_window_items._metrics = {}
        self.mock_edge_per_node._metrics = {}

        # Mock the set method
        self.mock_window_items.labels.return_value.set = MagicMock()
        self.mock_edge_per_node.labels.return_value.set = MagicMock()
        self.mock_feature_count.labels.return_value.set = MagicMock()

    def tearDown(self):
        """Restore original configuration after tests."""
        loader.feature_windows = self.original_windows
        loader.ACTIVE_EDGES = self.original_active_edges
        loader.WINDOW_ITEMS = self.original_window_items
        loader.EDGE_PER_NODE = self.original_edge_per_node
        loader.FEATURE_COUNT = self.original_feature_count

    def _generate_transaction(self, success=True, ip=None, merchant=None, device=None):
        """Generate a test transaction for processing."""
        current_time = time.time()
        return {
            "card_id": self.card_id,
            "timestamp": current_time,
            "ip": ip or self.ip,
            "merchant_id": merchant or self.merchant_id,
            "device_id": device or self.device_id,
            "status": "declined" if not success else "approved",
        }

    def test_complete_transaction_processing(self):
        """Test complete transaction processing flow with features and metrics."""
        # Arrange
        # Generate multiple transactions
        transactions = [
            self._generate_transaction(success=False),  # Declined transaction
            self._generate_transaction(success=False, ip="192.168.1.2"),  # Different IP
            self._generate_transaction(
                success=False, merchant="another_merchant"
            ),  # Different merchant
            self._generate_transaction(
                success=False, device="another_device"
            ),  # Different device
            self._generate_transaction(
                success=True
            ),  # Successful transaction (not counted as decline)
        ]

        # Mock the RedisPipeline
        with patch("loader.RedisPipeline", return_value=self.mock_pipeline):
            # Act
            # Process all transactions
            for tx in transactions:
                loader.process_transaction(tx)

            # Clean windows (real implementation)
            loader.clean_expired_windows()

            # Update features in Redis
            result = loader.update_features_in_redis(self.mock_redis)

        # Assert
        # Check transaction processing results
        # Should have 4 declines
        self.assertEqual(loader.feature_windows["declines"][self.card_id].count(), 4)

        # Should have 2 unique IPs
        unique_ips = loader.feature_windows["unique_ips"][
            self.card_id
        ].get_unique_count()
        self.assertEqual(unique_ips, 2)

        # Should have 2 unique merchants
        merchant_edges = loader.feature_windows["unique_merchants"][
            self.card_id
        ].get_unique_edges()
        self.assertEqual(len(merchant_edges), 2)

        # Should have 2 unique devices
        device_edges = loader.feature_windows["unique_devices"][
            self.card_id
        ].get_unique_edges()
        self.assertEqual(len(device_edges), 2)

        # Verify Redis operations
        self.assertGreater(self.mock_pipeline.operation_count, 0)

        # Check for hmset operations
        hmset_ops = [op for op in self.pipeline_operations if op[0] == "hmset"]
        self.assertGreater(len(hmset_ops), 0)

        # Verify card features
        card_features = None
        for op in hmset_ops:
            if op[1] == f"card:{self.card_id}":
                card_features = op[2]
                break

        self.assertIsNotNone(card_features)
        self.assertEqual(card_features["fail_60s"], 4)
        self.assertEqual(card_features["uniq_ip_60s"], 2)
        self.assertEqual(card_features["uniq_merchant_60s"], 2)
        self.assertEqual(card_features["uniq_device_60s"], 2)

        # Verify metrics were updated
        self.mock_window_items.labels.assert_any_call(
            entity_id=self.card_id, window_type="decline_60s"
        )
        self.mock_edge_per_node.labels.assert_any_call(
            entity_id=self.card_id, edge_type="card_merchant"
        )

    def test_memory_monitoring_during_processing(self):
        """Test that memory monitoring runs during transaction processing."""
        # Arrange
        # Create a mock Redis client that simulates memory reporting
        mock_redis = MagicMock()
        mock_memory_info = {
            "used_memory": 262144000,  # 250MB
            "used_memory_peak": 314572800,  # 300MB
            "maxmemory": 524288000,  # 512MB
            "maxmemory_policy": "volatile-lfu",
        }
        mock_redis.info.side_effect = [
            {"evicted_keys": 0},  # Basic info
            mock_memory_info,  # Memory info
        ]

        # Mock metrics
        mock_memory_usage = MagicMock()
        mock_memory_limit = MagicMock()
        original_memory_usage = loader.REDIS_MEMORY_USAGE
        original_memory_limit = loader.REDIS_MEMORY_LIMIT
        loader.REDIS_MEMORY_USAGE = mock_memory_usage
        loader.REDIS_MEMORY_LIMIT = mock_memory_limit

        try:
            # Act
            # Call memory monitoring function
            loader.monitor_redis_memory(mock_redis)

            # Assert
            # Verify memory metrics were updated
            mock_memory_usage.set.assert_called_with(262144000)
            mock_memory_limit.set.assert_called_with(524288000)

            # Verify memory info was retrieved
            mock_redis.info.assert_any_call(section="memory")
        finally:
            # Restore original metrics
            loader.REDIS_MEMORY_USAGE = original_memory_usage
            loader.REDIS_MEMORY_LIMIT = original_memory_limit


if __name__ == "__main__":
    unittest.main()
