"""Command-line interface for swent."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from swent import __version__
from swent.config import SwentConfig
from swent.core import analyze_project, calculate_entropy
from swent.metrics import EntropyMetrics
from swent.reports import ComprehensiveReporter


console = Console()


def display_metrics(metrics: EntropyMetrics, verbose: bool = False) -> None:
    """Display metrics in a nice formatted way."""
    
    # Create entropy gauge
    entropy_color = "green" if metrics.total_entropy < 0.3 else "yellow" if metrics.total_entropy < 0.6 else "red"
    
    console.print(Panel(
        f"[bold {entropy_color}]Total Entropy: {metrics.total_entropy:.3f}[/bold {entropy_color}]",
        title="Software Entropy Analysis",
        expand=False
    ))
    
    # Summary table
    table = Table(title="Summary Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Total Files", str(metrics.total_files))
    table.add_row("Total Lines", str(metrics.total_lines))
    table.add_row("Average Complexity", f"{metrics.average_complexity:.2f}")
    table.add_row("Code Duplication", f"{metrics.duplication_ratio:.1%}")
    
    if metrics.test_coverage is not None:
        table.add_row("Test Coverage", f"{metrics.test_coverage:.1%}")
    
    table.add_row("Documentation Coverage", f"{metrics.documentation_coverage:.1%}")
    table.add_row("Technical Debt", f"{metrics.technical_debt_hours:.1f} hours")
    
    console.print(table)
    
    if verbose:
        # Entropy components table
        comp_table = Table(title="Entropy Components")
        comp_table.add_column("Component", style="cyan")
        comp_table.add_column("Value", style="white")
        comp_table.add_column("Status", style="white")
        
        components = [
            ("Complexity", metrics.complexity_entropy),
            ("Size", metrics.size_entropy),
            ("Duplication", metrics.duplication_entropy),
            ("Coverage", metrics.coverage_entropy),
            ("Dependencies", metrics.dependency_entropy),
            ("Change Frequency", metrics.change_entropy),
        ]
        
        for name, value in components:
            status_color = "green" if value < 0.3 else "yellow" if value < 0.6 else "red"
            status = "✓ Good" if value < 0.3 else "⚠ Warning" if value < 0.6 else "✗ Poor"
            comp_table.add_row(name, f"{value:.3f}", f"[{status_color}]{status}[/{status_color}]")
        
        console.print(comp_table)


@click.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed metrics")
@click.option("--report", "-r", is_flag=True, help="Generate comprehensive analysis report")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
@click.option("--threshold", "-t", type=float, default=0.6, help="Entropy threshold for failure")
@click.option("--exclude", "-e", multiple=True, help="Patterns to exclude (can be used multiple times)")
@click.option("--init", is_flag=True, help="Generate a default .swentrc.toml configuration file")
@click.version_option(version=__version__)
def main(
    path: str,
    verbose: bool,
    report: bool,
    output_json: bool,
    threshold: float,
    exclude: tuple,
    init: bool,
) -> None:
    """
    Analyze software entropy for a Python project.
    
    PATH is the directory containing the project to analyze.
    """
    # Handle init command
    if init:
        config = SwentConfig(Path(path) if path else Path.cwd())
        config.save_default_config()
        console.print("[green]✓ Created .swentrc.toml configuration file[/green]")
        console.print("[dim]Edit this file to customize swent behavior[/dim]")
        return
    
    # Require path for analysis
    if not path:
        console.print("[red]Error: PATH argument is required for analysis[/red]")
        console.print("[dim]Use --init to generate a configuration file[/dim]")
        sys.exit(1)
    
    try:
        console.print(f"[dim]Analyzing project at {path}...[/dim]")
        
        # Analyze the project
        if report:
            # Get raw data for comprehensive report
            result = analyze_project(path, list(exclude) if exclude else None, return_raw_data=True, verbose=verbose)
            if isinstance(result, tuple):
                metrics, raw_data = result
            else:
                metrics = result
                raw_data = {}
        else:
            result = analyze_project(path, list(exclude) if exclude else None, verbose=verbose)
            if isinstance(result, tuple):
                metrics, raw_data = result
            else:
                metrics = result
                raw_data = {}
        
        # Calculate overall entropy
        metrics.total_entropy = calculate_entropy(metrics)
        
        if output_json:
            # Output as JSON
            if report and raw_data:
                # Include raw data in JSON output
                output = {
                    "summary": metrics.to_dict(),
                    "detailed_analysis": raw_data
                }
                print(json.dumps(output, indent=2))
            else:
                print(json.dumps(metrics.to_dict(), indent=2))
        elif report:
            # Generate comprehensive report
            reporter = ComprehensiveReporter(console)
            reporter.generate_report(metrics, raw_data, path)
        else:
            # Display standard output
            display_metrics(metrics, verbose)
        
        # Exit with error code if entropy exceeds threshold
        if metrics.total_entropy > threshold:
            console.print(
                f"\n[red]✗ Entropy ({metrics.total_entropy:.3f}) "
                f"exceeds threshold ({threshold:.3f})[/red]"
            )
            sys.exit(1)
        else:
            console.print(
                f"\n[green]✓ Entropy ({metrics.total_entropy:.3f}) "
                f"is within threshold ({threshold:.3f})[/green]"
            )
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()