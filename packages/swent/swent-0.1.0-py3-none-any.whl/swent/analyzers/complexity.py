"""Complexity analysis using radon and other metrics."""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze

from swent.analyzers.base import BaseAnalyzer
from swent.metrics import FileMetrics


class ComplexityAnalyzer(BaseAnalyzer):
    """Analyzes code complexity metrics."""
    
    # No custom __init__ needed, uses BaseAnalyzer's __init__
    
    def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze complexity metrics for all Python files.
        
        Returns dict with:
            - file_metrics: List of FileMetrics objects
            - average_complexity: Average cyclomatic complexity
            - total_complexity: Sum of all complexities
            - complexity_distribution: Dict of complexity ranges
        """
        python_files = self.find_python_files(project_path)
        file_metrics_list = []
        total_complexity = 0.0
        complexity_distribution = {
            "simple": 0,      # 1-5
            "moderate": 0,    # 6-10
            "complex": 0,     # 11-20
            "very_complex": 0 # 21+
        }
        
        for file_path in python_files:
            metrics = self._analyze_file(file_path, project_path)
            if metrics:
                file_metrics_list.append(metrics)
                total_complexity += metrics.cyclomatic_complexity
                
                # Update distribution
                if metrics.cyclomatic_complexity <= 5:
                    complexity_distribution["simple"] += 1
                elif metrics.cyclomatic_complexity <= 10:
                    complexity_distribution["moderate"] += 1
                elif metrics.cyclomatic_complexity <= 20:
                    complexity_distribution["complex"] += 1
                else:
                    complexity_distribution["very_complex"] += 1
        
        avg_complexity = total_complexity / len(file_metrics_list) if file_metrics_list else 0.0
        
        return {
            "file_metrics": file_metrics_list,
            "average_complexity": avg_complexity,
            "total_complexity": total_complexity,
            "complexity_distribution": complexity_distribution,
            "high_complexity_files": self._find_high_complexity_files(file_metrics_list),
        }
    
    def _analyze_file(self, file_path: Path, project_path: Path) -> Optional[FileMetrics]:
        """Analyze a single Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Get raw metrics
            raw_metrics = analyze(content)
            
            # Get cyclomatic complexity
            cc_blocks = cc_visit(content)
            file_complexity = sum(block.complexity for block in cc_blocks)
            avg_block_complexity = file_complexity / len(cc_blocks) if cc_blocks else 0
            
            # Get maintainability index (0-100, higher is better)
            mi = mi_visit(content, multi=True)
            
            # Radon returns MI as a float, but can be None for empty files
            if mi is None:
                # For empty or trivial files, use a default good score
                mi = 100.0 if raw_metrics.loc == 0 else 50.0
            
            # Get Halstead metrics
            halstead = h_visit(content)
            halstead_metrics = {}
            
            if halstead and halstead.total:
                halstead_metrics = {
                    "volume": halstead.total.volume,
                    "difficulty": halstead.total.difficulty,
                    "effort": halstead.total.effort,
                    "bugs": halstead.total.bugs,
                    "time": halstead.total.time,  # Time to program in seconds
                }
            
            return FileMetrics(
                path=str(file_path.relative_to(project_path)),
                lines_of_code=raw_metrics.loc,
                cyclomatic_complexity=avg_block_complexity,
                maintainability_index=float(mi),  # Ensure it's a float
                halstead_metrics=halstead_metrics,
            )
            
        except Exception as e:
            # Skip files that can't be parsed
            print(f"Warning: Could not analyze {file_path}: {e}")
            return None
    
    def _find_high_complexity_files(self, file_metrics: List[FileMetrics], threshold: float = 10.0) -> List[Dict[str, Any]]:
        """Find files with high complexity."""
        high_complexity = []
        
        for metrics in file_metrics:
            if metrics.cyclomatic_complexity > threshold:
                high_complexity.append({
                    "path": metrics.path,
                    "complexity": metrics.cyclomatic_complexity,
                    "maintainability": metrics.maintainability_index,
                })
        
        # Sort by complexity descending
        high_complexity.sort(key=lambda x: int(x["complexity"]), reverse=True)  # type: ignore[call-overload]
        return high_complexity[:10]  # Top 10 most complex files