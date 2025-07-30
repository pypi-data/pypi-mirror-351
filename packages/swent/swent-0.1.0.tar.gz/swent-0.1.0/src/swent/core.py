"""Core functionality for software entropy analysis."""

from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

from swent.analyzers import (
    ComplexityAnalyzer,
    DuplicationAnalyzer,
    SizeAnalyzer,
    DependencyAnalyzer,
    DocumentationAnalyzer,
    GitHistoryAnalyzer,
)
from swent.config import SwentConfig
from swent.entropy_calculator import EntropyCalculator
from swent.metrics import EntropyMetrics


def analyze_project(
    project_path: Union[str, Path],
    exclude_patterns: Optional[List[str]] = None,
    return_raw_data: bool = False,
    verbose: bool = False,
) -> Union[EntropyMetrics, Tuple[EntropyMetrics, Dict[str, Any]]]:
    """
    Analyze a project and calculate its software entropy.
    
    Args:
        project_path: Path to the project directory
        exclude_patterns: List of glob patterns to exclude
        return_raw_data: If True, also return raw analyzer data
        verbose: If True, print verbose output
        
    Returns:
        EntropyMetrics object containing all calculated metrics
        If return_raw_data is True, returns tuple of (metrics, raw_data)
    """
    path = Path(project_path)
    if not path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")
    
    # Create configuration
    config = SwentConfig(path, verbose=verbose)
    
    # Initialize analyzers with config
    complexity_analyzer = ComplexityAnalyzer(exclude_patterns, config)
    size_analyzer = SizeAnalyzer(exclude_patterns, config)
    duplication_analyzer = DuplicationAnalyzer(exclude_patterns, config)
    dependency_analyzer = DependencyAnalyzer(exclude_patterns, config)
    documentation_analyzer = DocumentationAnalyzer(exclude_patterns, config)
    git_analyzer = GitHistoryAnalyzer(exclude_patterns, config)
    
    # Run all analyzers
    all_metrics = {
        "complexity": complexity_analyzer.analyze(path),
        "size": size_analyzer.analyze(path),
        "duplication": duplication_analyzer.analyze(path),
        "dependencies": dependency_analyzer.analyze(path),
        "documentation": documentation_analyzer.analyze(path),
        "git_history": git_analyzer.analyze(path),
    }
    
    # Calculate entropy
    calculator = EntropyCalculator(config)
    metrics = calculator.calculate_total_entropy(all_metrics)
    
    if return_raw_data:
        return metrics, all_metrics
    return metrics


def calculate_entropy(metrics: EntropyMetrics) -> float:
    """
    Calculate overall entropy score from individual metrics.
    
    Args:
        metrics: EntropyMetrics object containing individual metrics
        
    Returns:
        Overall entropy score (0.0 = perfect, higher = worse)
    """
    return metrics.total_entropy