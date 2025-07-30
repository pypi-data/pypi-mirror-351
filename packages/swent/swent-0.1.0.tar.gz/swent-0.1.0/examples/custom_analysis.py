#!/usr/bin/env python3
"""Example of custom swent analysis with specific configuration."""

import sys
from pathlib import Path

from swent import analyze_project
from swent.config import SwentConfig


def main():
    """Run custom entropy analysis with specific thresholds."""
    if len(sys.argv) < 2:
        print("Usage: python custom_analysis.py <project_path>")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    
    # Create custom configuration
    config = SwentConfig(project_path)
    
    # Customize thresholds
    config.config["entropy_thresholds"]["good"] = 0.25
    config.config["entropy_thresholds"]["warning"] = 0.5
    
    # Add custom exclusions
    custom_excludes = ["*_generated.py", "migrations/", "vendor/"]
    
    print(f"Analyzing with custom configuration...")
    print(f"Good threshold: {config.get_threshold('good')}")
    print(f"Warning threshold: {config.get_threshold('warning')}")
    print("-" * 50)
    
    # Analyze with custom configuration
    metrics = analyze_project(project_path, exclude_patterns=custom_excludes)
    
    # Check against custom thresholds
    if metrics.total_entropy < config.get_threshold('good'):
        status = "✅ EXCELLENT"
        color = "\033[92m"  # Green
    elif metrics.total_entropy < config.get_threshold('warning'):
        status = "⚠️  WARNING"
        color = "\033[93m"  # Yellow
    else:
        status = "❌ POOR"
        color = "\033[91m"  # Red
    
    reset_color = "\033[0m"
    
    print(f"\n{color}Status: {status}{reset_color}")
    print(f"Total Entropy: {metrics.total_entropy:.3f}")
    
    # Show which components are contributing most to entropy
    components = [
        ("Complexity", metrics.complexity_entropy),
        ("Duplication", metrics.duplication_entropy),
        ("Size", metrics.size_entropy),
        ("Coverage", metrics.coverage_entropy),
        ("Dependencies", metrics.dependency_entropy),
        ("Change", metrics.change_entropy),
    ]
    
    print("\nTop entropy contributors:")
    for name, value in sorted(components, key=lambda x: x[1], reverse=True)[:3]:
        print(f"  {name}: {value:.3f}")
    
    # Actionable recommendations
    print("\nRecommendations:")
    if metrics.complexity_entropy > 0.5:
        print("  - Refactor complex functions (cyclomatic complexity > 10)")
    if metrics.duplication_entropy > 0.5:
        print("  - Extract duplicated code into shared utilities")
    if metrics.coverage_entropy > 0.5:
        print("  - Add documentation to public APIs")
    if metrics.dependency_entropy > 0.5:
        print("  - Reduce coupling between modules")


if __name__ == "__main__":
    main()