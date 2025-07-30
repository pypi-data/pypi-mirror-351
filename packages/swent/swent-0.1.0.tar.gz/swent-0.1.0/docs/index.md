# swent - Software Entropy Measurement Tool

## What is swent?

**swent** is a comprehensive tool for measuring software entropy in Python projects. It analyzes multiple aspects of code quality and combines them into a single entropy score that quantifies the disorder, complexity, and maintenance burden of your codebase.

## Key Features

- 📊 **Multi-dimensional Analysis**: Examines complexity, duplication, size, dependencies, documentation, and change patterns
- 🎯 **Single Entropy Score**: Combines all metrics into one actionable number (0-1 scale)
- 🔍 **Detailed Insights**: Provides breakdowns of what's contributing to entropy
- 🚀 **CI/CD Ready**: Integrates seamlessly with continuous integration pipelines
- 📈 **Technical Debt Estimation**: Estimates maintenance effort in hours
- 🎨 **Beautiful CLI**: Rich terminal output with colors and formatting

## Quick Example

```bash
# Install swent
pip install swent

# Analyze a project
swent /path/to/project

# Get detailed metrics
swent --verbose /path/to/project

# Set entropy threshold for CI/CD
swent --threshold 0.6 /path/to/project
```

## Understanding Software Entropy

Software entropy is a measure of disorder in code. Like physical entropy, it naturally increases over time unless energy is applied to reduce it. High entropy indicates:

- 🔧 Harder to maintain code
- 🐛 More likely to have bugs
- 💰 Higher cost of changes
- 😰 Increased developer frustration

## How swent Works

1. **Analysis Phase**: Multiple analyzers examine different aspects of your code
2. **Normalization**: Each metric is normalized to a 0-1 scale
3. **Weighted Combination**: Metrics are combined using carefully tuned weights
4. **Actionable Output**: Results are presented with specific recommendations

## Entropy Score Interpretation

| Score | Rating | What it Means |
|-------|--------|---------------|
| 0.0-0.3 | ✅ Excellent | Clean, maintainable code |
| 0.3-0.6 | ⚠️ Warning | Some areas need attention |
| 0.6-1.0 | ❌ Poor | Significant refactoring needed |

## Next Steps

- [Installation Guide](getting-started/installation.md) - Get swent up and running
- [Quick Start](getting-started/quickstart.md) - Start analyzing your first project
- [Understanding Metrics](metrics/overview.md) - Deep dive into what we measure
- [CI/CD Integration](usage/cicd.md) - Add entropy checks to your pipeline