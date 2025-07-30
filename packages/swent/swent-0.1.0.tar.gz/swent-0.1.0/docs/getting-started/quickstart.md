# Quick Start Guide

Get up and running with swent in minutes!

## Installation

```bash
pip install swent
```

For development:
```bash
git clone https://git.ligo.org/greg/swent.git
cd swent
pip install -e ".[dev]"
```

## Basic Usage

### Analyze Current Directory
```bash
swent .
```

### Analyze Specific Project
```bash
swent /path/to/project
```

### Verbose Output
```bash
swent --verbose /path/to/project
```

## Understanding Output

### Basic Output
```
╭─ Software Entropy Analysis ──╮
│ Total Entropy: 0.423         │
╰──────────────────────────────╯

        Summary Metrics        
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric               ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Files          │ 127   │
│ Total Lines          │ 15423 │
│ Average Complexity   │ 3.42  │
│ Code Duplication     │ 2.3%  │
│ Documentation        │ 64.2% │
│ Technical Debt       │ 18.5h │
└──────────────────────┴───────┘

✓ Entropy (0.423) is within threshold (0.600)
```

### Verbose Output
Includes entropy component breakdown:
```
      Entropy Components      
┏━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━┓
┃ Component       ┃ Value┃ Status  ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━┩
│ Complexity      │ 0.31 │ ⚠ Warning│
│ Size            │ 0.18 │ ✓ Good  │
│ Duplication     │ 0.42 │ ⚠ Warning│
│ Coverage        │ 0.52 │ ⚠ Warning│
│ Dependencies    │ 0.23 │ ✓ Good  │
│ Change Frequency│ 0.20 │ ✓ Good  │
└─────────────────┴──────┴─────────┘
```

## Common Options

### Set Entropy Threshold
Fail if entropy exceeds threshold (useful for CI/CD):
```bash
swent --threshold 0.5 .
```

### Exclude Patterns
Skip certain files or directories:
```bash
swent --exclude "**/tests/*" --exclude "**/vendor/*" .
```

### JSON Output
For programmatic use:
```bash
swent --json . > entropy.json
```

### Show Version
```bash
swent --version
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Entropy Check
on: [push, pull_request]

jobs:
  entropy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install swent
      - run: swent --threshold 0.6 .
```

### GitLab CI
```yaml
entropy:
  image: python:3.10
  script:
    - pip install swent
    - swent --threshold 0.6 .
  only:
    - merge_requests
    - main
```

### Pre-commit Hook
`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://git.ligo.org/greg/swent
    rev: v0.1.0
    hooks:
      - id: swent
        args: ['--threshold', '0.6']
```

## Next Steps

1. **Deep Dive**: Read about [individual metrics](../metrics/overview.md)
2. **Customize**: Learn about [configuration options](configuration.md)
3. **Integrate**: Set up [CI/CD integration](../usage/cicd.md)
4. **Contribute**: Check out [development guide](../contributing/setup.md)

## Troubleshooting

### "Project path does not exist"
Ensure you're providing a valid path to a directory containing Python files.

### No output / 0 files analyzed
Check that:
- Directory contains `.py` files
- Files aren't excluded by default patterns (e.g., `__pycache__`)
- You have read permissions

### High entropy score
See [Interpreting Results](../concepts/interpreting-results.md) for guidance on improving your score.