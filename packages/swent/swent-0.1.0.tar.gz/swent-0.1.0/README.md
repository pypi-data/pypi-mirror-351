# swent - Software Entropy Measurement Tool

[![PyPI version](https://badge.fury.io/py/swent.svg)](https://badge.fury.io/py/swent)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/swent)](https://pepy.tech/project/swent)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**swent** analyzes Python projects to measure software entropy - a metric that quantifies code complexity, technical debt, and maintenance burden. Like other development tools (pytest, black, flake8), swent integrates into your development workflow to provide actionable feedback on code health.

## Features

- 📊 **Comprehensive Metrics**: Analyzes multiple aspects of code quality
  - Cyclomatic complexity
  - Code duplication
  - File and function sizes
  - Dependency coupling
  - Documentation coverage
  - Test coverage integration
  - Code churn and change frequency

- 🎯 **Single Entropy Score**: Combines all metrics into one actionable number
- 🚦 **CI/CD Integration**: Fail builds when entropy exceeds thresholds
- 📈 **Trend Analysis**: Track entropy changes over time
- 🎨 **Rich CLI Output**: Beautiful, informative terminal displays

## Installation

```bash
pip install swent
```

For development:
```bash
git clone https://github.com/yourusername/swent.git
cd swent
pip install -e ".[dev]"
```

## Quick Start

```bash
# Analyze current directory
swent .

# Analyze with detailed metrics
swent --verbose /path/to/project

# Generate comprehensive report
swent --report /path/to/project

# Set custom threshold
swent --threshold 0.7 .

# Output as JSON for CI/CD pipelines
swent --json . > entropy.json

# Exclude patterns
swent --exclude "**/tests/*" --exclude "**/docs/*" .

# Generate configuration file
swent --init
```

## Understanding Software Entropy

Software entropy measures how "disordered" or difficult to maintain your code has become. A lower score is better:

- **0.0 - 0.3**: ✅ Excellent - Clean, maintainable code
- **0.3 - 0.6**: ⚠️ Warning - Consider refactoring problem areas
- **0.6 - 1.0**: ❌ Poor - High technical debt, needs attention

## Example Output

```
╭─ Software Entropy Analysis ──╮
│ Total Entropy: 0.423        │
╰─────────────────────────────╯

        Summary Metrics        
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric               ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Files          │ 127   │
│ Total Lines          │ 15423 │
│ Average Complexity   │ 3.42  │
│ Code Duplication     │ 2.3%  │
│ Test Coverage        │ 87.5% │
│ Documentation        │ 64.2% │
│ Technical Debt       │ 18.5h │
└──────────────────────┴───────┘

✓ Entropy (0.423) is within threshold (0.600)
```

## Configuration

swent automatically excludes common Python build artifacts (`build/`, `dist/`, `*.egg-info/`, etc.). You can customize behavior with a configuration file:

```bash
# Generate default configuration
swent --init

# Creates .swentrc.toml with all options
```

Example `.swentrc.toml`:
```toml
extend_default_excludes = true
exclude_patterns = ["vendor/", "legacy/"]

[entropy_thresholds]
good = 0.3
warning = 0.6

[weights]
complexity = 0.25
duplication = 0.20
# ... etc
```

See [Configuration Guide](https://swent.readthedocs.io/en/latest/getting-started/configuration/) for details.

## CI/CD Integration

### GitHub Actions

```yaml
- name: Check Software Entropy
  run: |
    pip install swent
    swent --threshold 0.6 .
```

### Pre-commit Hook

```yaml
repos:
  - repo: https://github.com/yourusername/swent
    rev: v0.1.0
    hooks:
      - id: swent
        args: ['--threshold', '0.6']
```

## Roadmap

- [ ] Language support beyond Python (JavaScript, Go, Rust)
- [ ] Historical entropy tracking and visualization
- [ ] IDE integrations (VS Code, PyCharm)
- [ ] Custom metric plugins
- [ ] Entropy prediction based on changes

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Credits

swent was developed with the assistance of Claude (Anthropic) and builds upon excellent open source libraries. See [CREDITS.md](CREDITS.md) for full acknowledgments.

## License

MIT License - see [LICENSE](LICENSE) for details.
