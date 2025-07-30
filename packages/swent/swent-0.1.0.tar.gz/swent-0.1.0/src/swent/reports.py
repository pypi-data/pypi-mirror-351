"""Comprehensive report generation for swent analysis."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.tree import Tree
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich import box

from swent.metrics import EntropyMetrics


class ComprehensiveReporter:
    """Generates detailed reports for entropy analysis."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize reporter with console."""
        self.console = console or Console()
    
    def generate_report(self, metrics: EntropyMetrics, all_data: Dict[str, Any], project_path: str) -> None:
        """Generate comprehensive report with all analysis details."""
        self.console.print("\n")
        
        # Header
        self._print_header(metrics, project_path)
        
        # Executive Summary
        self._print_executive_summary(metrics, all_data)
        
        # Detailed sections
        self._print_duplication_report(all_data.get("duplication", {}))
        self._print_complexity_report(all_data.get("complexity", {}))
        self._print_size_report(all_data.get("size", {}))
        self._print_dependency_report(all_data.get("dependencies", {}))
        self._print_documentation_report(all_data.get("documentation", {}))
        self._print_git_history_report(all_data.get("git_history", {}))
        
        # Recommendations
        self._print_recommendations(metrics, all_data)
    
    def _print_header(self, metrics: EntropyMetrics, project_path: str) -> None:
        """Print report header."""
        header = Panel(
            f"[bold cyan]Software Entropy Comprehensive Report[/bold cyan]\n"
            f"Project: {project_path}\n"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold]Total Entropy: {metrics.total_entropy:.3f}[/bold]",
            title="swent Analysis Report",
            expand=False
        )
        self.console.print(header)
    
    def _print_executive_summary(self, metrics: EntropyMetrics, all_data: Dict[str, Any]) -> None:
        """Print executive summary."""
        self.console.print("\n[bold cyan]Executive Summary[/bold cyan]")
        
        # Create summary table
        table = Table(box=box.ROUNDED)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white", width=15)
        table.add_column("Status", width=12)
        table.add_column("Entropy", style="yellow", width=10)
        
        # Add rows with color coding
        components = [
            ("Complexity", f"{metrics.average_complexity:.2f}", metrics.complexity_entropy, "CC/function"),
            ("Duplication", f"{metrics.duplication_ratio:.1%}", metrics.duplication_entropy, "ratio"),
            ("File Size", f"{metrics.average_file_size:.0f}", metrics.size_entropy, "lines/file"),
            ("Documentation", f"{metrics.documentation_coverage:.1%}", metrics.coverage_entropy, "coverage"),
            ("Dependencies", f"{metrics.dependency_count}", metrics.dependency_entropy, "external"),
            ("Code Churn", f"{all_data.get('git_history', {}).get('commit_frequency', 0):.1f}", metrics.change_entropy, "commits/week"),
        ]
        
        for name, value, entropy, unit in components:
            status_color = "green" if entropy < 0.3 else "yellow" if entropy < 0.6 else "red"
            status = "✓ Good" if entropy < 0.3 else "⚠ Warning" if entropy < 0.6 else "✗ Poor"
            
            table.add_row(
                name,
                f"{value} {unit}",
                f"[{status_color}]{status}[/{status_color}]",
                f"{entropy:.3f}"
            )
        
        self.console.print(table)
        
        # Technical debt
        debt_color = "green" if metrics.technical_debt_hours < 100 else "yellow" if metrics.technical_debt_hours < 500 else "red"
        self.console.print(f"\n[bold]Technical Debt:[/bold] [{debt_color}]{metrics.technical_debt_hours:.1f} hours[/{debt_color}]")
    
    def _print_duplication_report(self, duplication_data: Dict[str, Any]) -> None:
        """Print detailed duplication report."""
        self.console.print("\n[bold cyan]Code Duplication Analysis[/bold cyan]")
        
        if not duplication_data:
            self.console.print("[dim]No duplication data available[/dim]")
            return
        
        # Summary statistics
        summary = duplication_data.get("duplication_summary", {})
        if summary:
            summary_table = Table(title="Duplication Summary", box=box.SIMPLE)
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="white")
            
            summary_table.add_row("Total Duplicated Blocks", str(summary.get("total_duplicated_blocks", 0)))
            summary_table.add_row("Total Duplicated Lines", str(summary.get("total_duplicated_lines", 0)))
            summary_table.add_row("Files Affected", str(summary.get("files_affected", 0)))
            summary_table.add_row("Max Duplications", str(summary.get("max_duplications", 0)))
            
            self.console.print(summary_table)
        
        # Categories
        categories = summary.get("duplication_categories", {})
        if categories:
            cat_table = Table(title="Duplication Categories", box=box.SIMPLE)
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Count", style="white")
            
            cat_table.add_row("Small (6-20 lines)", str(categories.get("small", 0)))
            cat_table.add_row("Medium (21-50 lines)", str(categories.get("medium", 0)))
            cat_table.add_row("Large (51-100 lines)", str(categories.get("large", 0)))
            cat_table.add_row("Very Large (100+ lines)", str(categories.get("very_large", 0)))
            cat_table.add_row("High Impact (3+ copies)", str(categories.get("high_impact", 0)))
            
            self.console.print(cat_table)
        
        # Hotspot files
        hotspots = duplication_data.get("duplication_hotspots", [])
        if hotspots:
            self.console.print("\n[bold]Duplication Hotspots:[/bold]")
            hotspot_table = Table(box=box.SIMPLE)
            hotspot_table.add_column("File", style="cyan", width=40)
            hotspot_table.add_column("Dup Lines", style="yellow", width=10)
            hotspot_table.add_column("Total Lines", style="white", width=12)
            hotspot_table.add_column("Dup %", style="red", width=8)
            
            for hotspot in hotspots[:5]:  # Top 5
                hotspot_table.add_row(
                    hotspot["file"],
                    str(hotspot["duplicated_lines"]),
                    str(hotspot["total_lines"]),
                    f"{hotspot['duplication_percentage']:.1f}%"
                )
            
            self.console.print(hotspot_table)
        
        # Detailed duplicated blocks
        blocks = duplication_data.get("duplicated_blocks", [])
        if blocks:
            self.console.print("\n[bold]Top Duplicated Code Blocks:[/bold]")
            
            for i, block in enumerate(blocks[:5], 1):  # Top 5 duplications
                # Block header
                self.console.print(f"\n[yellow]#{i} Duplication[/yellow] - {block['type']}: {block['name']}")
                self.console.print(f"Impact: {block['lines']} lines × {block['occurrences']} occurrences = {block['impact_score']} total lines")
                
                # Locations
                self.console.print("Locations:")
                for loc in block["locations"]:
                    self.console.print(f"  • {loc['file']}:{loc['start_line']}-{loc['end_line']}")
                
                # Code snippet
                if "code_snippet" in block:
                    self.console.print("\nCode snippet:")
                    syntax = Syntax(
                        block["code_snippet"], 
                        "python", 
                        theme="monokai",
                        line_numbers=True,
                        start_line=block["locations"][0]["start_line"]
                    )
                    self.console.print(syntax)
    
    def _print_complexity_report(self, complexity_data: Dict[str, Any]) -> None:
        """Print detailed complexity report."""
        self.console.print("\n[bold cyan]Complexity Analysis[/bold cyan]")
        
        if not complexity_data:
            self.console.print("[dim]No complexity data available[/dim]")
            return
        
        # Distribution
        dist = complexity_data.get("complexity_distribution", {})
        if dist:
            dist_table = Table(title="Complexity Distribution", box=box.SIMPLE)
            dist_table.add_column("Category", style="cyan")
            dist_table.add_column("Files", style="white")
            dist_table.add_column("Percentage", style="yellow")
            
            total = sum(dist.values())
            for category, count in [
                ("Simple (CC ≤ 5)", dist.get("simple", 0)),
                ("Moderate (CC ≤ 10)", dist.get("moderate", 0)),
                ("Complex (CC ≤ 20)", dist.get("complex", 0)),
                ("Very Complex (CC > 20)", dist.get("very_complex", 0)),
            ]:
                percentage = (count / total * 100) if total > 0 else 0
                dist_table.add_row(category, str(count), f"{percentage:.1f}%")
            
            self.console.print(dist_table)
        
        # High complexity files
        high_complexity = complexity_data.get("high_complexity_files", [])
        if high_complexity:
            self.console.print("\n[bold]High Complexity Files:[/bold]")
            complex_table = Table(box=box.SIMPLE)
            complex_table.add_column("File", style="cyan", width=40)
            complex_table.add_column("Complexity", style="red", width=12)
            complex_table.add_column("Maintainability", style="yellow", width=15)
            
            for file_info in high_complexity[:10]:  # Top 10
                mi_color = "green" if file_info["maintainability"] >= 85 else "yellow" if file_info["maintainability"] >= 65 else "red"
                complex_table.add_row(
                    file_info["path"],
                    f"{file_info['complexity']:.1f}",
                    f"[{mi_color}]{file_info['maintainability']:.1f}[/{mi_color}]"
                )
            
            self.console.print(complex_table)
    
    def _print_recommendations(self, metrics: EntropyMetrics, all_data: Dict[str, Any]) -> None:
        """Print actionable recommendations."""
        self.console.print("\n[bold cyan]Recommendations[/bold cyan]")
        
        recommendations = []
        
        # Based on entropy components
        if metrics.complexity_entropy > 0.6:
            recommendations.append(("High", "Refactor complex functions", "Break down functions with CC > 10"))
        elif metrics.complexity_entropy > 0.3:
            recommendations.append(("Medium", "Reduce complexity", "Simplify conditional logic in hot paths"))
        
        if metrics.duplication_entropy > 0.6:
            recommendations.append(("High", "Eliminate duplication", "Extract common code into shared utilities"))
        elif metrics.duplication_entropy > 0.3:
            recommendations.append(("Medium", "Reduce duplication", "Consider DRY principle for repeated patterns"))
        
        if metrics.coverage_entropy > 0.6:
            recommendations.append(("High", "Add documentation", "Document all public APIs and complex logic"))
        elif metrics.coverage_entropy > 0.3:
            recommendations.append(("Medium", "Improve documentation", "Add docstrings to key functions"))
        
        if metrics.dependency_entropy > 0.6:
            recommendations.append(("High", "Reduce coupling", "Break circular dependencies and decouple modules"))
        
        if metrics.size_entropy > 0.6:
            recommendations.append(("High", "Split large files", "Break files > 500 lines into smaller modules"))
        
        # Display recommendations
        if recommendations:
            rec_table = Table(box=box.ROUNDED)
            rec_table.add_column("Priority", style="bold", width=10)
            rec_table.add_column("Action", style="cyan", width=25)
            rec_table.add_column("Details", style="white", width=45)
            
            # Sort by priority
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            recommendations.sort(key=lambda x: priority_order.get(x[0], 3))
            
            for priority, action, details in recommendations:
                color = "red" if priority == "High" else "yellow" if priority == "Medium" else "green"
                rec_table.add_row(f"[{color}]{priority}[/{color}]", action, details)
            
            self.console.print(rec_table)
        else:
            self.console.print("[green]✓ No critical issues found. Keep maintaining good practices![/green]")
    
    def _print_size_report(self, size_data: Dict[str, Any]) -> None:
        """Print size analysis details."""
        # Implementation for size report
        pass
    
    def _print_dependency_report(self, dependency_data: Dict[str, Any]) -> None:
        """Print dependency analysis details."""
        # Implementation for dependency report
        pass
    
    def _print_documentation_report(self, documentation_data: Dict[str, Any]) -> None:
        """Print documentation coverage details."""
        # Implementation for documentation report
        pass
    
    def _print_git_history_report(self, git_data: Dict[str, Any]) -> None:
        """Print git history analysis details."""
        # Implementation for git history report
        pass