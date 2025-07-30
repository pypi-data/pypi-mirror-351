"""
Sentr-Guard: High-Performance Fraud Detection Rules Engine

A lightweight, high-performance fraud detection system optimized for real-time
transaction processing with sub-millisecond rule evaluation.
"""

__version__ = "0.1.4"
__author__ = "Sentr Team"
__email__ = "hello@sentr.dev"

# Core components
try:
    from .engine.rules_engine import RulesEngine
    from .rules.rule_parser import RuleParser
    _RULES_ENGINE_AVAILABLE = True
except ImportError:
    _RULES_ENGINE_AVAILABLE = False

# Feature store (optional)
try:
    from .feature_store.time_series_store import TimeSeriesStore
    _FEATURE_STORE_AVAILABLE = True
except ImportError:
    _FEATURE_STORE_AVAILABLE = False

# Monitoring (optional)
try:
    from .monitoring.metrics import MetricsCollector
    _MONITORING_AVAILABLE = True
except ImportError:
    _MONITORING_AVAILABLE = False

# Export main components
__all__ = [
    "__version__",
    "RulesEngine", 
    "RuleParser",
    "get_component_status"
]

# Only export if available
if _RULES_ENGINE_AVAILABLE:
    __all__.extend(["RulesEngine", "RuleParser"])
if _FEATURE_STORE_AVAILABLE:
    __all__.append("TimeSeriesStore")
if _MONITORING_AVAILABLE:
    __all__.append("MetricsCollector")

def get_component_status():
    """Get status of available components."""
    return {
        "rules_engine": _RULES_ENGINE_AVAILABLE,
        "feature_store": _FEATURE_STORE_AVAILABLE,
        "monitoring": _MONITORING_AVAILABLE,
        "version": __version__
    } 