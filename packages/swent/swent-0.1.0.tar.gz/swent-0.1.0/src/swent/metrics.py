"""Metrics collection and data structures."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FileMetrics:
    """Metrics for a single file."""
    
    path: str
    lines_of_code: int = 0
    cyclomatic_complexity: float = 0.0
    maintainability_index: float = 100.0
    halstead_metrics: Dict[str, float] = field(default_factory=dict)
    coupling: int = 0
    cohesion: float = 0.0
    test_coverage: Optional[float] = None
    documentation_coverage: float = 0.0
    code_duplication: float = 0.0
    last_modified_days: int = 0
    change_frequency: int = 0


@dataclass
class EntropyMetrics:
    """Container for all project entropy metrics."""
    
    total_files: int = 0
    total_lines: int = 0
    average_complexity: float = 0.0
    average_file_size: float = 0.0
    duplication_ratio: float = 0.0
    test_coverage: Optional[float] = None
    documentation_coverage: float = 0.0
    dependency_count: int = 0
    outdated_dependencies: int = 0
    code_smells: int = 0
    technical_debt_hours: float = 0.0
    files_metrics: List[FileMetrics] = field(default_factory=list)
    
    # Entropy components (normalized 0-1)
    complexity_entropy: float = 0.0
    size_entropy: float = 0.0
    duplication_entropy: float = 0.0
    coverage_entropy: float = 0.0
    dependency_entropy: float = 0.0
    change_entropy: float = 0.0
    
    # Overall entropy score
    total_entropy: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            "summary": {
                "total_files": self.total_files,
                "total_lines": self.total_lines,
                "average_complexity": round(self.average_complexity, 2),
                "average_file_size": round(self.average_file_size, 2),
                "duplication_ratio": round(self.duplication_ratio, 3),
                "test_coverage": round(self.test_coverage, 2) if self.test_coverage else None,
                "documentation_coverage": round(self.documentation_coverage, 2),
                "dependency_count": self.dependency_count,
                "outdated_dependencies": self.outdated_dependencies,
                "code_smells": self.code_smells,
                "technical_debt_hours": round(self.technical_debt_hours, 1),
            },
            "entropy_components": {
                "complexity": round(self.complexity_entropy, 3),
                "size": round(self.size_entropy, 3),
                "duplication": round(self.duplication_entropy, 3),
                "coverage": round(self.coverage_entropy, 3),
                "dependency": round(self.dependency_entropy, 3),
                "change": round(self.change_entropy, 3),
            },
            "total_entropy": round(self.total_entropy, 3),
        }