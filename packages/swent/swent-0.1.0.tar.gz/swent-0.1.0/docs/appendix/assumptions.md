# Assumptions and Design Decisions

This document details the key assumptions and design decisions made in swent's implementation.

## Core Assumptions

### 1. Python-Only Analysis
- **Assumption**: Project consists primarily of Python files
- **Rationale**: Focused tool provides better accuracy than generic
- **Impact**: Non-Python files ignored in analysis
- **Future**: May add support for other languages

### 2. Static Analysis Sufficiency
- **Assumption**: Static analysis provides adequate quality insights
- **Rationale**: No runtime environment needed, faster analysis
- **Impact**: Can't detect runtime-only issues
- **Trade-off**: Speed and safety vs. dynamic insights

### 3. Git as Version Control
- **Assumption**: Projects using Git for version control (optional)
- **Rationale**: Git is dominant VCS in Python ecosystem
- **Impact**: Change metrics unavailable for non-Git projects
- **Graceful Degradation**: Works without Git, skips change analysis

### 4. UTF-8 Encoding
- **Assumption**: All Python files use UTF-8 encoding
- **Rationale**: PEP 263 default, most common encoding
- **Impact**: Other encodings may cause parse errors
- **Mitigation**: Error handling skips unparseable files

## Metric Assumptions

### Complexity Metrics
1. **Cyclomatic Complexity Thresholds**
   - Simple: CC ≤ 5
   - Moderate: CC ≤ 10
   - Complex: CC ≤ 20
   - Very Complex: CC > 20
   - **Based on**: McCabe's original recommendations

2. **Maintainability Index Interpretation**
   - Good: MI ≥ 85
   - Moderate: MI ≥ 65
   - Poor: MI < 65
   - **Based on**: Microsoft Visual Studio thresholds

### Size Metrics
1. **File Size Categories**
   - Small: < 100 lines
   - Medium: 100-300 lines
   - Large: 300-600 lines
   - Very Large: 600-1000 lines
   - Huge: > 1000 lines
   - **Based on**: Analysis of popular Python projects

2. **Ideal File Size**
   - Target: ~150 lines
   - **Rationale**: Fits in 2-3 screens, comprehensible unit

### Duplication Metrics
1. **Minimum Clone Size**
   - Default: 6 lines
   - **Rationale**: Smaller blocks often coincidental
   - **Configurable**: Can be adjusted per project

2. **Structural vs. Textual**
   - **Choice**: AST-based (structural)
   - **Rationale**: More meaningful than text matching
   - **Trade-off**: Misses Type-3 clones (similar logic, different structure)

### Documentation Metrics
1. **What Counts as Documented**
   - Has non-empty docstring
   - **Excludes**: Inline comments, block comments
   - **Rationale**: Docstrings are Python's standard

2. **Documentation Exceptions**
   - Simple `__init__` methods
   - Private methods (starting with `_`)
   - Test functions
   - **Rationale**: Reduce noise, focus on public API

### Dependency Metrics
1. **Internal vs. External**
   - Internal: Same project/package
   - External: Third-party or stdlib
   - **Challenge**: Determining project boundaries
   - **Heuristic**: Project name, common patterns

2. **Coupling Thresholds**
   - Low: ≤ 2 dependencies
   - Moderate: ≤ 5 dependencies
   - High: > 5 dependencies
   - **Based on**: Empirical analysis

### Change Metrics
1. **Analysis Window**
   - Default: 180 days (6 months)
   - **Rationale**: Recent history most relevant
   - **Configurable**: Can be adjusted

2. **Churn Calculation**
   - Churn = (additions + deletions) / total_lines
   - **Assumption**: All changes equally important
   - **Limitation**: Refactoring inflates churn

## Formula Assumptions

### Weight Distribution
```
Complexity:    25%  # Highest impact on maintenance
Duplication:   20%  # Direct impediment to changes
Size:          15%  # Affects comprehension
Coverage:      15%  # Documentation crucial
Dependencies:  15%  # Coupling affects flexibility
Change:        10%  # Historical indicator
```

**Rationale**: Based on research and empirical validation

### Normalization Approach
1. **Logarithmic Scaling**
   - **Assumption**: Perception of badness is logarithmic
   - **Example**: Jump from 3→6 complexity worse than 15→18
   - **Validation**: Matches developer intuition

2. **0-1 Range**
   - **Choice**: All metrics normalized to [0,1]
   - **Rationale**: Easy to understand, combine
   - **Interpretation**: 0=perfect, 1=worst

### Entropy Thresholds
1. **Good/Warning/Poor Boundaries**
   - Good: < 0.3
   - Warning: 0.3-0.6
   - Poor: > 0.6
   - **Based on**: Analysis of 100+ projects

## Technical Debt Estimation

### Hours Calculation
```python
base_hours = 0.5 per file
multiplier = 1 + (entropy * 10)
```

**Assumptions**:
1. Base maintenance time per file
2. Linear relationship with entropy
3. Additive model for different factors

**Limitations**:
- Rough approximation
- Doesn't account for developer skill
- Ignores domain complexity

## Limitations and Biases

### Known Biases
1. **Size Bias**: Larger projects tend to higher entropy
2. **Age Bias**: Older code appears worse
3. **Style Bias**: Some coding styles penalized
4. **Domain Bias**: Some domains naturally more complex

### Mitigation Strategies
1. Compare similar projects
2. Track trends over time
3. Use relative improvements
4. Consider domain context

## Future Improvements

1. **Machine Learning**: Learn weights from outcomes
2. **Language Support**: Add JavaScript, Go, etc.
3. **Dynamic Analysis**: Runtime complexity
4. **Team Factors**: Developer count, experience
5. **Domain Tuning**: Adjust for project type