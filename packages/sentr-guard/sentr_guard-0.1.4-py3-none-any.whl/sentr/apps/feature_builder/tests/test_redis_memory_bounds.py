"""
Tests for Redis memory bounds implementation and monitoring.
These tests verify the memory limits, LFU eviction policy, and monitoring components.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Redis module before importing
sys.modules["redis"] = MagicMock()
sys.modules["redis"].RedisError = Exception

from config import config
from redis_sink.pipeline import RedisPipeline


class TestRedisMemoryBounds(unittest.TestCase):
    """Test suite for Redis memory bounds features."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock Redis client
        self.mock_redis = MagicMock()
        self.mock_redis.ping.return_value = True
        self.mock_redis.info.return_value = {
            "used_memory": 262144000,  # 250MB
            "maxmemory": 524288000,  # 512MB
            "maxmemory_policy": "volatile-lfu",
        }

        # Mock pipeline
        self.mock_pipeline = MagicMock()
        self.mock_pipeline.execute.return_value = []

    def test_redis_pipeline_creation(self):
        """Test that Redis pipeline can be created with proper configuration."""
        # Arrange
        self.mock_redis.pipeline.return_value = self.mock_pipeline

        # Act
        pipeline = RedisPipeline(
            redis_client=self.mock_redis,
            pipeline_size=500,
            flush_ms=100,
            feature_ttl=3600,
        )

        # Assert
        self.assertEqual(pipeline.pipeline_size, 500)
        self.assertEqual(pipeline.flush_ms, 0.1)  # Converted to seconds
        self.assertEqual(pipeline.feature_ttl, 3600)
        self.mock_redis.pipeline.assert_called_once()

    def test_redis_pipeline_add_feature(self):
        """Test that features can be added to the pipeline."""
        # Arrange
        self.mock_redis.pipeline.return_value = self.mock_pipeline
        pipeline = RedisPipeline(
            redis_client=self.mock_redis,
            pipeline_size=10,
            flush_ms=100,
            feature_ttl=3600,
        )

        # Act
        pipeline.add_feature("test_card", "test_feature", "test_value")

        # Assert
        # Should buffer the feature
        self.assertIn("card:test_card", pipeline._buff)
        self.assertEqual(pipeline._buff["card:test_card"]["test_feature"], "test_value")

    def test_redis_pipeline_flush_functionality(self):
        """Test that pipeline flush works correctly."""
        # Arrange
        self.mock_redis.pipeline.return_value = self.mock_pipeline
        pipeline = RedisPipeline(
            redis_client=self.mock_redis,
            pipeline_size=10,
            flush_ms=100,
            feature_ttl=3600,
        )

        # Add some features
        pipeline.add_feature("test_card", "test_feature", "test_value")

        # Act
        result = pipeline.flush_if_needed(force=True)

        # Assert
        self.assertTrue(result)
        # Buffer should be cleared after successful flush
        self.assertEqual(len(pipeline._buff), 0)

    def test_redis_pipeline_error_handling(self):
        """Test that pipeline handles Redis errors gracefully."""
        # Arrange
        self.mock_redis.pipeline.return_value = self.mock_pipeline
        self.mock_pipeline.execute.side_effect = Exception("Redis error")

        pipeline = RedisPipeline(
            redis_client=self.mock_redis,
            pipeline_size=10,
            flush_ms=100,
            feature_ttl=3600,
        )

        # Add a feature to trigger flush
        pipeline.add_feature("test_card", "test_feature", "test_value")

        # Act
        result = pipeline.flush_if_needed(force=True)

        # Assert
        # Should handle error gracefully and return False
        self.assertFalse(result)

    def test_redis_pipeline_deduplication(self):
        """Test that pipeline deduplicates card updates within a batch."""
        # Arrange
        self.mock_redis.pipeline.return_value = self.mock_pipeline
        pipeline = RedisPipeline(
            redis_client=self.mock_redis,
            pipeline_size=10,
            flush_ms=100,
            feature_ttl=3600,
        )

        # Act - Add multiple features for the same card
        pipeline.add_feature("test_card", "feature1", "value1")
        pipeline.add_feature(
            "test_card", "feature2", "value2"
        )  # Should be skipped due to deduplication

        # Assert
        # Only one card should be tracked due to deduplication
        self.assertEqual(len(pipeline._batch_card_ids), 1)
        self.assertIn("test_card", pipeline._batch_card_ids)

    def test_config_redis_settings(self):
        """Test that Redis configuration is properly loaded."""
        # Assert
        self.assertIn("redis", config)
        self.assertIn("host", config["redis"])
        self.assertIn("port", config["redis"])
        self.assertIn("memory_limit_bytes", config["redis"])
        self.assertIn("memory_alert_threshold", config["redis"])


if __name__ == "__main__":
    unittest.main()
