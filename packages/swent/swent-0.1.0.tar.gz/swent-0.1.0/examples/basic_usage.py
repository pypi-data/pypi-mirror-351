#!/usr/bin/env python3
"""Example of using swent as a Python library for basic analysis."""

import sys
from pathlib import Path

from swent import analyze_project


def main():
    """Run entropy analysis on a sample project."""
    # You can analyze any Python project
    # For this example, we'll analyze the parent directory
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        # Default to analyzing swent itself
        project_path = Path(__file__).parent.parent / "src"
    
    print(f"Analyzing project: {project_path}")
    print("-" * 50)
    
    try:
        metrics = analyze_project(project_path)
        
        print(f"Total Entropy: {metrics.total_entropy:.3f}")
        print(f"\nSummary:")
        print(f"  Files: {metrics.total_files}")
        print(f"  Lines: {metrics.total_lines}")
        print(f"  Average Complexity: {metrics.average_complexity:.2f}")
        print(f"  Code Duplication: {metrics.duplication_ratio:.1%}")
        print(f"  Dependencies: {metrics.dependency_count}")
        print(f"  Technical Debt: {metrics.technical_debt_hours:.1f} hours")
        
        print(f"\nEntropy Components:")
        print(f"  Complexity: {metrics.complexity_entropy:.3f}")
        print(f"  Size: {metrics.size_entropy:.3f}")
        print(f"  Duplication: {metrics.duplication_entropy:.3f}")
        print(f"  Coverage: {metrics.coverage_entropy:.3f}")
        print(f"  Dependencies: {metrics.dependency_entropy:.3f}")
        print(f"  Change: {metrics.change_entropy:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()