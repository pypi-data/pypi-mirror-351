"""
Unit tests for Kafka consumer component.

Tests message processing, back-pressure handling, and offset management.
"""

import json
import time
from unittest.mock import Mock, patch

import pytest
from confluent_kafka import KafkaException

from apps.graph_loader.kafka_consumer.consumer import GraphLoaderKafkaConsumer


class TestGraphLoaderKafkaConsumer:
    """Test Kafka consumer functionality."""

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
                "batch_size": 10,
                "batch_timeout_ms": 1000,
            },
            "performance": {"backpressure_threshold_ms": 100},
        }

    @pytest.fixture
    def mock_message_handler(self):
        """Mock message handler for testing."""
        return Mock(return_value=True)

    @pytest.fixture
    def consumer(self, mock_config, mock_message_handler):
        """Create consumer with mocked config."""
        with patch("apps.graph_loader.kafka_consumer.consumer.config", mock_config):
            with patch("apps.graph_loader.kafka_consumer.consumer.running", True):
                return GraphLoaderKafkaConsumer(mock_message_handler)

    def test_consumer_initialization(self, consumer, mock_message_handler):
        """Test consumer initializes correctly."""
        assert consumer.message_handler == mock_message_handler
        assert consumer.running is True
        assert consumer.paused is False
        assert consumer.messages_processed == 0
        assert consumer.batches_processed == 0

    @patch("apps.graph_loader.kafka_consumer.consumer.Consumer")
    def test_create_consumer(self, mock_consumer_class, consumer):
        """Test Kafka consumer creation."""
        mock_consumer_instance = Mock()
        mock_consumer_class.return_value = mock_consumer_instance

        result = consumer._create_consumer()

        assert result == mock_consumer_instance
        mock_consumer_class.assert_called_once()

        # Check configuration passed to Consumer
        call_args = mock_consumer_class.call_args[0][0]
        assert call_args["bootstrap.servers"] == "localhost:9092"
        assert call_args["group.id"] == "sentr-graph-loader"  # Uses actual config value
        assert call_args["enable.auto.commit"] is False

    def test_parse_message_success(self, consumer):
        """Test successful message parsing."""
        # Mock Kafka message
        mock_message = Mock()
        mock_message.value.return_value = json.dumps(
            {"transaction_id": "tx_123", "card_id": "card_456", "amount": 100.0}
        ).encode("utf-8")
        mock_message.topic.return_value = "tx_enriched"
        mock_message.partition.return_value = 0
        mock_message.offset.return_value = 12345
        mock_message.timestamp.return_value = (1, 1234567890000)

        result = consumer._parse_message(mock_message)

        assert result is not None
        assert result["transaction_id"] == "tx_123"
        assert result["card_id"] == "card_456"
        assert result["amount"] == 100.0
        assert "_kafka_metadata" in result
        assert result["_kafka_metadata"]["topic"] == "tx_enriched"
        assert result["_kafka_metadata"]["offset"] == 12345

    def test_parse_message_null_value(self, consumer):
        """Test parsing message with null value."""
        mock_message = Mock()
        mock_message.value.return_value = None
        mock_message.offset.return_value = 12345

        result = consumer._parse_message(mock_message)

        assert result is None

    def test_parse_message_invalid_json(self, consumer):
        """Test parsing message with invalid JSON."""
        mock_message = Mock()
        mock_message.value.return_value = b"invalid json"
        mock_message.offset.return_value = 12345

        result = consumer._parse_message(mock_message)

        assert result is None

    def test_should_pause_for_backpressure_no_data(self, consumer):
        """Test back-pressure check with no processing times."""
        result = consumer._should_pause_for_backpressure()
        assert result is False

    def test_should_pause_for_backpressure_below_threshold(self, consumer):
        """Test back-pressure check below threshold."""
        # Add processing times below threshold (100ms = 0.1s)
        consumer.processing_times.extend([0.05, 0.06, 0.07])  # 50-70ms

        result = consumer._should_pause_for_backpressure()
        assert result is False

    def test_should_pause_for_backpressure_above_threshold(self, consumer):
        """Test back-pressure check above threshold."""
        # Add processing times above threshold (100ms = 0.1s)
        consumer.processing_times.extend([0.15, 0.16, 0.17])  # 150-170ms

        result = consumer._should_pause_for_backpressure()
        assert result is True

    def test_handle_backpressure_pause(self, consumer):
        """Test back-pressure handling - pause."""
        # Setup consumer with mock
        mock_consumer = Mock()
        consumer.consumer = mock_consumer

        # Add high processing times to trigger pause
        consumer.processing_times.extend([0.15, 0.16, 0.17])

        consumer._handle_backpressure()

        assert consumer.paused is True
        mock_consumer.pause.assert_called_once()

    def test_handle_backpressure_resume(self, consumer):
        """Test back-pressure handling - resume."""
        # Setup consumer with mock
        mock_consumer = Mock()
        consumer.consumer = mock_consumer
        consumer.paused = True
        consumer.pause_start_time = time.time() - 1

        # Add low processing times to trigger resume
        consumer.processing_times.extend([0.05, 0.06, 0.07])

        consumer._handle_backpressure()

        assert consumer.paused is False
        mock_consumer.resume.assert_called_once()

    def test_commit_offsets_throttled(self, consumer):
        """Test offset commit throttling."""
        mock_consumer = Mock()
        consumer.consumer = mock_consumer
        consumer.last_commit_time = time.time()  # Recent commit

        # Should not commit due to throttling
        consumer._commit_offsets()

        mock_consumer.commit.assert_not_called()

    def test_commit_offsets_forced(self, consumer):
        """Test forced offset commit."""
        mock_consumer = Mock()
        consumer.consumer = mock_consumer

        consumer._commit_offsets(force=True)

        mock_consumer.commit.assert_called_once_with(asynchronous=False)

    def test_commit_offsets_time_elapsed(self, consumer):
        """Test offset commit after time elapsed."""
        mock_consumer = Mock()
        consumer.consumer = mock_consumer
        consumer.last_commit_time = time.time() - 10  # 10 seconds ago

        consumer._commit_offsets()

        mock_consumer.commit.assert_called_once_with(asynchronous=False)

    def test_commit_offsets_kafka_exception(self, consumer):
        """Test offset commit with Kafka exception."""
        mock_consumer = Mock()
        mock_consumer.commit.side_effect = KafkaException("Commit failed")
        consumer.consumer = mock_consumer

        # Should not raise exception
        consumer._commit_offsets(force=True)

    def test_process_batch_success(self, consumer, mock_message_handler):
        """Test successful batch processing."""
        batch = [
            {"transaction_id": "tx_1", "amount": 100},
            {"transaction_id": "tx_2", "amount": 200},
        ]

        consumer._process_batch(batch)

        mock_message_handler.assert_called_once_with(batch)
        assert len(consumer.processing_times) == 1
        assert consumer.batches_processed == 1

    def test_process_batch_handler_failure(self, consumer, mock_message_handler):
        """Test batch processing with handler failure."""
        mock_message_handler.return_value = False

        batch = [{"transaction_id": "tx_1"}]

        consumer._process_batch(batch)

        mock_message_handler.assert_called_once_with(batch)
        # Should still track processing time
        assert len(consumer.processing_times) == 1

    def test_process_batch_handler_exception(self, consumer, mock_message_handler):
        """Test batch processing with handler exception."""
        mock_message_handler.side_effect = Exception("Handler error")

        batch = [{"transaction_id": "tx_1"}]

        # Should not raise exception
        consumer._process_batch(batch)

        assert len(consumer.processing_times) == 1

    def test_process_batch_empty(self, consumer, mock_message_handler):
        """Test processing empty batch."""
        consumer._process_batch([])

        mock_message_handler.assert_not_called()

    def test_stop(self, consumer):
        """Test stopping consumer."""
        consumer.stop()

        assert consumer.running is False

    @patch("apps.graph_loader.kafka_consumer.consumer.Consumer")
    def test_shutdown(self, mock_consumer_class, consumer):
        """Test consumer shutdown."""
        mock_consumer_instance = Mock()
        consumer.consumer = mock_consumer_instance

        consumer._shutdown()

        mock_consumer_instance.commit.assert_called_once_with(asynchronous=False)
        mock_consumer_instance.close.assert_called_once()

    @patch("apps.graph_loader.kafka_consumer.consumer.Consumer")
    def test_shutdown_commit_exception(self, mock_consumer_class, consumer):
        """Test consumer shutdown with commit exception."""
        mock_consumer_instance = Mock()
        mock_consumer_instance.commit.side_effect = KafkaException("Commit failed")
        consumer.consumer = mock_consumer_instance

        # Should not raise exception
        consumer._shutdown()

        # Close should still be called even if commit fails
        mock_consumer_instance.close.assert_called_once()

    def test_log_metrics_no_time_elapsed(self, consumer):
        """Test metrics logging with no time elapsed."""
        consumer.last_metrics_time = time.time()

        # Should not log metrics
        with patch("apps.graph_loader.kafka_consumer.consumer.logger") as mock_logger:
            consumer._log_metrics()
            mock_logger.info.assert_not_called()

    def test_log_metrics_time_elapsed(self, consumer):
        """Test metrics logging after time elapsed."""
        consumer.last_metrics_time = time.time() - 35  # 35 seconds ago
        consumer.messages_processed = 100
        consumer.batches_processed = 10
        consumer.processing_times.extend([0.05, 0.06, 0.07])

        with patch("apps.graph_loader.kafka_consumer.consumer.logger") as mock_logger:
            consumer._log_metrics()
            mock_logger.info.assert_called_once()

            # Check metrics were reset
            assert consumer.messages_processed == 0
            assert consumer.batches_processed == 0


if __name__ == "__main__":
    pytest.main([__file__])
