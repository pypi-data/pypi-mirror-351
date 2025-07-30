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
from apps.feature_builder.sliding_window.window import (
    ConfigurableIPWindow,
    ConfigurableWindow,
    make_window,
)


class TestConfigurableWindow(unittest.TestCase):
    """Test suite for the ConfigurableWindow classes"""

    def setUp(self):
        # Initialize test windows
        self.short_window = ConfigurableWindow(
            window_size=60, max_size=5, window_type="test_short"
        )
        self.long_window = ConfigurableWindow(
            window_size=3600, max_size=10, window_type="test_long"
        )
        self.ip_window = ConfigurableIPWindow(
            window_size=60, max_size=5, window_type="test_ip"
        )

    def test_max_size_enforcement(self):
        """Test that windows enforce their maximum size limit"""
        # Add more items than max_size
        current_time = int(time.time())

        # Add 10 items to window with max_size=5
        for i in range(10):
            self.short_window.add(current_time + i)

        # Check window size is capped at max_size
        self.assertEqual(len(self.short_window.timestamps), 5)

        # Check that only the most recent 5 items are kept
        self.assertEqual(min(self.short_window.timestamps), current_time + 5)
        self.assertEqual(max(self.short_window.timestamps), current_time + 9)

    def test_clean_expired(self):
        """Test that clean_expired removes items outside window"""
        current_time = int(time.time())

        # Add items with timestamps across window boundary
        for i in range(10):
            self.short_window.add(
                current_time - 30 - i * 10
            )  # Some inside, some outside 60s window

        # Clean expired with current time
        self.short_window.clean_expired(current_time)

        # Check only items within window remain
        for ts in self.short_window.timestamps:
            self.assertGreater(ts, current_time - 60)

    def test_update_config(self):
        """Test dynamic reconfiguration of window size"""
        current_time = int(time.time())

        # Add items with various timestamps
        for i in range(5):
            self.short_window.add(
                current_time - i * 15
            )  # 0, 15, 30, 45, 60 seconds ago

        # Should have 5 items all within 60s window
        self.assertEqual(len(self.short_window.timestamps), 5)

        # Update window size to 30s
        with patch("time.time", return_value=current_time):
            self.short_window.update_config(window_size=30)

        # Should now have only items within 30s
        self.assertLessEqual(
            len(self.short_window.timestamps), 3
        )  # 0, 15, 30 seconds ago

        # Verify all remaining items are within new window
        for ts in self.short_window.timestamps:
            self.assertGreaterEqual(ts, current_time - 30)

    def test_entity_tracking(self):
        """Test that basic window counting works correctly"""
        current_time = int(time.time())

        # Add items (ConfigurableWindow doesn't track entities, just counts total)
        self.short_window.add(current_time)
        self.short_window.add(current_time)
        self.short_window.add(current_time)

        # Check total count (ConfigurableWindow doesn't filter by entity_id)
        self.assertEqual(self.short_window.count(), 3)

        # Test that entity_id parameter is ignored (doesn't crash)
        self.assertEqual(self.short_window.count(entity_id="entity1"), 3)
        self.assertEqual(self.short_window.count(entity_id="entity2"), 3)

    def test_ip_window_unique_tracking(self):
        """Test that IP window tracks unique IPs correctly"""
        current_time = int(time.time())

        # Add duplicate IPs
        self.ip_window.add(current_time, "1.1.1.1", entity_id="card1")
        self.ip_window.add(current_time, "1.1.1.1", entity_id="card1")  # Duplicate IP
        self.ip_window.add(current_time, "2.2.2.2", entity_id="card1")

        # Check unique IP count
        unique_ips = self.ip_window.get_unique_ips()
        self.assertEqual(len(unique_ips), 2)
        self.assertIn("1.1.1.1", unique_ips)
        self.assertIn("2.2.2.2", unique_ips)

    def test_hot_reload(self):
        """Test that window config updates work mid-operation"""
        current_time = int(time.time())

        # Add some items to 60s window
        for i in range(5):
            self.short_window.add(
                current_time - i * 10
            )  # 0, 10, 20, 30, 40 seconds ago

        # Should have 5 items
        self.assertEqual(len(self.short_window.timestamps), 5)

        # Simulate 10s passing and update window to 20s
        new_time = current_time + 10  # Now items are 10, 20, 30, 40, 50 seconds ago

        # Use patch to ensure time.time() returns our controlled value during update_config
        with patch("time.time", return_value=new_time):
            self.short_window.update_config(window_size=20)

        # Only items less than 20s old should remain (10s and 20s ago from new_time)
        self.assertLessEqual(len(self.short_window.timestamps), 2)

        # Add a new item
        self.short_window.add(new_time)

        # Should still respect new window size
        for ts in self.short_window.timestamps:
            self.assertGreaterEqual(ts, new_time - 20)

    def test_factory_function(self):
        """Test the make_window factory function"""
        # Create windows using factory
        short_decline = make_window(kind="decline", long=False)
        long_decline = make_window(kind="decline", long=True)
        short_ip = make_window(kind="ip", long=False)
        long_ip = make_window(kind="ip", long=True)

        # Verify correct types
        self.assertIsInstance(short_decline, ConfigurableWindow)
        self.assertIsInstance(long_decline, ConfigurableWindow)
        self.assertIsInstance(short_ip, ConfigurableIPWindow)
        self.assertIsInstance(long_ip, ConfigurableIPWindow)

        # Verify window sizes
        self.assertLess(short_decline.window_size, long_decline.window_size)
        self.assertLess(short_ip.window_size, long_ip.window_size)


if __name__ == "__main__":
    unittest.main()
