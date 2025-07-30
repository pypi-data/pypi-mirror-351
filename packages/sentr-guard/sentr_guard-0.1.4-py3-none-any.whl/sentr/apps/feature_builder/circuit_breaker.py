"""
Redis Circuit Breaker Implementation

Provides a circuit breaker pattern implementation to handle Redis failures gracefully
with exponential back-off and fast-fail capabilities.
"""

import enum
import functools
import threading
import time
from typing import Callable, Optional

import redis
import structlog

logger = structlog.get_logger()


class CircuitOpenError(redis.RedisError):
    """Exception raised when circuit breaker is open"""

    pass


class CircuitState(enum.Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation - requests go through
    OPEN = "open"  # Failure mode - fast fail all requests
    HALF_OPEN = "half_open"  # Testing mode - allowing limited requests to check if service is back


class RedisCircuitBreaker:
    """
    Implements circuit breaker pattern for Redis operations.
    Tracks failures and opens the circuit when threshold is reached.
    """

    def __init__(
        self,
        failure_threshold: int = 5,  # consecutive failures
        recovery_timeout: int = 30,
        timeout_factor: float = 2.0,
        max_timeout: int = 300,
        excluded_exceptions: Optional[list] = None,
        circuit_name: str = "redis",
    ):
        """
        Initialize the circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            recovery_timeout: Initial timeout (seconds) before trying half-open state
            timeout_factor: Factor to multiply timeout by with each consecutive failure
            max_timeout: Maximum timeout value (seconds)
            excluded_exceptions: List of exceptions that should not count as failures.
                                Each element must be an exception class or a tuple of exception classes.
            circuit_name: Name of this circuit breaker for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.initial_recovery_timeout = recovery_timeout
        self.recovery_timeout = recovery_timeout
        self.timeout_factor = timeout_factor
        self.max_timeout = max_timeout
        self.excluded_exceptions = excluded_exceptions or []
        self.circuit_name = circuit_name

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.next_attempt_time = 0

        self._lock = threading.RLock()

        # Bind circuit name to logger for consistent tracking
        self.logger = logger.bind(circuit=circuit_name)

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to wrap Redis operations with circuit breaker pattern.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == CircuitState.OPEN:
                    # Check if we should try half-open state
                    if time.time() > self.next_attempt_time:
                        self.state = CircuitState.HALF_OPEN
                        self.logger.info(
                            "Circuit half-open, testing Redis connection",
                            failure_count=self.failure_count,
                            seconds_since_failure=time.time() - self.last_failure_time,
                        )
                    else:
                        # Fast fail - circuit is open
                        seconds_until_retry = max(
                            0, self.next_attempt_time - time.time()
                        )
                        raise CircuitOpenError(
                            f"Circuit breaker '{self.circuit_name}' open - Redis unavailable. "
                            f"Next retry in {seconds_until_retry:.1f}s"
                        )

            try:
                result = func(*args, **kwargs)

                # If successful and in half-open state, close the circuit
                with self._lock:
                    if self.state == CircuitState.HALF_OPEN:
                        self.state = CircuitState.CLOSED
                        self.failure_count = 0
                        self.recovery_timeout = self.initial_recovery_timeout
                        self.logger.info("Circuit closed, Redis operations restored")

                return result

            except Exception as e:
                # Check if this exception should count as a failure
                # Support both exception classes and tuples of exception classes
                excluded = False
                for exc in self.excluded_exceptions:
                    if isinstance(exc, tuple):
                        if isinstance(e, exc):
                            excluded = True
                            break
                    elif isinstance(e, exc):
                        excluded = True
                        break

                if excluded:
                    # This is an excluded exception, don't count as circuit failure
                    raise

                with self._lock:
                    self.failure_count += 1
                    self.last_failure_time = time.time()

                    if (
                        self.state == CircuitState.CLOSED
                        and self.failure_count >= self.failure_threshold
                    ):
                        # Open the circuit after reaching threshold
                        self.state = CircuitState.OPEN
                        self.next_attempt_time = time.time() + self.recovery_timeout
                        self.logger.warning(
                            "Circuit opened, Redis operations suspended",
                            failures=self.failure_count,
                            recovery_timeout=self.recovery_timeout,
                        )

                    elif self.state == CircuitState.HALF_OPEN:
                        # Failed during testing, increase timeout exponentially
                        self.state = CircuitState.OPEN
                        self.recovery_timeout = min(
                            self.recovery_timeout * self.timeout_factor,
                            self.max_timeout,
                        )
                        self.next_attempt_time = time.time() + self.recovery_timeout
                        self.logger.warning(
                            "Circuit re-opened after failed test",
                            failures=self.failure_count,
                            recovery_timeout=self.recovery_timeout,
                        )

                # Re-raise the original exception
                raise

        return wrapper

    def reset(self):
        """Reset the circuit breaker to closed state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = 0
            self.next_attempt_time = 0
            self.recovery_timeout = self.initial_recovery_timeout

    def get_state(self):
        """Get the current state of the circuit breaker"""
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "last_failure": self.last_failure_time,
                "next_attempt": self.next_attempt_time,
                "recovery_timeout": self.recovery_timeout,
            }
