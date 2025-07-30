# Technical Debt Estimation

## Overview

swent estimates technical debt in hours, providing a concrete measure of the effort required to bring code quality to an acceptable level. This helps teams make informed decisions about refactoring investments.

## Estimation Formula

### Base Formula

$$TD_{hours} = Files \times Base_{hours} \times (1 + E_{total} \times 10) + TD_{specific}$$

Where:
- $TD_{hours}$ = Total technical debt in hours
- $Files$ = Number of files in project
- $Base_{hours}$ = Base maintenance time per file (0.5 hours)
- $E_{total}$ = Total entropy score (0-1)
- $TD_{specific}$ = Specific debt from individual issues

### Component-Specific Debt

$$TD_{specific} = TD_{complexity} + TD_{duplication} + TD_{dependencies}$$

Where:

$$TD_{complexity} = E_{complexity} \times Files \times 2.0$$
$$TD_{duplication} = E_{duplication} \times \frac{Lines}{100} \times 1.5$$
$$TD_{dependencies} = E_{dependencies} \times Dependencies \times 3.0$$

## Debt Categories

### 1. Complexity Debt
Time to simplify overly complex code:
- Refactor large functions
- Reduce nesting levels
- Simplify conditional logic
- **Hours per file**: 2.0 × complexity entropy

### 2. Duplication Debt
Time to eliminate duplicated code:
- Extract common functions
- Create shared utilities
- Consolidate similar classes
- **Hours per 100 lines**: 1.5 × duplication entropy

### 3. Dependency Debt
Time to reduce coupling:
- Break circular dependencies
- Reduce inter-module coupling
- Simplify import structure
- **Hours per dependency**: 3.0 × dependency entropy

### 4. Documentation Debt
Time to document code properly:
- Write missing docstrings
- Update outdated docs
- Add type hints
- **Included in base hours**

### 5. Size Debt
Time to break up large files:
- Split monolithic modules
- Extract related functionality
- Improve organization
- **Included in multiplier**

## Example Calculations

### Small Project (Low Entropy)
- Files: 20
- Entropy: 0.2
- Lines: 2,000
- Dependencies: 5

$$TD_{base} = 20 \times 0.5 \times (1 + 0.2 \times 10) = 20 \times 0.5 \times 3 = 30$$
$$TD_{complexity} = 0.2 \times 20 \times 2.0 = 8$$
$$TD_{duplication} = 0.2 \times 20 \times 1.5 = 6$$
$$TD_{dependencies} = 0.2 \times 5 \times 3.0 = 3$$
$$TD_{total} = 30 + 8 + 6 + 3 = 47 \text{ hours}$$

### Large Project (High Entropy)
- Files: 200
- Entropy: 0.7
- Lines: 50,000
- Dependencies: 30

$$TD_{base} = 200 \times 0.5 \times (1 + 0.7 \times 10) = 200 \times 0.5 \times 8 = 800$$
$$TD_{complexity} = 0.7 \times 200 \times 2.0 = 280$$
$$TD_{duplication} = 0.7 \times 500 \times 1.5 = 525$$
$$TD_{dependencies} = 0.7 \times 30 \times 3.0 = 63$$
$$TD_{total} = 800 + 280 + 525 + 63 = 1,668 \text{ hours}$$

## Interpretation Guidelines

### Debt Levels
| Hours | Impact | Action |
|-------|---------|---------|
| < 40 | Low | Address in regular development |
| 40-200 | Medium | Plan refactoring sprints |
| 200-1000 | High | Dedicated refactoring effort |
| > 1000 | Critical | Major refactoring project |

### Cost Calculation
```
Cost = TD_hours × Developer_hourly_rate
ROI = (Productivity_gain × Time_saved) - Cost
```

## Assumptions and Limitations

### Assumptions
1. **Linear Relationship**: Debt increases linearly with entropy
2. **Average Developer**: Based on mid-level developer speed
3. **Isolated Changes**: Doesn't account for ripple effects
4. **Equal Weight**: All debt types treated similarly

### Limitations
1. **Rough Approximation**: ±50% accuracy expected
2. **Context-Free**: Doesn't consider business value
3. **Skill Variance**: Developer experience affects actual time
4. **Domain Complexity**: Some domains inherently complex

## Using Debt Estimates

### 1. Prioritization
Sort by debt/value ratio:
```python
priority = technical_debt_hours / business_value
```

### 2. Sprint Planning
Allocate percentage of sprint to debt:
```
Sprint_capacity × 20% = Debt_reduction_hours
```

### 3. Tracking Progress
Monitor debt over time:
```
Debt_velocity = (Debt_t1 - Debt_t2) / (t2 - t1)
```

### 4. Business Case
Calculate payback period:
```
Payback_months = Refactoring_cost / Monthly_productivity_gain
```

## Best Practices

1. **Regular Measurement**: Track debt trends monthly
2. **Incremental Reduction**: Small, continuous improvements
3. **High-Impact First**: Focus on files with most debt
4. **Prevent Growth**: Add entropy checks to CI/CD
5. **Team Buy-in**: Share metrics with stakeholders

## Integration with Development

### Pre-commit Checks
```yaml
- repo: swent
  hooks:
    - id: entropy-check
      args: ['--max-debt-increase', '10']
```

### Code Review
- Flag PRs that increase debt significantly
- Require justification for debt increase
- Celebrate debt reduction

### Refactoring Sprints
- Use debt estimates for planning
- Track debt reduction as KPI
- Celebrate improvements