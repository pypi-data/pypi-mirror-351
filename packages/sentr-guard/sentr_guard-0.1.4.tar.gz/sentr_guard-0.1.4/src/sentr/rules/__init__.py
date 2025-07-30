"""
Rules engine for Sentr fraud detection system.

Provides deterministic, safe, sub-200µs rule evaluation with:
- Immutable rule definitions
- Safe expression compilation 
- YAML configuration support
- CLI utilities for development
- Prometheus metrics integration
"""

from .dsl import Rule, RuleAction, RuleState
from .evaluator import RuleEvaluator, UnsafeExpressionError, compile_rule_expression
from .parser import (
    DuplicateRuleIDError,
    RuleSet,
    format_rule_yaml,
    load_ruleset_from_yaml,
)

__all__ = [
    "Rule",
    "RuleAction",
    "RuleState",
    "RuleSet",
    "RuleEvaluator",
    "load_ruleset_from_yaml",
    "format_rule_yaml",
    "compile_rule_expression",
    "DuplicateRuleIDError",
    "UnsafeExpressionError",
]
