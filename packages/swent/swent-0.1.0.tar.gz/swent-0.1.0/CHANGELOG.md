# Changelog

All notable changes to swent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-05-29

### Added
- Initial release of swent - Software Entropy Measurement Tool
- Core entropy calculation combining 6 key metrics:
  - Cyclomatic complexity analysis using radon
  - AST-based code duplication detection
  - File size and structure analysis
  - Dependency coupling metrics
  - Documentation coverage analysis
  - Git history and code churn metrics
- Comprehensive CLI with multiple output formats:
  - Standard summary output
  - Verbose mode with detailed breakdowns
  - Comprehensive report mode with code snippets
  - JSON output for programmatic use
- Flexible configuration system:
  - Supports .swentrc, YAML, JSON, and TOML formats
  - Hierarchical configuration (CWD > project > home)
  - Integration with pyproject.toml
- Smart Python-specific defaults:
  - Automatic exclusion of build artifacts (build/, dist/, *.egg-info/)
  - Handles src/ layout and traditional layouts
  - Detects vendored files with conditional imports
- Technical debt estimation in hours
- CI/CD integration support with configurable thresholds
- Pre-commit hook support
- Beautiful terminal output using Rich
- Comprehensive documentation with MkDocs
- Example scripts for various use cases

### Development
- Co-developed with Claude (Anthropic) AI assistant
- Extensive type hints for better IDE support
- Modular analyzer architecture for extensibility

### Credits
- Built on excellent open source libraries: radon, GitPython, Rich, Click
- Inspired by tools like pytest, black, and flake8

[Unreleased]: https://github.com/chadhanna/swent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/chadhanna/swent/releases/tag/v0.1.0
