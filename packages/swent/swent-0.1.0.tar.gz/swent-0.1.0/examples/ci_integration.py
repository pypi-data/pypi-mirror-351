#!/usr/bin/env python3
"""Example of integrating swent into CI/CD pipelines."""

import json
import sys
from pathlib import Path

from swent import analyze_project


def main():
    """Run entropy analysis for CI/CD with JSON output and thresholds."""
    # Configuration
    ENTROPY_THRESHOLD = 0.6
    COMPLEXITY_THRESHOLD = 0.5
    DUPLICATION_THRESHOLD = 0.4
    
    # Get project path from command line or use current directory
    project_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    
    # Run analysis
    metrics = analyze_project(project_path)
    
    # Create detailed report
    report = {
        "project": str(project_path),
        "status": "pass",
        "total_entropy": round(metrics.total_entropy, 3),
        "thresholds": {
            "entropy": ENTROPY_THRESHOLD,
            "complexity": COMPLEXITY_THRESHOLD,
            "duplication": DUPLICATION_THRESHOLD,
        },
        "metrics": metrics.to_dict(),
        "failures": [],
    }
    
    # Check thresholds
    if metrics.total_entropy > ENTROPY_THRESHOLD:
        report["status"] = "fail"
        report["failures"].append({
            "type": "entropy",
            "message": f"Total entropy ({metrics.total_entropy:.3f}) exceeds threshold ({ENTROPY_THRESHOLD})",
            "severity": "error"
        })
    
    if metrics.complexity_entropy > COMPLEXITY_THRESHOLD:
        report["failures"].append({
            "type": "complexity",
            "message": f"Complexity entropy ({metrics.complexity_entropy:.3f}) exceeds threshold ({COMPLEXITY_THRESHOLD})",
            "severity": "warning" if report["status"] == "pass" else "error"
        })
    
    if metrics.duplication_entropy > DUPLICATION_THRESHOLD:
        report["failures"].append({
            "type": "duplication",
            "message": f"Duplication entropy ({metrics.duplication_entropy:.3f}) exceeds threshold ({DUPLICATION_THRESHOLD})",
            "severity": "warning" if report["status"] == "pass" else "error"
        })
    
    # Output JSON report
    print(json.dumps(report, indent=2))
    
    # Exit with appropriate code
    if report["status"] == "fail":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()