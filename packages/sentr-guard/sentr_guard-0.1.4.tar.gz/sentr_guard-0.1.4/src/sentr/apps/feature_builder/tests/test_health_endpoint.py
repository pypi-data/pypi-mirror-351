"""
Tests for health endpoint with memory reporting.
These tests verify that the health endpoint properly reports Redis memory usage.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Redis module before importing
sys.modules["redis"] = MagicMock()

from health import HealthCheckHandler


class TestHealthEndpoint(unittest.TestCase):
    """Test suite for health endpoint memory reporting."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock Redis client
        self.mock_redis = MagicMock()
        self.mock_redis.ping.return_value = True
        self.mock_redis.info.return_value = {
            "used_memory": 262144000,  # 250MB
            "connected_clients": 5,
            "total_commands_processed": 50000,
        }

        # Mock Redis pipeline
        self.mock_pipeline = MagicMock()
        self.mock_pipeline.add_feature = MagicMock()
        self.mock_pipeline.flush_if_needed = MagicMock(return_value=True)

        # Mock Kafka consumer
        self.mock_consumer = MagicMock()
        self.mock_consumer.assignment.return_value = [MagicMock()]

        # Mock server
        self.mock_server = MagicMock()
        self.mock_server.redis_client = self.mock_redis
        self.mock_server.redis_pipeline = self.mock_pipeline
        self.mock_server.kafka_consumer = self.mock_consumer

        # Create handler without socket setup
        self.handler = HealthCheckHandler.__new__(HealthCheckHandler)
        self.handler.server = self.mock_server
        self.handler.send_response = MagicMock()
        self.handler.send_header = MagicMock()
        self.handler.end_headers = MagicMock()
        self.handler.wfile = MagicMock()

    def test_health_endpoint_basic_functionality(self):
        """Test that health endpoint responds correctly."""
        # Act
        self.handler._handle_health_check(
            self.mock_redis, self.mock_pipeline, self.mock_consumer
        )

        # Assert
        self.handler.send_response.assert_called_with(200)
        self.handler.send_header.assert_called_with("Content-type", "application/json")
        self.handler.end_headers.assert_called_once()
        self.handler.wfile.write.assert_called_once()

    def test_health_endpoint_redis_check(self):
        """Test that health endpoint checks Redis properly."""
        # Arrange
        health_data = {"checks": {}}

        # Act
        result = self.handler._check_redis_health(
            self.mock_redis, self.mock_pipeline, health_data
        )

        # Assert
        self.assertTrue(result)
        self.assertIn("redis", health_data["checks"])
        self.assertTrue(health_data["checks"]["redis"]["connected"])
        self.assertTrue(health_data["checks"]["redis"]["pipeline_healthy"])

    def test_health_endpoint_handles_redis_error(self):
        """Test that health endpoint handles Redis connection errors gracefully."""
        # Arrange
        # Mock Redis to raise an exception
        self.mock_redis.ping.side_effect = Exception("Redis connection failed")

        health_data = {"checks": {}}

        # Act
        result = self.handler._check_redis_health(
            self.mock_redis, self.mock_pipeline, health_data
        )

        # Assert
        self.assertFalse(result)
        self.assertIn("redis", health_data["checks"])
        self.assertFalse(health_data["checks"]["redis"]["connected"])
        self.assertIn("error", health_data["checks"]["redis"])

    def test_health_endpoint_kafka_check(self):
        """Test that health endpoint checks Kafka properly."""
        # Arrange
        health_data = {"checks": {}}

        # Act
        result = self.handler._check_kafka_health(self.mock_consumer, health_data)

        # Assert
        self.assertTrue(result)
        self.assertIn("kafka", health_data["checks"])
        self.assertTrue(health_data["checks"]["kafka"]["connected"])

    def test_health_endpoint_missing_components(self):
        """Test that health endpoint handles missing components gracefully."""
        # Arrange
        health_data = {"checks": {}}

        # Act - Test with None components
        redis_result = self.handler._check_redis_health(None, None, health_data)
        kafka_result = self.handler._check_kafka_health(None, health_data)

        # Assert
        self.assertFalse(redis_result)
        self.assertFalse(kafka_result)
        self.assertIn("redis", health_data["checks"])
        self.assertIn("kafka", health_data["checks"])
        self.assertFalse(health_data["checks"]["redis"]["connected"])
        self.assertFalse(health_data["checks"]["kafka"]["connected"])


if __name__ == "__main__":
    unittest.main()
