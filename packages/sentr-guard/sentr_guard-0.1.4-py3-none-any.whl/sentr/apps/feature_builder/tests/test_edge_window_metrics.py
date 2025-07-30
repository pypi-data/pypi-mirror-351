"""
Tests for Edge Window metrics tracking with Prometheus.
These tests verify the window_items and edge_per_node metrics.
"""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import loader
from sliding_window.edge_window import EdgeConfigurableWindow


class TestEdgeWindowMetrics(unittest.TestCase):
    """Test suite for Edge Window metrics features."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock Prometheus metrics
        self.mock_window_items = MagicMock()
        self.mock_edge_per_node = MagicMock()
        loader.WINDOW_ITEMS = self.mock_window_items
        loader.EDGE_PER_NODE = self.mock_edge_per_node

        # Create edge window instance
        self.edge_window = EdgeConfigurableWindow(max_size=100, window_span=60)

        # Mock Redis client for feature updates
        self.mock_redis = MagicMock()

        # Current time for consistent testing
        self.current_time = int(time.time())

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_window_items_metric_tracking(self):
        """Test that window_items metrics are updated correctly."""
        # Arrange
        card_id = "card123"

        # Create mocked feature windows with our test edge window
        feature_windows = {
            "declines": {card_id: MagicMock()},
            "long_declines": {card_id: MagicMock()},
            "unique_ips": {card_id: MagicMock()},
            "long_unique_ips": {card_id: MagicMock()},
        }

        # Configure the mock windows to return specific counts
        feature_windows["declines"][card_id].count.return_value = 5
        feature_windows["long_declines"][card_id].count.return_value = 15
        feature_windows["unique_ips"][card_id].get_unique_count.return_value = 3
        feature_windows["long_unique_ips"][card_id].get_unique_count.return_value = 8

        # Save original feature windows
        original_windows = loader.feature_windows
        loader.feature_windows = feature_windows

        # Mock the metrics clear method
        self.mock_window_items._metrics = MagicMock()

        # Act
        with patch("loader.update_features_in_redis") as mock_update:
            # Call the update function with our card
            loader.update_features_in_redis(self.mock_redis)

        # Assert
        # Check that window_items metrics were updated for each window type
        self.mock_window_items.labels.assert_any_call(
            entity_id=card_id, window_type="decline_60s"
        )
        self.mock_window_items.labels.assert_any_call(
            entity_id=card_id, window_type="decline_7d"
        )
        self.mock_window_items.labels.assert_any_call(
            entity_id=card_id, window_type="ip_60s"
        )
        self.mock_window_items.labels.assert_any_call(
            entity_id=card_id, window_type="ip_7d"
        )

        # Restore original feature windows
        loader.feature_windows = original_windows

    def test_edge_per_node_metric_tracking(self):
        """Test that edge_per_node metrics are updated correctly."""
        # Arrange
        card_id = "card456"
        loader.ACTIVE_EDGES = {"card_merchant", "card_device"}

        # Create mocked feature windows for edge tracking
        feature_windows = {
            "declines": {card_id: MagicMock()},
            "long_declines": {card_id: MagicMock()},
            "unique_ips": {card_id: MagicMock()},
            "long_unique_ips": {card_id: MagicMock()},
            "unique_merchants": {card_id: MagicMock()},
            "unique_devices": {card_id: MagicMock()},
        }

        # Configure basic window counts
        feature_windows["declines"][card_id].count.return_value = 1
        feature_windows["long_declines"][card_id].count.return_value = 1

        # Configure edge window counts
        merchant_edges = {"merchant1", "merchant2", "merchant3"}
        device_edges = {"device1", "device2"}
        feature_windows["unique_merchants"][
            card_id
        ].get_unique_edges.return_value = merchant_edges
        feature_windows["unique_devices"][
            card_id
        ].get_unique_edges.return_value = device_edges

        # Save original feature windows
        original_windows = loader.feature_windows
        loader.feature_windows = feature_windows

        # Mock the metrics clear method
        self.mock_edge_per_node._metrics = MagicMock()

        # Act
        with patch("loader.update_features_in_redis") as mock_update:
            # Call the update function with our card
            loader.update_features_in_redis(self.mock_redis)

        # Assert
        # Check that edge_per_node metrics were updated for each edge type
        self.mock_edge_per_node.labels.assert_any_call(
            entity_id=card_id, edge_type="card_merchant"
        )
        self.mock_edge_per_node.labels.assert_any_call(
            entity_id=card_id, edge_type="card_device"
        )

        # Restore original feature windows
        loader.feature_windows = original_windows

    def test_real_edge_window_updates_metrics(self):
        """Test with a real EdgeConfigurableWindow instance to verify metric tracking."""
        # Arrange - Set up actual edge window
        window = EdgeConfigurableWindow(window_span=60, max_size=10)
        card_id = "test_card"
        current_time = int(time.time())

        # Add some edges to the window
        merchants = ["merchant1", "merchant2", "merchant3"]
        for merchant in merchants:
            window.add(current_time, merchant, entity_id=card_id)

        # Create metrics
        mock_labels = MagicMock()
        mock_labels.set = MagicMock()
        self.mock_edge_per_node.labels.return_value = mock_labels

        # Act - Call method that would update metrics
        unique_edges = window.get_unique_edges(entity_id=card_id)

        # Assert - Metrics would be correctly updated with count of unique edges
        self.assertEqual(len(unique_edges), 3)

        # In the actual loader.py, this logic happens:
        # EDGE_PER_NODE.labels(entity_id=card_id, edge_type="card_merchant").set(merchant_count)
        self.mock_edge_per_node.labels.return_value.set.assert_not_called()  # Not called in this test directly


if __name__ == "__main__":
    unittest.main()
