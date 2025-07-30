#!/usr/bin/env python3
"""
Command-line interface for Sentr rules engine and guard service.

Provides utilities for rule validation, simulation, formatting, and panic mode control.
"""
import asyncio
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import click
import redis
import structlog
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from common.enums import PanicMode

from .parser import RuleParseError, load_ruleset_from_yaml

console = Console()
logger = structlog.get_logger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(verbose: bool):
    """Sentr rules engine and guard service CLI."""
    if verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.argument("rules_file", type=click.Path(exists=True))
def lint(rules_file: str):
    """Validate rules file syntax and semantics."""
    console.print(f"[blue]Linting rules file: {rules_file}[/blue]")

    try:
        ruleset = load_ruleset_from_yaml(rules_file)

        # Display validation results
        table = Table(title="Rule Validation Results")
        table.add_column("Rule ID", style="cyan")
        table.add_column("Expression", style="white")
        table.add_column("Action", style="green")
        table.add_column("State", style="yellow")
        table.add_column("Score", style="magenta")

        for rule in ruleset.rules:
            table.add_row(
                rule.id,
                rule.expr[:50] + "..." if len(rule.expr) > 50 else rule.expr,
                rule.action.value,
                rule.state.value,
                str(rule.score),
            )

        console.print(table)
        console.print(
            f"[green]+ {len(ruleset.rules)} rules validated successfully[/green]"
        )
        console.print(f"[blue]Revision: {ruleset.revision_hash}[/blue]")

    except RuleParseError as e:
        console.print(f"[red]- Validation failed:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]- Unexpected error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("rules_file", type=click.Path(exists=True))
@click.option(
    "--merchant-id", default="test_merchant", help="Merchant ID for simulation"
)
@click.option("--amount", type=float, default=100.0, help="Transaction amount")
@click.option("--ip", default="192.168.1.1", help="Client IP address")
@click.option("--bin", default="411111", help="Card BIN")
@click.option("--features", help="JSON string of additional features")
def simulate(
    rules_file: str,
    merchant_id: str,
    amount: float,
    ip: str,
    bin: str,
    features: Optional[str],
):
    """Simulate rule evaluation with test data."""
    import json

    console.print(f"[blue]Simulating rules from: {rules_file}[/blue]")

    try:
        # Load ruleset
        ruleset = load_ruleset_from_yaml(rules_file)

        # Prepare features
        test_features = {
            "merchant_id": merchant_id,
            "amount": amount,
            "ip": ip,
            "bin": bin,
            "timestamp": time.time(),
        }

        # Add additional features from JSON
        if features:
            try:
                additional = json.loads(features)
                test_features.update(additional)
            except json.JSONDecodeError as e:
                console.print(f"[red]Invalid JSON in features: {e}[/red]")
                sys.exit(1)

        # Display test scenario
        console.print("\n[bold]Test Scenario:[/bold]")
        feature_table = Table()
        feature_table.add_column("Feature", style="cyan")
        feature_table.add_column("Value", style="white")

        for key, value in test_features.items():
            feature_table.add_row(key, str(value))

        console.print(feature_table)

        # Evaluate rules
        hits = ruleset.evaluate(test_features)

        # Display results
        if hits:
            console.print(f"\n[red]+ {len(hits)} rule(s) triggered:[/red]")

            results_table = Table()
            results_table.add_column("Rule ID", style="cyan")
            results_table.add_column("Action", style="red")
            results_table.add_column("Score", style="magenta")
            results_table.add_column("Expression", style="white")

            for hit in hits:
                results_table.add_row(
                    hit.id,
                    hit.action.value,
                    str(hit.score),
                    hit.expr[:60] + "..." if len(hit.expr) > 60 else hit.expr,
                )

            console.print(results_table)

            # Show final decision
            max_score = max(hit.score for hit in hits)
            has_block = any(hit.action.value == "BLOCK" for hit in hits)
            has_challenge = any(hit.action.value == "CHALLENGE_3DS" for hit in hits)

            if has_block:
                decision = "BLOCK"
                color = "red"
            elif has_challenge:
                decision = "CHALLENGE_3DS"
                color = "yellow"
            else:
                decision = "ALLOW"
                color = "green"

            console.print(
                f"\n[bold {color}]Final Decision: {decision} (Score: {max_score})[/bold {color}]"
            )

        else:
            console.print(
                "\n[green]+ No rules triggered - transaction would be ALLOWED[/green]"
            )

    except Exception as e:
        console.print(f"[red]- Simulation failed:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("rules_file", type=click.Path(exists=True))
def fmt(rules_file: str):
    """Format and normalize rules file."""
    # This would implement YAML formatting/normalization
    console.print(f"[blue]Formatting rules file: {rules_file}[/blue]")
    console.print("[yellow]Format command not yet implemented[/yellow]")


# New panic mode commands
@cli.group()
def panic():
    """Panic mode control commands."""
    pass


@panic.command("block-all")
@click.option("--ttl", default="5m", help="Time to live for panic mode")
@click.option("--redis-url", default="redis://localhost:6379/0", help="Redis URL")
def panic_block_all(ttl: str, redis_url: str):
    """Enable panic mode to block all transactions."""
    ttl_seconds = parse_ttl(ttl)

    client = redis.from_url(redis_url)
    client.setex("panic", ttl_seconds, PanicMode.BLOCK_ALL)

    click.echo(f"Panic mode enabled: blocking all transactions for {ttl}")


@panic.command("allow-all")
@click.option("--ttl", default="5m", help="Time to live for panic mode")
@click.option("--redis-url", default="redis://localhost:6379/0", help="Redis URL")
def panic_allow_all(ttl: str, redis_url: str):
    """Enable panic mode to allow all transactions."""
    ttl_seconds = parse_ttl(ttl)

    client = redis.from_url(redis_url)
    client.setex("panic", ttl_seconds, PanicMode.ALLOW_ALL)

    click.echo(f"Panic mode enabled: allowing all transactions for {ttl}")


@panic.command("clear")
@click.option(
    "--redis-url", default="redis://localhost:6379/0", help="Redis connection URL"
)
def panic_clear(redis_url: str):
    """Clear panic mode."""
    asyncio.run(_clear_panic_mode(redis_url))


@panic.command("status")
@click.option(
    "--redis-url", default="redis://localhost:6379/0", help="Redis connection URL"
)
def panic_status(redis_url: str):
    """Check panic mode status."""
    asyncio.run(_check_panic_status(redis_url))


async def _set_panic_mode(mode: str, ttl: str, redis_url: str):
    """Set panic mode in Redis with TTL."""
    import redis.asyncio as redis

    # Parse TTL
    ttl_seconds = _parse_ttl(ttl)

    try:
        client = redis.from_url(redis_url)

        # Set panic key with TTL
        await client.setex("panic", ttl_seconds, mode)

        console.print(f"[red]+ Panic mode enabled: {mode}[/red]")
        console.print(f"[yellow]TTL: {ttl} ({ttl_seconds} seconds)[/yellow]")

        # Show warning
        console.print(
            Panel(
                f"[bold red]WARNING: All transactions will be {mode.replace('_', ' ').upper()}[/bold red]\n"
                f"This mode will automatically expire in {ttl}.\n"
                f"Use 'sentr panic clear' to disable immediately.",
                title="Panic Mode Active",
                border_style="red",
            )
        )

        await client.aclose()

    except Exception as e:
        console.print(f"[red]- Failed to set panic mode: {e}[/red]")
        sys.exit(1)


async def _clear_panic_mode(redis_url: str):
    """Clear panic mode from Redis."""
    import redis.asyncio as redis

    try:
        client = redis.from_url(redis_url)

        # Delete panic key
        result = await client.delete("panic")

        if result:
            console.print("[green]+ Panic mode cleared[/green]")
        else:
            console.print("[yellow]No panic mode was active[/yellow]")

        await client.aclose()

    except Exception as e:
        console.print(f"[red]- Failed to clear panic mode: {e}[/red]")
        sys.exit(1)


async def _check_panic_status(redis_url: str):
    """Check current panic mode status."""
    import redis.asyncio as redis

    try:
        client = redis.from_url(redis_url)

        # Get panic key and TTL
        mode = await client.get("panic")

        if mode:
            ttl = await client.ttl("panic")
            console.print(f"[red]Panic mode ACTIVE: {mode.decode()}[/red]")

            if ttl > 0:
                hours, remainder = divmod(ttl, 3600)
                minutes, seconds = divmod(remainder, 60)
                ttl_str = f"{hours}h {minutes}m {seconds}s"
                console.print(f"[yellow]Time remaining: {ttl_str}[/yellow]")
            else:
                console.print("[yellow]Time remaining: Unknown[/yellow]")
        else:
            console.print("[green]Panic mode: INACTIVE[/green]")

        await client.aclose()

    except Exception as e:
        console.print(f"[red]- Failed to check panic status: {e}[/red]")
        sys.exit(1)


def parse_ttl(ttl_str: str) -> int:
    """Parse TTL string like '5m', '1h', '30s' into seconds."""
    match = re.match(r"(\d+)([smh])", ttl_str.lower())
    if not match:
        raise ValueError(f"Invalid TTL format: {ttl_str}")

    value, unit = match.groups()
    value = int(value)

    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:
        raise ValueError(f"Invalid TTL unit: {unit}")


if __name__ == "__main__":
    cli()
