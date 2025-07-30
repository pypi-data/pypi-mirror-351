#!/usr/bin/env python3
"""
Simple Performance Monitor for Feature Builder

Provides real-time performance insights and alerts for the Feature Builder service.
"""

import logging
import threading
import time
from collections import defaultdict, deque
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Lightweight performance monitor that tracks key metrics and provides alerts.
    """

    def __init__(self, alert_threshold_tps=50, window_size=60):
        """
        Initialize performance monitor.

        Args:
            alert_threshold_tps: TPS below which to trigger alerts
            window_size: Time window for performance calculations (seconds)
        """
        self.alert_threshold_tps = alert_threshold_tps
        self.window_size = window_size

        # Performance tracking
        self.transaction_times = deque(maxlen=1000)
        self.flush_times = deque(maxlen=100)
        self.error_counts = defaultdict(int)

        # Current metrics
        self.current_tps = 0.0
        self.avg_flush_time = 0.0
        self.total_transactions = 0
        self.total_errors = 0

        # Alerts
        self.alerts = deque(maxlen=50)
        self.last_alert_time = 0

        # Thread safety
        self._lock = threading.RLock()

    def record_transaction(self, processing_time: float = None) -> None:
        """Record a transaction for performance tracking."""
        with self._lock:
            current_time = time.time()
            self.transaction_times.append(current_time)
            self.total_transactions += 1

            if processing_time:
                # Could track processing times if needed
                pass

    def record_flush(self, flush_time: float) -> None:
        """Record a pipeline flush time."""
        with self._lock:
            self.flush_times.append(flush_time)

    def record_error(self, error_type: str) -> None:
        """Record an error for monitoring."""
        with self._lock:
            self.error_counts[error_type] += 1
            self.total_errors += 1

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        with self._lock:
            current_time = time.time()

            # Calculate TPS over the last window
            cutoff_time = current_time - self.window_size
            recent_transactions = [
                t for t in self.transaction_times if t >= cutoff_time
            ]
            self.current_tps = (
                len(recent_transactions) / self.window_size
                if recent_transactions
                else 0.0
            )

            # Calculate average flush time
            if self.flush_times:
                self.avg_flush_time = sum(self.flush_times) / len(self.flush_times)

            # Check for alerts
            self._check_alerts()

            return {
                "current_tps": round(self.current_tps, 2),
                "avg_flush_time_ms": round(self.avg_flush_time * 1000, 2),
                "total_transactions": self.total_transactions,
                "total_errors": self.total_errors,
                "error_rate": round(
                    self.total_errors / max(1, self.total_transactions) * 100, 2
                ),
                "recent_alerts": list(self.alerts)[-5:],  # Last 5 alerts
                "status": self._get_status(),
            }

    def _check_alerts(self) -> None:
        """Check for performance issues and generate alerts."""
        current_time = time.time()

        # Rate limit alerts to once per minute
        if current_time - self.last_alert_time < 60:
            return

        # TPS too low
        if (
            self.current_tps < self.alert_threshold_tps
            and self.total_transactions > 100
        ):
            self._add_alert(
                "LOW_TPS",
                f"TPS dropped to {self.current_tps:.1f} (threshold: {self.alert_threshold_tps})",
            )

        # Flush time too high
        if self.avg_flush_time > 0.1:  # 100ms
            self._add_alert(
                "HIGH_FLUSH_TIME",
                f"Average flush time: {self.avg_flush_time*1000:.1f}ms",
            )

        # High error rate
        error_rate = self.total_errors / max(1, self.total_transactions) * 100
        if error_rate > 5:  # 5% error rate
            self._add_alert("HIGH_ERROR_RATE", f"Error rate: {error_rate:.1f}%")

    def _add_alert(self, alert_type: str, message: str) -> None:
        """Add an alert to the queue."""
        alert = {"timestamp": time.time(), "type": alert_type, "message": message}
        self.alerts.append(alert)
        self.last_alert_time = time.time()

    def _get_status(self) -> str:
        """Get overall system status."""
        if self.current_tps < self.alert_threshold_tps * 0.5:
            return "CRITICAL"
        elif self.current_tps < self.alert_threshold_tps:
            return "WARNING"
        elif self.avg_flush_time > 0.05:  # 50ms
            return "WARNING"
        else:
            return "HEALTHY"

    def print_status(self) -> None:
        """Print current status to console."""
        metrics = self.get_current_metrics()

        logger.info("Feature Builder Performance Monitor")
        logger.info(
            "Performance metrics",
            status=metrics["status"],
            current_tps=metrics["current_tps"],
            avg_flush_time_ms=metrics["avg_flush_time_ms"],
            total_transactions=metrics["total_transactions"],
            total_errors=metrics["total_errors"],
            error_rate=metrics["error_rate"],
        )

        if metrics["recent_alerts"]:
            logger.warning("Recent performance alerts detected")
            for alert in metrics["recent_alerts"]:
                alert_time = time.strftime(
                    "%H:%M:%S", time.localtime(alert["timestamp"])
                )
                logger.warning(
                    "Performance alert",
                    timestamp=alert_time,
                    alert_type=alert["type"],
                    message=alert["message"],
                )

        logger.info("=" * 60)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return performance_monitor
