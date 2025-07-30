"""Configuration management for swent."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import yaml
import toml


class SwentConfig:
    """Manages configuration for swent analysis."""
    
    # Comprehensive default exclusions for Python projects
    DEFAULT_EXCLUDE_PATTERNS = [
        # Python cache and compiled files
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "*$py.class",
        
        # Build and distribution directories
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "share/python-wheels/",
        "*.egg-info/",
        "*.egg",
        ".installed.cfg",
        "MANIFEST",
        
        # Testing and coverage
        ".tox/",
        ".nox/",
        ".coverage",
        ".coverage.*",
        "htmlcov/",
        ".pytest_cache/",
        "cover/",
        ".hypothesis/",
        "nosetests.xml",
        "coverage.xml",
        "*.cover",
        "*.py,cover",
        
        # Type checking
        ".mypy_cache/",
        ".dmypy.json",
        "dmypy.json",
        ".pyre/",
        ".pytype/",
        
        # Virtual environments
        ".env",
        ".venv",
        "env/",
        "venv/",
        "ENV/",
        "env.bak/",
        "venv.bak/",
        ".python-version",
        
        # Jupyter
        ".ipynb_checkpoints",
        "*.ipynb_checkpoints",
        
        # IDEs and editors
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "*~",
        ".project",
        ".pydevproject",
        ".spyderproject",
        ".spyproject",
        ".ropeproject",
        
        # OS files
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        
        # Documentation builds
        "docs/_build/",
        "site/",
        
        # Package managers
        "pip-log.txt",
        "pip-delete-this-directory.txt",
        ".pdm.toml",
        "__pypackages__/",
        "poetry.lock",
        "Pipfile.lock",
        
        # Profiling
        "*.prof",
        ".prof",
        
        # Installer logs
        "*.log",
        
        # Unit test / coverage reports
        ".cache",
        
        # Translations
        "*.mo",
        "*.pot",
        
        # Django
        "local_settings.py",
        "db.sqlite3",
        "db.sqlite3-journal",
        "*.sqlite3",
        
        # Flask
        "instance/",
        ".webassets-cache",
        
        # Scrapy
        ".scrapy",
        
        # Sphinx
        "docs/_build/",
        
        # PyBuilder
        ".pybuilder/",
        "target/",
        
        # Celery
        "celerybeat-schedule",
        "celerybeat.pid",
        
        # SageMath
        "*.sage.py",
        
        # Spyder
        ".spyderproject",
        ".spyproject",
        
        # mkdocs
        "/site",
        
        # Cython
        "cython_debug/",
        
        # Version control
        ".git/",
        ".svn/",
        ".hg/",
        
        # Backup files
        "*.bak",
        "*.backup",
        "*.tmp",
        
        # Archives
        "*.zip",
        "*.tar",
        "*.tar.gz",
        "*.tgz",
        "*.rar",
        "*.7z",
        
        # Binary files
        "*.so",
        "*.dylib",
        "*.dll",
        "*.exe",
    ]
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "exclude_patterns": DEFAULT_EXCLUDE_PATTERNS,
        "min_duplicate_lines": 6,
        "entropy_thresholds": {
            "good": 0.3,
            "warning": 0.6,
        },
        "weights": {
            "complexity": 0.25,
            "duplication": 0.20,
            "size": 0.15,
            "coverage": 0.15,
            "dependencies": 0.15,
            "change": 0.10,
        },
        "analysis": {
            "git_history_days": 180,
            "max_file_size": 10000,  # Lines
            "complexity_threshold": 10,
        }
    }
    
    def __init__(self, project_path: Optional[Path] = None, verbose: bool = False):
        """Initialize configuration."""
        self.project_path = project_path or Path.cwd()
        self.config = self.DEFAULT_CONFIG.copy()
        self.verbose = verbose
        self.loaded_from = None  # Track where config was loaded from
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from files."""
        # Try different config file locations and formats
        config_files = [
            # Current working directory configs (highest priority)
            Path.cwd() / ".swentrc",
            Path.cwd() / ".swentrc.json",
            Path.cwd() / ".swentrc.yaml",
            Path.cwd() / ".swentrc.yml",
            Path.cwd() / ".swentrc.toml",
            Path.cwd() / "swent.toml",
            # Project-specific configs
            self.project_path / ".swentrc",
            self.project_path / ".swentrc.json",
            self.project_path / ".swentrc.yaml",
            self.project_path / ".swentrc.yml",
            self.project_path / ".swentrc.toml",
            self.project_path / "swent.toml",
            # Home directory configs
            Path.home() / ".swentrc",
            Path.home() / ".config" / "swent" / "config.toml",
        ]
        
        # Remove duplicates while preserving order (in case CWD == project_path)
        seen = set()
        unique_config_files = []
        for config_file in config_files:
            if config_file not in seen:
                seen.add(config_file)
                unique_config_files.append(config_file)
        
        # Load first found config file
        for config_file in unique_config_files:
            if config_file.exists():
                self._load_config_file(config_file)
                self.loaded_from = config_file  # type: ignore[assignment]
                if self.verbose:
                    print(f"Loaded configuration from: {config_file}")
                break
        
        # Check pyproject.toml for tool.swent section
        # First check CWD, then project path
        for base_path in [Path.cwd(), self.project_path]:
            pyproject_path = base_path / "pyproject.toml"
            if pyproject_path.exists() and pyproject_path not in seen:
                self._load_pyproject_config(pyproject_path)
                seen.add(pyproject_path)
    
    def _load_config_file(self, path: Path) -> None:
        """Load configuration from a file."""
        try:
            content = path.read_text()
            
            if path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(content)
            elif path.suffix == ".json" or (path.suffix == "" and content.strip().startswith("{")):
                data = json.loads(content)
            elif path.suffix == ".toml" or path.name == ".swentrc":
                # Try TOML first, fall back to JSON/YAML
                try:
                    data = toml.loads(content)
                except toml.TomlDecodeError:
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        data = yaml.safe_load(content)
            else:
                return
            
            if data:
                self._merge_config(data)
                
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")
    
    def _load_pyproject_config(self, path: Path) -> None:
        """Load configuration from pyproject.toml [tool.swent] section."""
        try:
            data = toml.loads(path.read_text())
            swent_config = data.get("tool", {}).get("swent", {})
            if swent_config:
                self._merge_config(swent_config)
        except Exception as e:
            print(f"Warning: Failed to load config from pyproject.toml: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing."""
        # Handle exclude patterns specially - extend rather than replace
        if "exclude_patterns" in new_config:
            if new_config.get("extend_default_excludes", True):
                # Extend default patterns
                current_patterns = self.config.get("exclude_patterns", [])
                if isinstance(current_patterns, list) and isinstance(new_config["exclude_patterns"], list):
                    current_patterns.extend(new_config["exclude_patterns"])
                    self.config["exclude_patterns"] = current_patterns
            else:
                # Replace default patterns
                self.config["exclude_patterns"] = new_config["exclude_patterns"]
        
        # Merge other configs
        for key, value in new_config.items():
            if key == "exclude_patterns":
                continue  # Already handled
            elif key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                # Merge nested dicts
                self.config[key].update(value)  # type: ignore[attr-defined]
            else:
                # Replace value
                self.config[key] = value
    
    def get_exclude_patterns(self, additional_patterns: Optional[List[str]] = None) -> List[str]:
        """Get combined exclude patterns."""
        base_patterns = self.config.get("exclude_patterns", [])
        patterns = base_patterns.copy() if isinstance(base_patterns, list) else []
        if additional_patterns:
            patterns.extend(additional_patterns)
        return patterns
    
    def get_weight(self, component: str) -> float:
        """Get weight for an entropy component."""
        weights = self.config.get("weights", {})
        return weights.get(component, 0.0) if isinstance(weights, dict) else 0.0
    
    def get_threshold(self, level: str) -> float:
        """Get entropy threshold for a level."""
        thresholds = self.config.get("entropy_thresholds", {})
        return thresholds.get(level, 0.6) if isinstance(thresholds, dict) else 0.6
    
    def save_default_config(self, path: Optional[Path] = None) -> None:
        """Save default configuration to a file."""
        if path is None:
            path = self.project_path / ".swentrc.toml"
        
        config_with_comments = '''# swent configuration file
# 
# This file configures the software entropy analyzer

# Patterns to exclude from analysis
# Set extend_default_excludes = false to replace rather than extend defaults
extend_default_excludes = true
exclude_patterns = [
    # Add your custom exclusions here
    # "vendor/",
    # "third_party/",
]

# Minimum lines for duplicate detection
min_duplicate_lines = 6

# Entropy thresholds
[entropy_thresholds]
good = 0.3     # Below this is good
warning = 0.6  # Below this is warning, above is poor

# Component weights (must sum to 1.0)
[weights]
complexity = 0.25
duplication = 0.20
size = 0.15
coverage = 0.15
dependencies = 0.15
change = 0.10

# Analysis parameters
[analysis]
git_history_days = 180
max_file_size = 10000  # Lines before warning
complexity_threshold = 10  # Cyclomatic complexity threshold
'''
        
        path.write_text(config_with_comments)
        print(f"Default configuration saved to {path}")