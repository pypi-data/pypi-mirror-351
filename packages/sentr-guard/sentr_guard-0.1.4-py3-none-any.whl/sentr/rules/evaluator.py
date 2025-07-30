"""
Safe expression compiler and evaluator for fraud detection rules.

Provides secure AST compilation with whitelist-based node filtering 
and optimized evaluation with early-exit support.
Performance target: P95 ≤ 150µs for 10 rules.
"""

import ast
import logging
import re
import time
from typing import Any, Callable, List, Mapping, Set

from .dsl import Rule

logger = logging.getLogger(__name__)

# Import metrics for tracking rule evaluation performance
try:
    import prometheus_client as prom

    # Create rule-specific metrics using the existing registry
    from infra.metrics import (
        REGISTRY,
    )

    rules_eval_total = prom.Counter(
        "rules_eval_total",
        "Total number of rule evaluations",
        ["result"],  # result: hit, miss
        registry=REGISTRY,
    )

    rules_hit_total = prom.Counter(
        "rules_hit_total",
        "Number of rule hits by rule ID",
        ["rule_id"],
        registry=REGISTRY,
    )

    rules_compile_errors_total = prom.Counter(
        "rules_compile_errors_total",
        "Number of rule compilation errors",
        ["phase"],  # phase: load, validate, compile
        registry=REGISTRY,
    )

    rules_latency_seconds = prom.Histogram(
        "rules_latency_seconds",
        "Rule evaluation latency",
        buckets=(
            0.00005,
            0.0001,
            0.0002,
            0.0005,
            0.001,
        ),  # 50µs to 1ms for sub-200µs target
        registry=REGISTRY,
    )

except ImportError:
    # Fallback no-op metrics if prometheus not available
    class NoOpMetric:
        def labels(self, **kwargs):
            return self

        def inc(self):
            pass

        def observe(self, value):
            pass

    rules_eval_total = NoOpMetric()
    rules_hit_total = NoOpMetric()
    rules_compile_errors_total = NoOpMetric()
    rules_latency_seconds = NoOpMetric()


class UnsafeExpressionError(Exception):
    """Raised when an expression contains unsafe AST nodes."""

    pass


class ExpressionCompileError(Exception):
    """Raised when expression compilation fails."""

    pass


# Whitelist of allowed AST node types (security-first approach)
ALLOWED_AST_NODES: Set[type] = {
    ast.Expression,  # Root expression node
    ast.BoolOp,  # and, or
    ast.BinOp,  # +, -, *, /, //, %, **, <<, >>, |, ^, &
    ast.UnaryOp,  # not, -, +, ~
    ast.Compare,  # ==, !=, <, <=, >, >=, is, is not, in, not in
    ast.Name,  # Variable names
    ast.Constant,  # Python 3.8+ constant values
    ast.Num,  # Numeric literals (legacy, but kept for compatibility)
    ast.Str,  # String literals (legacy)
    ast.Load,  # Variable load context
    ast.Store,  # Variable store context (for comprehensions)
    ast.In,  # 'in' operator
    ast.NotIn,  # 'not in' operator
    ast.Is,  # 'is' operator
    ast.IsNot,  # 'is not' operator
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,  # Comparison operators
    ast.And,
    ast.Or,  # Boolean operators
    ast.Not,  # Unary not
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,  # Arithmetic operators
    ast.List,  # List literals [1, 2, 3]
    ast.Tuple,  # Tuple literals (1, 2, 3)
    ast.Set,  # Set literals {1, 2, 3}
    ast.ListComp,  # List comprehensions [x for x in y]
    ast.SetComp,  # Set comprehensions {x for x in y}
    ast.comprehension,  # Comprehension helper
    ast.Subscript,  # Array/dict access a[b]
    ast.Index,  # Index helper (legacy)
    ast.Slice,  # Slice a[1:2]
}

# Additional safe operators and keywords
SAFE_BUILTINS = {
    "len",
    "min",
    "max",
    "sum",
    "abs",
    "round",
    "int",
    "float",
    "str",
    "bool",
    "any",
    "all",
}

# Pattern to identify feature references (transform a.b.c -> f["a.b.c"])
FEATURE_REFERENCE_PATTERN = re.compile(
    r"\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z0-9_]+)*)\b"
)

# Reserved words that should not be transformed
RESERVED_WORDS = {
    "and",
    "or",
    "not",
    "in",
    "is",
    "True",
    "False",
    "None",
    "len",
    "min",
    "max",
    "sum",
    "abs",
    "round",
    "int",
    "float",
    "str",
    "bool",
    "any",
    "all",
}


def transform_expression(expr: str) -> str:
    """
    Transform rule expression to use feature dictionary access.

    Converts: ip.fail_rate_60s > 0.8 and card.bin_country != ip.geo.country
    To: f["ip.fail_rate_60s"] > 0.8 and f["card.bin_country"] != f["ip.geo.country"]

    Args:
        expr: Original expression string

    Returns:
        Transformed expression string with f["..."] feature access
    """
    import re

    # Pattern that matches feature references but not inside string literals
    # This pattern looks for identifiers that:
    # 1. Start with a letter/underscore
    # 2. Contain letters, numbers, underscores, and dots
    # 3. Are not followed by parentheses (to avoid function calls)
    # 4. Are not inside string literals
    pattern = r'\b([a-zA-Z_][a-zA-Z0-9_.]+)\b(?=(?:[^"\']*(?:"[^"]*"|\'[^\']*\'))*[^"\']*$)(?!\s*\()'

    def replace_feature_ref(match):
        identifier = match.group(1)

        # Don't transform reserved words
        if identifier in RESERVED_WORDS:
            return identifier

        # Don't transform if it looks like a function call (followed by parentheses)
        rest_of_string = expr[match.end() :]
        if rest_of_string.startswith("("):
            return identifier

        # Transform to dictionary access
        return f'f["{identifier}"]'

    # Apply the transformation
    transformed = re.sub(pattern, replace_feature_ref, expr)

    logger.debug(f"Transformed expression: '{expr}' -> '{transformed}'")
    return transformed


def validate_ast_safety(node: ast.AST) -> None:
    """
    Recursively validate that AST only contains safe node types.

    Args:
        node: AST node to validate

    Raises:
        UnsafeExpressionError: If unsafe node type found
    """
    if type(node) not in ALLOWED_AST_NODES:
        raise UnsafeExpressionError(
            f"Unsafe AST node type: {type(node).__name__}. "
            f"Only basic expressions, comparisons, and boolean logic allowed."
        )

    # Recursively check all child nodes
    for child in ast.iter_child_nodes(node):
        validate_ast_safety(child)


def compile_rule_expression(expr: str) -> Callable[[Mapping[str, Any]], bool]:
    """
    Compile rule expression to safe, fast evaluation function.

    Security measures:
    - AST node whitelist (no imports, function calls, etc.)
    - No external builtins access
    - Feature references transformed to dict access

    Performance measures:
    - Pre-compiled to bytecode
    - Minimal runtime overhead
    - JIT-warmed evaluation function

    Args:
        expr: Rule expression string

    Returns:
        Compiled evaluation function

    Raises:
        UnsafeExpressionError: If expression contains unsafe constructs
        ExpressionCompileError: If compilation fails
    """
    try:
        # Step 1: Transform feature references
        transformed_expr = transform_expression(expr)

        # Step 2: Parse to AST
        try:
            parsed = ast.parse(transformed_expr, mode="eval")
        except SyntaxError as e:
            rules_compile_errors_total.labels(phase="parse").inc()
            raise ExpressionCompileError(f"Syntax error in expression '{expr}': {e}")

        # Step 3: Validate AST safety
        try:
            validate_ast_safety(parsed)
        except UnsafeExpressionError:
            rules_compile_errors_total.labels(phase="validate").inc()
            raise

        # Step 4: Compile to bytecode
        try:
            code = compile(parsed, "<rule expression>", "eval")
        except Exception as e:
            rules_compile_errors_total.labels(phase="compile").inc()
            raise ExpressionCompileError(f"Failed to compile expression '{expr}': {e}")

        # Step 5: Create safe evaluation function
        def evaluate_rule(features: Mapping[str, Any]) -> bool:
            """
            Evaluate compiled rule expression against feature set.

            Args:
                features: Feature dictionary

            Returns:
                Boolean result of rule evaluation
            """
            try:
                # Create safe execution environment
                safe_globals = {
                    "__builtins__": {
                        name: __builtins__[name]
                        for name in SAFE_BUILTINS
                        if name in __builtins__
                    },
                    "f": features,  # Feature dictionary access
                }

                # Evaluate compiled bytecode
                result = eval(code, safe_globals, {})
                return bool(result)

            except KeyError as e:
                # Missing feature - treat as False (feature not present)
                logger.debug(f"Missing feature in rule evaluation: {e}")
                return False
            except Exception as e:
                # Other evaluation errors - log and treat as False
                logger.warning(f"Error evaluating rule expression '{expr}': {e}")
                return False

        # Step 6: Pre-warm the function (JIT optimization)
        try:
            evaluate_rule({})  # Call once with empty dict to warm bytecode
        except Exception:
            pass  # Ignore errors during warming

        return evaluate_rule

    except (UnsafeExpressionError, ExpressionCompileError):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        rules_compile_errors_total.labels(phase="unknown").inc()
        raise ExpressionCompileError(
            f"Unexpected error compiling expression '{expr}': {e}"
        )


class RuleEvaluator:
    """
    High-performance rule evaluator with early-exit optimization.

    Evaluates rules in order and stops on first blocking action.
    Target performance: P95 ≤ 150µs for 10 rules.
    """

    def __init__(self, rules: List[Rule]):
        """
        Initialize evaluator with compiled rules.

        Args:
            rules: List of rules to evaluate (order matters for early-exit)
        """
        self.rules = rules
        self.active_rules = [rule for rule in rules if rule.is_active()]

        # Pre-compile all rule expressions
        self._compile_rules()

        logger.info(
            f"RuleEvaluator initialized with {len(rules)} total rules, "
            f"{len(self.active_rules)} active"
        )

    def _compile_rules(self) -> None:
        """Compile expressions for all rules."""
        compiled_count = 0

        for rule in self.rules:
            try:
                # Compile the expression
                compiled_fn = compile_rule_expression(rule.expr)

                # Store compiled function (use object.__setattr__ for frozen dataclass)
                object.__setattr__(rule, "_fn", compiled_fn)
                compiled_count += 1

            except (UnsafeExpressionError, ExpressionCompileError) as e:
                logger.error(f"Failed to compile rule '{rule.id}': {e}")
                # Store a function that always returns False for safety
                object.__setattr__(rule, "_fn", lambda features: False)

        logger.info(f"Compiled {compiled_count}/{len(self.rules)} rules successfully")

    def evaluate(self, features: Mapping[str, Any]) -> List[Rule]:
        """
        Evaluate all active rules against feature set with early-exit.

        Performance optimizations:
        - Skip audit rules entirely
        - Early-exit on first blocking rule
        - Minimal function call overhead
        - Pre-compiled expressions

        Args:
            features: Feature dictionary to evaluate against

        Returns:
            List of rules that triggered (empty if none)
        """
        start_time = time.perf_counter()
        hits: List[Rule] = []

        try:
            # Evaluate active rules in order
            for rule in self.active_rules:
                # Skip audit rules (they don't affect decisions)
                if rule.state == "audit":
                    continue

                # Evaluate rule expression
                try:
                    if rule._fn and rule._fn(features):
                        hits.append(rule)

                        # Track rule hit
                        rules_hit_total.labels(rule_id=rule.id).inc()

                        # Early exit on blocking actions
                        if rule.is_blocking():
                            logger.debug(f"Early exit on blocking rule: {rule.id}")
                            break

                except Exception as e:
                    logger.warning(f"Error evaluating rule '{rule.id}': {e}")
                    # Continue with other rules
                    continue

            # Track evaluation metrics
            result = "hit" if hits else "miss"
            rules_eval_total.labels(result=result).inc()

            # Track latency
            duration = time.perf_counter() - start_time
            rules_latency_seconds.observe(duration)

            if hits:
                logger.debug(
                    f"Rule evaluation: {len(hits)} hits in {duration*1000:.3f}ms"
                )

            return hits

        except Exception as e:
            # Track failed evaluation
            duration = time.perf_counter() - start_time
            rules_latency_seconds.observe(duration)
            logger.error(f"Critical error in rule evaluation: {e}")
            return []  # Fail safe - no rules triggered

    def evaluate_single(self, rule: Rule, features: Mapping[str, Any]) -> bool:
        """
        Evaluate a single rule against features.

        Args:
            rule: Rule to evaluate
            features: Feature dictionary

        Returns:
            True if rule triggered, False otherwise
        """
        if not rule._fn:
            return False

        try:
            return rule._fn(features)
        except Exception as e:
            logger.warning(f"Error evaluating single rule '{rule.id}': {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get evaluator statistics.

        Returns:
            Dictionary with evaluator stats
        """
        return {
            "total_rules": len(self.rules),
            "active_rules": len(self.active_rules),
            "audit_rules": len([r for r in self.rules if r.state == "audit"]),
            "blocking_rules": len([r for r in self.active_rules if r.is_blocking()]),
            "compiled_rules": len([r for r in self.rules if r._fn is not None]),
        }
