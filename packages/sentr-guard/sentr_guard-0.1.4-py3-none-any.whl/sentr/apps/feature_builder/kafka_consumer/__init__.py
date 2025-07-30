"""
Kafka consumer module with exactly-once semantics.
"""

from .consumer import FeatureConsumer, KafkaConsumerConfig

__all__ = ["FeatureConsumer", "KafkaConsumerConfig"]
