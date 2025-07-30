"""File and project size analysis."""

import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from swent.analyzers.base import BaseAnalyzer


class SizeAnalyzer(BaseAnalyzer):
    """Analyzes file sizes and project structure."""
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None, config: Any = None):
        """Initialize size analyzer."""
        super().__init__(exclude_patterns, config)
        self.size_thresholds = {
            "small": 100,      # < 100 lines
            "medium": 300,     # 100-300 lines  
            "large": 600,      # 300-600 lines
            "very_large": 1000 # 600-1000 lines
            # > 1000 lines is "huge"
        }
    
    def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze file sizes and structure.
        
        Returns dict with:
            - total_files: Number of Python files
            - total_lines: Total lines of code
            - average_file_size: Average lines per file
            - size_distribution: Distribution of file sizes
            - large_files: List of files exceeding thresholds
        """
        python_files = self.find_python_files(project_path)
        
        file_sizes = []
        total_lines = 0
        size_distribution = {
            "small": 0,
            "medium": 0,
            "large": 0,
            "very_large": 0,
            "huge": 0
        }
        large_files = []
        empty_files = []
        
        for file_path in python_files:
            size_info = self._analyze_file_size(file_path, project_path)
            if size_info:
                file_sizes.append(size_info)
                total_lines += size_info["lines"]
                
                # Categorize by size
                lines = size_info["lines"]
                if lines == 0:
                    empty_files.append(size_info["path"])
                elif lines < self.size_thresholds["small"]:
                    size_distribution["small"] += 1
                elif lines < self.size_thresholds["medium"]:
                    size_distribution["medium"] += 1
                elif lines < self.size_thresholds["large"]:
                    size_distribution["large"] += 1
                elif lines < self.size_thresholds["very_large"]:
                    size_distribution["very_large"] += 1
                else:
                    size_distribution["huge"] += 1
                    large_files.append(size_info)
        
        # Sort large files by size
        large_files.sort(key=lambda x: x["lines"], reverse=True)
        
        avg_size = total_lines / len(file_sizes) if file_sizes else 0
        
        # Calculate directory statistics
        dir_stats = self._analyze_directory_structure(python_files, project_path)
        
        return {
            "total_files": len(python_files),
            "total_lines": total_lines,
            "average_file_size": avg_size,
            "size_distribution": size_distribution,
            "large_files": large_files[:10],  # Top 10 largest files
            "empty_files": empty_files,
            "directory_stats": dir_stats,
            "file_sizes": file_sizes,  # All file sizes for detailed analysis
        }
    
    def _analyze_file_size(self, file_path: Path, project_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single file's size metrics."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Count different types of lines
            code_lines = 0
            comment_lines = 0
            blank_lines = 0
            
            in_docstring = False
            docstring_delim: Optional[str] = None
            
            for line in lines:
                stripped = line.strip()
                
                # Handle docstrings
                if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                    in_docstring = True
                    docstring_delim = '"""' if stripped.startswith('"""') else "'''"
                    comment_lines += 1
                    if stripped.endswith(docstring_delim) and len(stripped) > 3:
                        in_docstring = False
                elif in_docstring:
                    comment_lines += 1
                    if docstring_delim is not None and stripped.endswith(docstring_delim):
                        in_docstring = False
                elif not stripped:
                    blank_lines += 1
                elif stripped.startswith("#"):
                    comment_lines += 1
                else:
                    code_lines += 1
            
            # Get file size in bytes
            file_size_bytes = os.path.getsize(file_path)
            
            return {
                "path": str(file_path.relative_to(project_path)),
                "lines": len(lines),
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "bytes": file_size_bytes,
                "comment_ratio": comment_lines / len(lines) if lines else 0,
            }
            
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            return None
    
    def _analyze_directory_structure(self, python_files: List[Path], project_path: Path) -> Dict[str, Any]:
        """Analyze directory structure and nesting."""
        dir_file_count: Dict[str, int] = defaultdict(int)
        max_depth = 0
        
        for file_path in python_files:
            rel_path = file_path.relative_to(project_path)
            
            # Count files per directory
            dir_path = rel_path.parent
            dir_file_count[str(dir_path)] += 1
            
            # Calculate depth
            depth = len(rel_path.parts) - 1
            max_depth = max(max_depth, depth)
        
        # Find directories with many files
        crowded_dirs = []
        for dir_path_str, count in dir_file_count.items():  # type: ignore[assignment]
            if count > 10:  # More than 10 files in a directory
                crowded_dirs.append({
                    "path": str(dir_path_str),
                    "file_count": count
                })
        
        crowded_dirs.sort(key=lambda x: int(x["file_count"]), reverse=True)  # type: ignore[call-overload]
        
        return {
            "max_depth": max_depth,
            "total_directories": len(dir_file_count),
            "average_files_per_dir": sum(dir_file_count.values()) / len(dir_file_count) if dir_file_count else 0,
            "crowded_directories": crowded_dirs[:5],  # Top 5 most crowded
        }