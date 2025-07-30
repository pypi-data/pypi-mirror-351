"""
Configuration module for Sentr Graph Loader.

Handles configuration for Kafka consumption, Neo4j connections, and edge processing.
"""

import logging
import os
from typing import Any, Dict, List

import structlog

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger()

# Configuration dictionary
config = {
    "kafka": {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        "group_id": os.getenv("KAFKA_GROUP_ID", "sentr-graph-loader"),
        "auto_offset_reset": "earliest",
        "topic": os.getenv("KAFKA_TOPIC", "tx_enriched"),
        "batch_size": int(os.getenv("KAFKA_BATCH_SIZE", "200")),
        "batch_timeout_ms": int(os.getenv("KAFKA_BATCH_TIMEOUT_MS", "1000")),
        "enable_auto_commit": False,  # Manual commit for exactly-once
        "max_poll_records": int(os.getenv("KAFKA_MAX_POLL_RECORDS", "500")),
    },
    "neo4j": {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "password"),
        "database": os.getenv("NEO4J_DATABASE", "fraudgraph"),
        "max_connection_lifetime": int(
            os.getenv("NEO4J_MAX_CONNECTION_LIFETIME", "3600")
        ),
        "max_connection_pool_size": int(
            os.getenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "50")
        ),
        "connection_acquisition_timeout": int(
            os.getenv("NEO4J_CONNECTION_TIMEOUT", "60")
        ),
        "encrypted": os.getenv("NEO4J_ENCRYPTED", "false").lower() == "true",
        "trust": os.getenv("NEO4J_TRUST", "TRUST_ALL_CERTIFICATES"),
        # Performance settings
        "batch_size": int(os.getenv("NEO4J_BATCH_SIZE", "300")),
        "batch_timeout_ms": int(os.getenv("NEO4J_BATCH_TIMEOUT_MS", "100")),
        "retry_attempts": int(os.getenv("NEO4J_RETRY_ATTEMPTS", "3")),
        "retry_delay_ms": int(os.getenv("NEO4J_RETRY_DELAY_MS", "100")),
        "circuit_breaker": {
            "failure_threshold": int(os.getenv("NEO4J_CIRCUIT_FAILURE_THRESHOLD", "5")),
            "recovery_timeout": int(os.getenv("NEO4J_CIRCUIT_RECOVERY_TIMEOUT", "30")),
            "half_open_timeout": int(os.getenv("NEO4J_CIRCUIT_HALF_OPEN_TIMEOUT", "5")),
        },
    },
    "edge_processing": {
        # Time bucket size for edge aggregation (seconds)
        "time_bucket_size": int(os.getenv("EDGE_TIME_BUCKET_SIZE", "60")),
        # Maximum transaction IDs to store per edge
        "max_txn_ids": int(os.getenv("EDGE_MAX_TXN_IDS", "100")),
        # Edge types to process
        "enabled_edge_types": os.getenv(
            "EDGE_TYPES", "CARD_IP,CARD_MERCHANT,CARD_DEVICE,IP_MERCHANT"
        ).split(","),
        # Edge retention in days
        "retention_days": int(os.getenv("EDGE_RETENTION_DAYS", "90")),
    },
    "monitoring": {
        "port": int(os.getenv("HEALTH_CHECK_PORT", "8083")),
        "metrics_interval": int(os.getenv("METRICS_INTERVAL", "30")),
    },
    "performance": {
        # Target throughput (edges/sec)
        "target_edges_per_sec": int(os.getenv("TARGET_EDGES_PER_SEC", "2000")),
        # Write latency threshold (ms)
        "write_latency_threshold_ms": int(
            os.getenv("WRITE_LATENCY_THRESHOLD_MS", "50")
        ),
        # Back-pressure settings
        "backpressure_threshold_ms": int(os.getenv("BACKPRESSURE_THRESHOLD_MS", "100")),
        "backpressure_pause_duration": int(
            os.getenv("BACKPRESSURE_PAUSE_DURATION", "1000")
        ),
    },
}

# Edge type configurations
EDGE_TYPE_CONFIGS = {
    "CARD_IP": {
        "src_field": "card_id",
        "dst_field": "ip_address",
        "src_prefix": "card:",
        "dst_prefix": "ip:",
        "direction": "outgoing",
        "properties": ["amount", "is_success", "merchant_id"],
    },
    "CARD_MERCHANT": {
        "src_field": "card_id",
        "dst_field": "merchant_id",
        "src_prefix": "card:",
        "dst_prefix": "merchant:",
        "direction": "outgoing",
        "properties": ["amount", "is_success", "ip_address"],
    },
    "CARD_DEVICE": {
        "src_field": "card_id",
        "dst_field": "device_id",
        "src_prefix": "card:",
        "dst_prefix": "device:",
        "direction": "outgoing",
        "properties": ["amount", "is_success", "ip_address"],
    },
    "IP_MERCHANT": {
        "src_field": "ip_address",
        "dst_field": "merchant_id",
        "src_prefix": "ip:",
        "dst_prefix": "merchant:",
        "direction": "outgoing",
        "properties": ["card_id", "amount", "is_success"],
    },
}

# Global state
running = True
service_status = {"status": "initializing", "edges_processed": 0, "last_write": None}


def get_edge_config(edge_type: str) -> Dict[str, Any]:
    """Get configuration for a specific edge type."""
    return EDGE_TYPE_CONFIGS.get(edge_type, {})


def is_edge_type_enabled(edge_type: str) -> bool:
    """Check if an edge type is enabled for processing."""
    return edge_type in config["edge_processing"]["enabled_edge_types"]


def get_enabled_edge_types() -> List[str]:
    """Get list of enabled edge types."""
    return [
        et
        for et in config["edge_processing"]["enabled_edge_types"]
        if et in EDGE_TYPE_CONFIGS
    ]
