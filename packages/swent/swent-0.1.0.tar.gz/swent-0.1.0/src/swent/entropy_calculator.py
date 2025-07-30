"""Entropy calculation formulas and normalization."""

import math
from typing import Dict, Any, Optional

from swent.config import SwentConfig
from swent.metrics import EntropyMetrics


class EntropyCalculator:
    """Calculates software entropy from various metrics."""
    
    def __init__(self, config: Optional[SwentConfig] = None):
        """Initialize entropy calculator with weight configurations."""
        self.config = config or SwentConfig()
        
        # Get weights from config
        self.weights = {
            "complexity": self.config.get_weight("complexity"),
            "size": self.config.get_weight("size"),
            "duplication": self.config.get_weight("duplication"),
            "coverage": self.config.get_weight("coverage"),
            "dependencies": self.config.get_weight("dependencies"),
            "change": self.config.get_weight("change"),
        }
        
        # Normalization parameters for each metric
        self.normalization = {
            "complexity": {"ideal": 3.0, "max": 20.0},
            "file_size": {"ideal": 150, "max": 1000},
            "duplication": {"ideal": 0.02, "max": 0.30},
            "test_coverage": {"ideal": 0.90, "min": 0.20},
            "doc_coverage": {"ideal": 0.80, "min": 0.10},
            "coupling": {"ideal": 2.0, "max": 10.0},
            "churn": {"ideal": 0.1, "max": 0.5},
        }
    
    def calculate_total_entropy(self, all_metrics: Dict[str, Any]) -> EntropyMetrics:
        """
        Calculate total entropy from all analyzer outputs.
        
        Args:
            all_metrics: Dictionary containing results from all analyzers
            
        Returns:
            EntropyMetrics object with calculated entropy values
        """
        metrics = EntropyMetrics()
        
        # Extract data from analyzers
        complexity_data = all_metrics.get("complexity", {})
        size_data = all_metrics.get("size", {})
        duplication_data = all_metrics.get("duplication", {})
        dependency_data = all_metrics.get("dependencies", {})
        documentation_data = all_metrics.get("documentation", {})
        git_data = all_metrics.get("git_history", {})
        
        # Basic metrics
        metrics.total_files = size_data.get("total_files", 0)
        metrics.total_lines = size_data.get("total_lines", 0)
        metrics.average_complexity = complexity_data.get("average_complexity", 0)
        metrics.average_file_size = size_data.get("average_file_size", 0)
        metrics.duplication_ratio = duplication_data.get("duplication_ratio", 0)
        metrics.dependency_count = dependency_data.get("external_dependency_count", 0)
        metrics.documentation_coverage = documentation_data.get("documentation_coverage", 0)
        
        # Calculate individual entropy components
        metrics.complexity_entropy = self._calculate_complexity_entropy(complexity_data)
        metrics.size_entropy = self._calculate_size_entropy(size_data)
        metrics.duplication_entropy = self._calculate_duplication_entropy(duplication_data)
        metrics.coverage_entropy = self._calculate_coverage_entropy(all_metrics)
        metrics.dependency_entropy = self._calculate_dependency_entropy(dependency_data)
        metrics.change_entropy = self._calculate_change_entropy(git_data, metrics.total_files)
        
        # Calculate weighted total entropy
        metrics.total_entropy = (
            self.weights["complexity"] * metrics.complexity_entropy +
            self.weights["size"] * metrics.size_entropy +
            self.weights["duplication"] * metrics.duplication_entropy +
            self.weights["coverage"] * metrics.coverage_entropy +
            self.weights["dependencies"] * metrics.dependency_entropy +
            self.weights["change"] * metrics.change_entropy
        )
        
        # Collect file metrics if available
        if "file_metrics" in complexity_data:
            metrics.files_metrics = complexity_data["file_metrics"]
        
        # Technical debt estimation (in hours)
        metrics.technical_debt_hours = self._estimate_technical_debt(metrics)
        
        return metrics
    
    def _calculate_complexity_entropy(self, complexity_data: Dict[str, Any]) -> float:
        """Calculate entropy from complexity metrics."""
        avg_complexity = complexity_data.get("average_complexity", 0)
        distribution = complexity_data.get("complexity_distribution", {})
        
        # Normalize average complexity
        complexity_norm = self.normalization.get("complexity", {})
        if isinstance(complexity_norm, dict):
            ideal = complexity_norm.get("ideal", 3.0)
            max_val = complexity_norm.get("max", 20.0)
        else:
            ideal, max_val = 3.0, 20.0
        complexity_score = self._normalize_metric(avg_complexity, ideal, max_val)
        
        # Factor in distribution (penalize many complex files)
        complex_count = distribution.get("complex", 0) + distribution.get("very_complex", 0)
        total_count = sum(distribution.values()) if isinstance(distribution, dict) else 1
        complex_ratio = complex_count / max(1, total_count)
        
        # Combine metrics
        return 0.7 * complexity_score + 0.3 * complex_ratio  # type: ignore[no-any-return]
    
    def _calculate_size_entropy(self, size_data: Dict[str, Any]) -> float:
        """Calculate entropy from size metrics."""
        avg_size = size_data.get("average_file_size", 0)
        distribution = size_data.get("size_distribution", {})
        
        # Normalize average file size
        size_norm = self.normalization.get("file_size", {})
        if isinstance(size_norm, dict):
            ideal = size_norm.get("ideal", 150)
            max_val = size_norm.get("max", 1000)
        else:
            ideal, max_val = 150, 1000
        size_score = self._normalize_metric(avg_size, ideal, max_val)
        
        # Factor in distribution (penalize many large files)
        large_count = distribution.get("very_large", 0) + distribution.get("huge", 0)
        total_count = sum(distribution.values()) if isinstance(distribution, dict) else 1
        large_ratio = large_count / max(1, total_count)
        
        # Check directory structure
        dir_stats = size_data.get("directory_stats", {})
        depth_penalty = min(1.0, dir_stats.get("max_depth", 0) / 10)  # Penalize deep nesting
        
        # Combine metrics
        return 0.5 * size_score + 0.3 * large_ratio + 0.2 * depth_penalty  # type: ignore[no-any-return]
    
    def _calculate_duplication_entropy(self, duplication_data: Dict[str, Any]) -> float:
        """Calculate entropy from duplication metrics."""
        dup_ratio = duplication_data.get("duplication_ratio", 0)
        
        # Normalize duplication ratio
        dup_norm = self.normalization.get("duplication", {})
        if isinstance(dup_norm, dict):
            ideal = dup_norm.get("ideal", 0.02)
            max_val = dup_norm.get("max", 0.30)
        else:
            ideal, max_val = 0.02, 0.30
        return self._normalize_metric(dup_ratio, ideal, max_val)  # type: ignore[no-any-return]
    
    def _calculate_coverage_entropy(self, all_metrics: Dict[str, Any]) -> float:
        """Calculate entropy from coverage metrics."""
        # Get documentation coverage
        doc_data = all_metrics.get("documentation", {})
        doc_coverage = doc_data.get("documentation_coverage", 0.0)
        
        # Get maintainability index as code quality proxy
        complexity_data = all_metrics.get("complexity", {})
        file_metrics = complexity_data.get("file_metrics", [])
        
        if file_metrics:
            # Calculate average maintainability index (0-100, higher is better)
            avg_maintainability = sum(f.maintainability_index for f in file_metrics) / len(file_metrics)
            # Convert to score (0-1, higher is better)
            maintainability_score = avg_maintainability / 100.0
        else:
            maintainability_score = 0.5  # Default middle value
        
        # Combine documentation and maintainability
        # Both are "higher is better" so we need to invert for entropy
        doc_entropy = 1.0 - doc_coverage
        maintainability_entropy = 1.0 - maintainability_score
        
        # Weight documentation more heavily
        return 0.6 * doc_entropy + 0.4 * maintainability_entropy  # type: ignore[no-any-return]
    
    def _calculate_dependency_entropy(self, dependency_data: Dict[str, Any]) -> float:
        """Calculate entropy from dependency metrics."""
        coupling_metrics = dependency_data.get("coupling_metrics", {})
        avg_coupling = coupling_metrics.get("average_coupling", 0)
        circular_deps = len(dependency_data.get("circular_dependencies", []))
        
        # Normalize coupling
        coupling_norm = self.normalization.get("coupling", {})
        if isinstance(coupling_norm, dict):
            ideal = coupling_norm.get("ideal", 2.0)
            max_val = coupling_norm.get("max", 10.0)
        else:
            ideal, max_val = 2.0, 10.0
        coupling_score = self._normalize_metric(avg_coupling, ideal, max_val)
        
        # Penalize circular dependencies heavily
        circular_penalty = min(1.0, circular_deps * 0.2)
        
        # Combine metrics
        return 0.7 * coupling_score + 0.3 * circular_penalty
    
    def _calculate_change_entropy(self, git_data: Dict[str, Any], total_files: int) -> float:
        """Calculate entropy from change frequency."""
        if not git_data.get("is_git_repo", False) or total_files == 0:
            return 0.0  # No git data available
        
        # Calculate churn ratio
        files_changed = git_data.get("files_changed", 0)
        churn_ratio = files_changed / total_files
        
        # Normalize churn
        churn_norm = self.normalization.get("churn", {})
        if isinstance(churn_norm, dict):
            ideal = churn_norm.get("ideal", 0.1)
            max_val = churn_norm.get("max", 0.5)
        else:
            ideal, max_val = 0.1, 0.5
        churn_score = self._normalize_metric(churn_ratio, ideal, max_val)
        
        # Factor in stability
        stability_ratio = git_data.get("stability_ratio", 1.0)
        instability_score = 1.0 - stability_ratio
        
        # Combine metrics
        return 0.6 * churn_score + 0.4 * instability_score  # type: ignore[no-any-return]
    
    def _normalize_metric(self, value: float, ideal: float, max_val: float) -> float:
        """
        Normalize a metric to 0-1 range using logarithmic scaling.
        
        0 = ideal value
        1 = max (worst) value
        """
        if value <= ideal:
            return 0.0
        
        if value >= max_val:
            return 1.0
        
        # Logarithmic scaling for smooth progression
        ratio = (value - ideal) / (max_val - ideal)
        return math.log1p(ratio * math.e) / math.log1p(math.e)
    
    def _estimate_technical_debt(self, metrics: EntropyMetrics) -> float:
        """
        Estimate technical debt in hours based on entropy.
        
        This is a rough estimation based on industry averages.
        """
        base_hours_per_file = 0.5  # Base maintenance time per file
        
        # Calculate debt multiplier based on entropy
        debt_multiplier = 1.0 + (metrics.total_entropy * 10)  # 1x to 11x
        
        # Factor in specific issues
        complexity_debt = metrics.complexity_entropy * metrics.total_files * 2.0
        duplication_debt = metrics.duplication_entropy * metrics.total_lines / 100 * 1.5
        dependency_debt = metrics.dependency_entropy * metrics.dependency_count * 3.0
        
        total_debt = (
            metrics.total_files * base_hours_per_file * debt_multiplier +
            complexity_debt +
            duplication_debt +
            dependency_debt
        )
        
        return total_debt