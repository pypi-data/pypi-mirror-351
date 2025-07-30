"""
Sentr-Fraud CLI - Command line interface for fraud detection system.

Provides commands for package information, system status, and rules testing.
"""

import typer
import yaml
from pathlib import Path
from typing import Optional

from . import __version__, get_component_status

# Create the main CLI app
app = typer.Typer(
    name="sentr-guard",
    help="High-performance fraud detection rules engine",
    add_completion=False
)


@app.command()
def version():
    """Show package version and build information."""
    typer.echo(f"sentr-guard version {__version__}")
    typer.echo("High-performance fraud detection rules engine")
    

@app.command()
def status():
    """Show system component status and availability."""
    typer.echo("Sentr-Guard System Status:")
    typer.echo("=" * 40)
    
    status = get_component_status()
    
    # Core components
    rules_status = "✅ Available" if status["rules_engine"] else "❌ Not Available"
    typer.echo(f"Rules Engine:    {rules_status}")
    
    feature_status = "✅ Available" if status["feature_store"] else "❌ Not Available"
    typer.echo(f"Feature Store:   {feature_status}")
    
    monitoring_status = "✅ Available" if status["monitoring"] else "❌ Not Available"
    typer.echo(f"Monitoring:      {monitoring_status}")
    
    typer.echo(f"Version:         {status['version']}")
    
    # Performance info
    if status["rules_engine"]:
        typer.echo("\nPerformance:")
        typer.echo("Rules evaluation: ~4-5µs (P95)")
        typer.echo("Total latency:    ~1ms (including infrastructure)")


@app.command()
def rules(
    file: Optional[Path] = typer.Argument(None, help="YAML rules file to validate"),
    evaluate: bool = typer.Option(False, "--evaluate", "-e", help="Evaluate rules with sample data")
):
    """Validate and optionally evaluate fraud detection rules."""
    
    if not file:
        typer.echo("Please provide a rules file path")
        typer.echo("Example: sentr rules my_rules.yaml")
        raise typer.Exit(1)
    
    if not file.exists():
        typer.echo(f"Error: Rules file '{file}' not found")
        raise typer.Exit(1)
    
    try:
        # Load and validate YAML
        with open(file, 'r') as f:
            rules_data = yaml.safe_load(f)
        
        typer.echo(f"✅ Successfully loaded rules from {file}")
        typer.echo(f"Found {len(rules_data.get('rules', []))} rules")
        
        # Basic validation
        if 'rules' not in rules_data:
            typer.echo("❌ Warning: No 'rules' section found in file")
        
        # Show rule names
        for i, rule in enumerate(rules_data.get('rules', []), 1):
            name = rule.get('name', f'Rule {i}')
            typer.echo(f"  {i}. {name}")
        
        if evaluate:
            typer.echo("\n🧪 Rule evaluation would require full system setup")
            typer.echo("Install with: pip install sentr-fraud[full]")
            
    except yaml.YAMLError as e:
        typer.echo(f"❌ YAML parsing error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main() 