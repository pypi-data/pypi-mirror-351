"""
Common enums and constants for the Sentr fraud detection system.

Centralizes string literals to avoid duplication and typos.
"""

from enum import Enum


class ErrorReason(str, Enum):
    """Error reasons for API responses."""

    REDIS_DOWN = "redis_down"
    BURST_FAILURES = "burst_failures"
    RATE_LIMITED = "rate_limited"
    INVALID_REQUEST = "invalid_request"
    INTERNAL_ERROR = "internal_error"


class PanicMode(str, Enum):
    """Panic mode types for emergency controls."""

    BLOCK_ALL = "block_all"
    ALLOW_ALL = "allow_all"
    DISABLED = "disabled"


class PanicReason(str, Enum):
    """Panic mode reasons for decision responses."""

    PANIC_BLOCK_ALL = "panic_block_all"
    PANIC_ALLOW_ALL = "panic_allow_all"


class DecisionAction(str, Enum):
    """Decision actions for fraud detection."""

    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE_3DS = "challenge_3ds"
    REVIEW = "review"


class RuleState(str, Enum):
    """Rule states for rule engine."""

    ACTIVE = "active"
    AUDIT = "audit"
    DISABLED = "disabled"


class ServiceStatus(str, Enum):
    """Service health status values."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
