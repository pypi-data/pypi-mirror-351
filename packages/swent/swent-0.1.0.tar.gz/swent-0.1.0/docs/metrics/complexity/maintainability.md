# Maintainability Index

## Overview

The Maintainability Index (MI) is a composite metric that provides a single score indicating how maintainable code is. It ranges from 0 to 100, with higher values indicating better maintainability.

## Formula

The Maintainability Index is calculated using:

$$MI = MAX\left(0, \left(171 - 5.2 \ln(V) - 0.23 \cdot CC - 16.2 \ln(LOC)\right) \cdot \frac{100}{171}\right)$$

Where:
- **V** = Halstead Volume
- **CC** = Cyclomatic Complexity
- **LOC** = Lines of Code (source lines, excluding blanks/comments)

### With Comments (Microsoft Enhanced Formula)

$$MI = MAX\left(0, \left(171 - 5.2 \ln(V) - 0.23 \cdot CC - 16.2 \ln(LOC) + 50 \sin(\sqrt{2.4 \cdot CM})\right) \cdot \frac{100}{171}\right)$$

Where **CM** = Comment percentage (0-1)

## Interpretation

| MI Range | Rating | Maintainability | Color | Action |
|----------|--------|----------------|-------|---------|
| 85-100 | High | Highly maintainable | 🟢 Green | No action needed |
| 65-85 | Moderate | Moderately maintainable | 🟡 Yellow | Consider refactoring complex areas |
| 0-65 | Low | Difficult to maintain | 🔴 Red | Refactoring strongly recommended |

## Component Analysis

### Volume Impact (Halstead V)
- Measures the "size" of the implementation
- Based on number of operators and operands
- Higher volume = more information to process

### Complexity Impact (CC)
- Counts decision points in code
- Each `if`, `for`, `while`, etc. adds complexity
- More paths = harder to test and understand

### Size Impact (LOC)
- Raw size penalty
- More lines = more to read and understand
- Logarithmic scale reduces impact of very large files

## Example Calculations

### Example 1: Simple Function
```python
def add(a, b):
    """Add two numbers."""
    return a + b
```
- Halstead Volume: ~15
- Cyclomatic Complexity: 1
- Lines of Code: 1
- **MI ≈ 95** (Excellent)

### Example 2: Complex Function
```python
def process_data(data, options):
    result = []
    for item in data:
        if options.get('filter'):
            if item > options['threshold']:
                if options.get('transform'):
                    result.append(transform(item))
                else:
                    result.append(item)
        else:
            result.append(item)
    return result
```
- Halstead Volume: ~150
- Cyclomatic Complexity: 5
- Lines of Code: 11
- **MI ≈ 65** (Moderate)

## swent Implementation

```python
# From complexity.py
mi = mi_visit(content, multi=True)

# Handle edge cases
if mi is None:
    mi = 100.0 if raw_metrics.loc == 0 else 50.0
```

### Key Features:
1. Uses `radon` library for accurate calculation
2. Handles empty files gracefully
3. Integrates with overall entropy score
4. Per-file and project-wide averages

## Impact on Entropy

Maintainability Index affects entropy through coverage metrics:

```python
# From entropy_calculator.py
maintainability_score = avg_maintainability / 100.0
maintainability_entropy = 1.0 - maintainability_score
coverage_entropy = 0.6 * doc_entropy + 0.4 * maintainability_entropy
```

## Best Practices to Improve MI

1. **Reduce Complexity**
   - Break large functions into smaller ones
   - Reduce nesting levels
   - Simplify conditional logic

2. **Minimize Size**
   - Extract reusable code
   - Remove dead code
   - Follow Single Responsibility Principle

3. **Improve Structure**
   - Use clear variable names
   - Apply consistent patterns
   - Reduce coupling between components

## Limitations

1. **Language-Specific**: Formula calibrated for procedural languages
2. **No Semantic Analysis**: Doesn't understand code meaning
3. **Size Bias**: Can penalize necessarily large files
4. **Style Insensitive**: Doesn't account for readability

## References

- Oman, P., & Hagemeister, J. (1992). "Metrics for assessing a software system's maintainability"
- Coleman, D., et al. (1994). "Using metrics to evaluate software system maintainability"
- Microsoft Visual Studio Documentation on Code Metrics