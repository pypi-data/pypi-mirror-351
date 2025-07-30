"""
Unit tests for the EdgeConfigurableWindow class.
Tests edge tracking functionality for merchants and devices.
"""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Mock prometheus_client before importing window module
sys.modules["prometheus_client"] = MagicMock()

# Create Gauge, Counter mocks
prom_mock = sys.modules["prometheus_client"]
prom_mock.Gauge = MagicMock()
prom_mock.Gauge.return_value.labels.return_value.set = MagicMock()
prom_mock.Counter = MagicMock()
prom_mock.Counter.return_value.labels.return_value.inc = MagicMock()
prom_mock.REGISTRY = MagicMock()
prom_mock.REGISTRY.get_sample_value = MagicMock()

# Now import the modules that depend on prometheus_client
from apps.feature_builder.sliding_window.edge_window import EdgeConfigurableWindow


class TestEdgeWindow(unittest.TestCase):
    """Test suite for the EdgeConfigurableWindow class"""

    def setUp(self):
        # Initialize test windows
        self.merchant_window = EdgeConfigurableWindow(
            window_size=60,
            max_size=5,
            window_type="test_merchant",
            edge_type="merchant",
        )
        self.device_window = EdgeConfigurableWindow(
            window_size=60, max_size=5, window_type="test_device", edge_type="device"
        )

    def test_basic_functionality(self):
        """Test basic operations of EdgeConfigurableWindow"""
        current_time = int(time.time())

        # Add merchant edges for a card
        self.merchant_window.add(current_time, "merchant1", entity_id="card1")
        self.merchant_window.add(current_time, "merchant2", entity_id="card1")
        self.merchant_window.add(
            current_time, "merchant1", entity_id="card1"
        )  # Duplicate merchant

        # Check counts
        self.assertEqual(self.merchant_window.count(entity_id="card1"), 3)
        self.assertEqual(self.merchant_window.count_unique_edges(entity_id="card1"), 2)

        # Verify unique edges
        unique_merchants = self.merchant_window.get_unique_edges()
        self.assertEqual(len(unique_merchants), 2)
        self.assertIn("merchant1", unique_merchants)
        self.assertIn("merchant2", unique_merchants)

    def test_window_cleaning(self):
        """Test that clean_expired removes items outside window"""
        current_time = int(time.time())

        # Add items with timestamps across window boundary
        for i in range(5):
            self.merchant_window.add(
                current_time - 30 - i * 10, f"merchant{i}", entity_id="card1"
            )  # Some in, some out of 60s window

        # Initial count should be 5
        self.assertEqual(self.merchant_window.count(entity_id="card1"), 5)

        # Explicitly call clean_expired with the card1 entity_id
        # to ensure the entity count is properly updated
        removed = self.merchant_window.clean_expired(current_time, entity_id="card1")

        # Should have removed items outside 60s window
        self.assertEqual(removed, 0)  # All within 60s

        # Test with a more aggressive time boundary
        # Note: We need to pass entity_id to ensure entity counts are updated correctly
        removed = self.merchant_window.clean_expired(
            current_time + 40, entity_id="card1"
        )  # Make all timestamps expire

        # The implementation removes all 5 timestamps since our earliest is at current_time - 30,
        # and when we add 40 to current_time, the window boundary becomes current_time + 40 - 60 = current_time - 20,
        # which is later than all our timestamps
        self.assertEqual(removed, 5)  # All timestamps are removed

        # After all timestamps are removed, the entity count should be 0
        self.assertEqual(self.merchant_window.count(entity_id="card1"), 0)

        # Check that the window is now empty
        self.assertEqual(len(self.merchant_window.timestamps), 0)

    def test_max_size_enforcement(self):
        """Test that windows enforce their maximum size limit"""
        current_time = int(time.time())

        # Add more items than max_size
        for i in range(10):
            self.device_window.add(current_time + i, f"device{i}", entity_id="card1")

        # Check window size is capped at max_size
        self.assertEqual(len(self.device_window.timestamps), 5)

        # Check that only the most recent 5 items are kept
        self.assertEqual(min(self.device_window.timestamps), current_time + 5)
        self.assertEqual(max(self.device_window.timestamps), current_time + 9)

        # Check unique edges count
        unique_devices = self.device_window.get_unique_edges()
        self.assertEqual(len(unique_devices), 5)

        # Verify only most recent device IDs remain
        for i in range(5, 10):
            self.assertIn(f"device{i}", unique_devices)

    def test_dynamic_config_update(self):
        """Test dynamic reconfiguration of window size"""
        current_time = int(time.time())

        # Add items with various timestamps
        for i in range(5):
            self.merchant_window.add(
                current_time - i * 15, f"merchant{i}", entity_id="card1"
            )  # 0, 15, 30, 45, 60 seconds ago

        # Should have 5 items all within 60s window
        self.assertEqual(len(self.merchant_window.timestamps), 5)

        # Update window size to 30s
        with patch("time.time", return_value=current_time):
            self.merchant_window.update_config(window_size=30)

        # Should now have only items within 30s
        self.assertLessEqual(
            len(self.merchant_window.timestamps), 3
        )  # 0, 15, 30 seconds ago

        # Check unique edges count after window shrinking
        unique_merchants = self.merchant_window.get_unique_edges()
        self.assertLessEqual(len(unique_merchants), 3)

        # Verify all remaining items are within new window
        for ts in self.merchant_window.timestamps:
            self.assertGreaterEqual(ts, current_time - 30)

    def test_hot_reload(self):
        """Test that window config updates work mid-operation"""
        current_time = int(time.time())

        # Add some items to 60s window
        for i in range(5):
            self.device_window.add(
                current_time - i * 10, f"device{i}", entity_id="card1"
            )  # 0, 10, 20, 30, 40 seconds ago

        # Should have 5 items
        self.assertEqual(len(self.device_window.timestamps), 5)

        # Simulate 10s passing and update window to 20s
        new_time = current_time + 10  # Now items are 10, 20, 30, 40, 50 seconds ago

        # Use patch to ensure time.time() returns our controlled value during update_config
        with patch("time.time", return_value=new_time):
            self.device_window.update_config(window_size=20)

        # Only items less than 20s old should remain (10s and 20s ago from new_time)
        self.assertLessEqual(len(self.device_window.timestamps), 2)

        # Add a new device
        self.device_window.add(new_time, "new_device", entity_id="card1")

        # Should still respect new window size
        for ts in self.device_window.timestamps:
            self.assertGreaterEqual(ts, new_time - 20)

        # Check unique edges count after window changes
        unique_devices = self.device_window.get_unique_edges()
        self.assertIn("new_device", unique_devices)

    def test_multiple_entities(self):
        """Test tracking multiple entities in the same window"""
        current_time = int(time.time())

        # Add merchants for different cards
        self.merchant_window.add(current_time, "merchant1", entity_id="card1")
        self.merchant_window.add(current_time, "merchant2", entity_id="card1")
        self.merchant_window.add(current_time, "merchant1", entity_id="card2")
        self.merchant_window.add(current_time, "merchant3", entity_id="card2")

        # Check entity-specific counts
        self.assertEqual(self.merchant_window.count(entity_id="card1"), 2)
        self.assertEqual(self.merchant_window.count(entity_id="card2"), 2)

        # Check unique merchant counts per card
        self.assertEqual(self.merchant_window.count_unique_edges(entity_id="card1"), 2)
        self.assertEqual(self.merchant_window.count_unique_edges(entity_id="card2"), 2)

        # Total unique merchants across all cards
        self.assertEqual(len(self.merchant_window.get_unique_edges()), 3)


if __name__ == "__main__":
    unittest.main()
