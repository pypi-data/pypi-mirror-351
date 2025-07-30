"""
YAML rule parser and RuleSet loader for fraud detection rules.

Provides safe YAML loading with validation, duplicate detection,
and comprehensive error reporting with line/column information.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.constructor import DuplicateKeyError
    from ruamel.yaml.parser import ParserError
    from ruamel.yaml.scanner import ScannerError

    YAML_AVAILABLE = True
except ImportError:
    # Fallback to standard yaml if ruamel.yaml not available
    import yaml

    YAML_AVAILABLE = False
    YAML = None
    ParserError = yaml.parser.ParserError
    ScannerError = yaml.scanner.ScannerError
    DuplicateKeyError = Exception

from .dsl import Rule, RuleAction, RuleState, validate_rule_id, validate_score
from .evaluator import RuleEvaluator

logger = logging.getLogger(__name__)


class DuplicateRuleIDError(Exception):
    """Raised when duplicate rule IDs are found."""

    pass


class RuleValidationError(Exception):
    """Raised when rule validation fails."""

    pass


class RuleParseError(Exception):
    """Raised when YAML parsing fails."""

    pass


@dataclass(frozen=True)
class RuleSet:
    """
    Immutable collection of fraud detection rules.

    Attributes:
        rules: Tuple of rules (immutable)
        revision_hash: SHA256 hash of rule content for change detection
        source_path: Path to source file/directory
        metadata: Additional metadata about the ruleset
    """

    rules: Tuple[Rule, ...] = field(default_factory=tuple)
    revision_hash: str = ""
    source_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Cached evaluator (not part of equality/hashing)
    _evaluator: Optional[RuleEvaluator] = field(
        init=False, repr=False, compare=False, default=None
    )

    def __post_init__(self):
        """Initialize derived fields after creation."""
        if not self.revision_hash:
            # Calculate revision hash from rule content
            content = self._get_content_for_hash()
            revision_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
            object.__setattr__(self, "revision_hash", revision_hash)

        # Create evaluator
        evaluator = RuleEvaluator(list(self.rules))
        object.__setattr__(self, "_evaluator", evaluator)

    def _get_content_for_hash(self) -> str:
        """Get normalized content string for hashing."""
        rule_contents = []
        for rule in self.rules:
            rule_content = f"{rule.id}:{rule.expr}:{rule.action.value}:{rule.score}:{rule.state.value}"
            rule_contents.append(rule_content)

        # Include file metadata if available to detect file changes
        content_parts = ["\n".join(sorted(rule_contents))]

        if self.metadata:
            # Include file modification time and size to detect any file changes
            if "modified_time" in self.metadata:
                content_parts.append(f"mtime:{self.metadata['modified_time']}")
            if "file_size" in self.metadata:
                content_parts.append(f"size:{self.metadata['file_size']}")
            if "files" in self.metadata:
                # For directory-based rulesets, include all file metadata
                for file_info in self.metadata["files"]:
                    content_parts.append(
                        f"file:{file_info['path']}:{file_info['modified_time']}:{file_info['size']}"
                    )

        return "|".join(content_parts)

    def evaluate(self, features: Dict[str, Any]) -> List[Rule]:
        """
        Evaluate all rules against feature set.

        Args:
            features: Feature dictionary

        Returns:
            List of triggered rules
        """
        if self._evaluator is None:
            return []
        return self._evaluator.evaluate(features)

    def get_rule_by_id(self, rule_id: str) -> Optional[Rule]:
        """Get rule by ID."""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def get_active_rules(self) -> List[Rule]:
        """Get all active (non-audit) rules."""
        return [rule for rule in self.rules if rule.is_active()]

    def get_blocking_rules(self) -> List[Rule]:
        """Get all rules that can block transactions."""
        return [rule for rule in self.rules if rule.is_blocking()]

    def get_stats(self) -> Dict[str, Any]:
        """Get ruleset statistics."""
        active_rules = self.get_active_rules()
        blocking_rules = self.get_blocking_rules()

        stats = {
            "total_rules": len(self.rules),
            "active_rules": len(active_rules),
            "audit_rules": len([r for r in self.rules if r.state == RuleState.AUDIT]),
            "shadow_rules": len([r for r in self.rules if r.state == RuleState.SHADOW]),
            "enforce_rules": len(
                [r for r in self.rules if r.state == RuleState.ENFORCE]
            ),
            "blocking_rules": len(blocking_rules),
            "revision_hash": self.revision_hash,
            "source_path": self.source_path,
        }

        if self._evaluator:
            stats.update(self._evaluator.get_stats())

        return stats


def _create_yaml_loader() -> Union[YAML, Any]:
    """Create YAML loader with safe configuration."""
    if YAML_AVAILABLE:
        # Use ruamel.yaml for better error reporting and comment preservation
        yaml_loader = YAML(typ="rt", pure=True)
        yaml_loader.preserve_quotes = True
        yaml_loader.map_indent = 2
        yaml_loader.sequence_indent = 4
        return yaml_loader
    else:
        # Fallback to standard yaml
        return yaml


def _validate_rule_dict(
    rule_data: Dict[str, Any], line_num: Optional[int] = None
) -> None:
    """
    Validate rule dictionary structure and values.

    Args:
        rule_data: Rule dictionary to validate
        line_num: Line number for error reporting

    Raises:
        RuleValidationError: If validation fails
    """
    location = f" (line {line_num})" if line_num else ""

    # Check required fields
    required_fields = {"id", "if", "action"}
    missing_fields = required_fields - set(rule_data.keys())
    if missing_fields:
        raise RuleValidationError(
            f"Missing required fields: {missing_fields}{location}"
        )

    # Validate allowed top-level keys
    allowed_keys = {"id", "if", "action", "score", "state", "description", "tags"}
    invalid_keys = set(rule_data.keys()) - allowed_keys
    if invalid_keys:
        raise RuleValidationError(
            f"Invalid keys found: {invalid_keys}. Allowed: {allowed_keys}{location}"
        )

    # Validate rule ID
    try:
        validate_rule_id(rule_data["id"])
    except ValueError as e:
        raise RuleValidationError(f"Invalid rule ID: {e}{location}")

    # Validate expression is not empty
    expr = rule_data["if"]
    if not expr or not str(expr).strip():
        raise RuleValidationError(f"Rule expression cannot be empty{location}")

    # Validate action
    try:
        RuleAction(rule_data["action"])
    except ValueError:
        valid_actions = [action.value for action in RuleAction]
        raise RuleValidationError(
            f"Invalid action '{rule_data['action']}'. Valid actions: {valid_actions}{location}"
        )

    # Validate score if present
    if "score" in rule_data:
        try:
            validate_score(rule_data["score"])
        except ValueError as e:
            raise RuleValidationError(f"Invalid score: {e}{location}")

    # Validate state if present
    if "state" in rule_data:
        try:
            RuleState(rule_data["state"])
        except ValueError:
            valid_states = [state.value for state in RuleState]
            raise RuleValidationError(
                f"Invalid state '{rule_data['state']}'. Valid states: {valid_states}{location}"
            )


def _get_line_number(node, yaml_loader) -> Optional[int]:
    """Extract line number from YAML node if available."""
    if YAML_AVAILABLE and hasattr(node, "start_mark"):
        return node.start_mark.line + 1
    return None


def parse_rule_yaml(yaml_content: str, source_path: Optional[str] = None) -> List[Rule]:
    """
    Parse YAML content into Rule objects.

    Args:
        yaml_content: YAML string content
        source_path: Source file path for error reporting

    Returns:
        List of parsed Rule objects

    Raises:
        RuleParseError: If YAML parsing fails
        RuleValidationError: If rule validation fails
        DuplicateRuleIDError: If duplicate rule IDs found
    """
    yaml_loader = _create_yaml_loader()

    try:
        # Parse YAML content
        if YAML_AVAILABLE:
            documents = list(yaml_loader.load_all(yaml_content))
        else:
            documents = list(yaml.safe_load_all(yaml_content))

        if not documents:
            return []

        # Handle single document vs multiple documents
        if len(documents) == 1 and isinstance(documents[0], list):
            rule_dicts = documents[0]
        else:
            # Multiple documents or single dict
            rule_dicts = []
            for doc in documents:
                if isinstance(doc, list):
                    rule_dicts.extend(doc)
                elif isinstance(doc, dict):
                    rule_dicts.append(doc)
                else:
                    source_info = f" in {source_path}" if source_path else ""
                    raise RuleParseError(f"Invalid YAML structure{source_info}")

        # Validate and convert to Rule objects
        rules = []
        seen_ids = set()

        for i, rule_data in enumerate(rule_dicts):
            if not isinstance(rule_data, dict):
                source_info = f" in {source_path}" if source_path else ""
                raise RuleParseError(
                    f"Rule at index {i} is not a dictionary{source_info}"
                )

            # Get line number for error reporting
            line_num = (
                _get_line_number(rule_data, yaml_loader) if YAML_AVAILABLE else None
            )

            # Validate rule structure
            _validate_rule_dict(rule_data, line_num)

            # Check for duplicate IDs
            rule_id = rule_data["id"]
            if rule_id in seen_ids:
                source_info = f" in {source_path}" if source_path else ""
                line_info = f" (line {line_num})" if line_num else ""
                raise DuplicateRuleIDError(
                    f"Duplicate rule ID '{rule_id}'{line_info}{source_info}"
                )
            seen_ids.add(rule_id)

            # Create Rule object
            try:
                rule = Rule.from_dict(rule_data)
                rules.append(rule)
            except Exception as e:
                source_info = f" in {source_path}" if source_path else ""
                line_info = f" (line {line_num})" if line_num else ""
                raise RuleValidationError(
                    f"Failed to create rule '{rule_id}': {e}{line_info}{source_info}"
                )

        return rules

    except (ParserError, ScannerError) as e:
        source_info = f" in {source_path}" if source_path else ""
        raise RuleParseError(f"YAML syntax error: {e}{source_info}")
    except DuplicateKeyError as e:
        source_info = f" in {source_path}" if source_path else ""
        raise RuleParseError(f"Duplicate YAML key: {e}{source_info}")
    except (RuleParseError, RuleValidationError, DuplicateRuleIDError):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        source_info = f" in {source_path}" if source_path else ""
        raise RuleParseError(f"Unexpected error parsing YAML: {e}{source_info}")


def load_ruleset_from_file(file_path: Union[str, Path]) -> RuleSet:
    """
    Load RuleSet from a single YAML file.

    Args:
        file_path: Path to YAML file

    Returns:
        RuleSet object

    Raises:
        FileNotFoundError: If file doesn't exist
        RuleParseError: If parsing fails
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Rule file not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        yaml_content = file_path.read_text(encoding="utf-8")
        rules = parse_rule_yaml(yaml_content, str(file_path))

        metadata = {
            "source_type": "file",
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "modified_time": file_path.stat().st_mtime,
        }

        return RuleSet(
            rules=tuple(rules), source_path=str(file_path), metadata=metadata
        )

    except (RuleParseError, RuleValidationError, DuplicateRuleIDError):
        raise  # Re-raise rule-specific errors
    except Exception as e:
        raise RuleParseError(f"Error reading rule file {file_path}: {e}")


def load_ruleset_from_directory(dir_path: Union[str, Path]) -> RuleSet:
    """
    Load RuleSet from directory of YAML files.

    Args:
        dir_path: Path to directory containing YAML files

    Returns:
        RuleSet object with rules from all files

    Raises:
        FileNotFoundError: If directory doesn't exist
        RuleParseError: If parsing fails
    """
    dir_path = Path(dir_path)

    if not dir_path.exists():
        raise FileNotFoundError(f"Rule directory not found: {dir_path}")

    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {dir_path}")

    # Find all YAML files
    yaml_files = []
    for pattern in ["*.yml", "*.yaml"]:
        yaml_files.extend(dir_path.glob(pattern))

    if not yaml_files:
        logger.warning(f"No YAML files found in directory: {dir_path}")
        return RuleSet(source_path=str(dir_path))

    # Load rules from all files
    all_rules = []
    seen_ids = set()
    file_info = []

    for yaml_file in sorted(yaml_files):
        try:
            yaml_content = yaml_file.read_text(encoding="utf-8")
            file_rules = parse_rule_yaml(yaml_content, str(yaml_file))

            # Check for duplicate IDs across files
            for rule in file_rules:
                if rule.id in seen_ids:
                    raise DuplicateRuleIDError(
                        f"Duplicate rule ID '{rule.id}' found in {yaml_file} "
                        f"(already defined in another file)"
                    )
                seen_ids.add(rule.id)

            all_rules.extend(file_rules)
            file_info.append(
                {
                    "path": str(yaml_file),
                    "rule_count": len(file_rules),
                    "size": yaml_file.stat().st_size,
                    "modified_time": yaml_file.stat().st_mtime,
                }
            )

        except Exception as e:
            logger.error(f"Error loading rules from {yaml_file}: {e}")
            raise

    metadata = {
        "source_type": "directory",
        "directory_path": str(dir_path),
        "file_count": len(yaml_files),
        "files": file_info,
    }

    return RuleSet(rules=tuple(all_rules), source_path=str(dir_path), metadata=metadata)


def load_ruleset_from_yaml(path: Union[str, Path]) -> RuleSet:
    """
    Load RuleSet from YAML file or directory.

    Args:
        path: Path to YAML file or directory

    Returns:
        RuleSet object

    Raises:
        FileNotFoundError: If path doesn't exist
        RuleParseError: If parsing fails
    """
    path = Path(path)

    if path.is_file():
        return load_ruleset_from_file(path)
    elif path.is_dir():
        return load_ruleset_from_directory(path)
    else:
        raise FileNotFoundError(f"Rule path not found: {path}")


def format_rule_yaml(rules: List[Rule]) -> str:
    """
    Format rules as canonical YAML.

    Args:
        rules: List of rules to format

    Returns:
        Formatted YAML string
    """
    yaml_loader = _create_yaml_loader()

    # Convert rules to dictionaries
    rule_dicts = []
    for rule in rules:
        rule_dict = {
            "id": rule.id,
            "if": rule.expr,
            "action": rule.action.value,
            "score": rule.score,
            "state": rule.state.value,
        }
        rule_dicts.append(rule_dict)

    # Format as YAML
    if YAML_AVAILABLE:
        import io

        output = io.StringIO()
        yaml_loader.dump(rule_dicts, output)
        return output.getvalue()
    else:
        return yaml.dump(rule_dicts, default_flow_style=False, sort_keys=False)
