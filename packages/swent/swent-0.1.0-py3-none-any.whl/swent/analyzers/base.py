"""Base analyzer class and utilities."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from swent.config import SwentConfig


class BaseAnalyzer(ABC):
    """Abstract base class for all analyzers."""
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None, config: Optional[SwentConfig] = None):
        """
        Initialize analyzer.
        
        Args:
            exclude_patterns: List of glob patterns to exclude
            config: SwentConfig instance (will create one if not provided)
        """
        self.config = config or SwentConfig()
        # Get exclude patterns from config, with any additional patterns
        self.exclude_patterns = self.config.get_exclude_patterns(exclude_patterns)
    
    @abstractmethod
    def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze the project and return metrics.
        
        Args:
            project_path: Path to project root
            
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    def should_analyze_file(self, file_path: Path) -> bool:
        """Check if a file should be analyzed."""
        # Check against exclude patterns
        for pattern in self.exclude_patterns:
            # Handle both file and directory patterns
            if "/" in pattern:
                # Directory pattern - check full path
                for part in file_path.parts:
                    if Path(part).match(pattern.rstrip("/")):
                        return False
            else:
                # File pattern - check file name and parent directories
                if file_path.match(pattern):
                    return False
                # Also check if any parent directory matches
                for parent in file_path.parents:
                    if parent.name == pattern or parent.match(pattern):
                        return False
        
        # Only analyze Python files for now
        return file_path.suffix == ".py"
    
    def find_python_files(self, project_path: Path) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        
        for file_path in project_path.rglob("*.py"):
            if self.should_analyze_file(file_path):
                python_files.append(file_path)
        
        return python_files