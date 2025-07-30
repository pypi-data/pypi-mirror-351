# Interpreting Results

## Understanding Your Entropy Score

### Overall Score Scale

| Score Range | Rating | What It Means | Recommended Action |
|-------------|--------|---------------|-------------------|
| 0.0 - 0.3 | ✅ **Excellent** | Clean, well-maintained code | Keep up the good work! |
| 0.3 - 0.6 | ⚠️ **Warning** | Some areas need attention | Plan targeted refactoring |
| 0.6 - 1.0 | ❌ **Poor** | Significant issues present | Major refactoring needed |

### What the Score Represents

The entropy score is a weighted combination of six key metrics:

```
Total Entropy = 25% Complexity + 20% Duplication + 15% Size + 
                15% Coverage + 15% Dependencies + 10% Changes
```

## Component Analysis

### Complexity (25%)
**What it measures**: How difficult code is to understand
- Cyclomatic complexity
- Halstead metrics
- Maintainability index

**Red flags**:
- Functions with CC > 10
- Files with MI < 65
- Deep nesting (> 4 levels)

**How to improve**:
- Break large functions into smaller ones
- Reduce conditional nesting
- Simplify boolean logic

### Duplication (20%)
**What it measures**: Copy-pasted or similar code
- Structural duplicates via AST
- Percentage of duplicated lines

**Red flags**:
- Duplication > 10%
- Same logic in 3+ places
- Large duplicated blocks

**How to improve**:
- Extract common functions
- Create shared utilities
- Use inheritance for similar classes

### Size (15%)
**What it measures**: File and project structure
- Lines per file
- Directory nesting
- File organization

**Red flags**:
- Files > 500 lines
- Directories > 5 levels deep
- 20+ files in one directory

**How to improve**:
- Split large files by responsibility
- Flatten deep hierarchies
- Group related files

### Coverage (15%)
**What it measures**: Documentation and code quality
- Docstring coverage
- Maintainability indicators

**Red flags**:
- < 50% documentation coverage
- Missing docstrings on public APIs
- Low maintainability scores

**How to improve**:
- Add docstrings to all public functions/classes
- Document complex logic
- Improve code clarity

### Dependencies (15%)
**What it measures**: Module coupling and imports
- Import complexity
- Circular dependencies
- External dependencies

**Red flags**:
- Circular import chains
- High coupling (> 10 imports)
- Many external dependencies

**How to improve**:
- Break circular dependencies
- Reduce coupling between modules
- Minimize external dependencies

### Changes (10%)
**What it measures**: Code stability over time
- Frequency of changes
- Hot spots (files that change often)
- Code churn rate

**Red flags**:
- Files changing every week
- High churn rate (> 50%)
- Concentrated changes

**How to improve**:
- Stabilize frequently changing code
- Add tests to reduce bugs
- Refactor unstable areas

## Reading Detailed Output

### Verbose Mode Analysis
```bash
swent --verbose .
```

Shows breakdown by component:
```
Entropy Components:
  Complexity: 0.31    ⚠ Warning
  Size: 0.18          ✓ Good
  Duplication: 0.42   ⚠ Warning
```

### Problem Identification

1. **Check worst component first**
   - Focus on highest entropy components
   - Look for "Poor" ratings

2. **Review specific files**
   - Check "hot files" in git analysis
   - Look at "high complexity files"
   - Find "large files" list

3. **Examine patterns**
   - Repeated problems across files?
   - Concentrated in one area?
   - Recent or historical?

## Action Planning

### Priority Matrix

| Entropy Component | Score > 0.6 | Score 0.3-0.6 | Score < 0.3 |
|------------------|-------------|----------------|-------------|
| **Complexity** | 🔴 Urgent refactor | 🟡 Plan refactor | 🟢 Monitor |
| **Duplication** | 🔴 Extract common code | 🟡 Review duplicates | 🟢 Good |
| **Size** | 🔴 Split files | 🟡 Consider splitting | 🟢 Good |
| **Coverage** | 🔴 Document now | 🟡 Improve docs | 🟢 Maintain |
| **Dependencies** | 🔴 Decouple modules | 🟡 Review structure | 🟢 Good |
| **Changes** | 🟡 Stabilize code | 🟢 Natural churn | 🟢 Stable |

### Refactoring Strategy

#### Quick Wins (< 1 hour each)
- Add missing docstrings
- Extract obvious duplicates
- Split files > 1000 lines
- Fix circular imports

#### Medium Effort (1-4 hours)
- Refactor complex functions
- Consolidate similar code
- Improve module structure
- Add comprehensive docs

#### Major Refactoring (> 4 hours)
- Architectural changes
- Complete module rewrites
- Dependency restructuring
- Legacy code modernization

## Tracking Progress

### Establish Baseline
```bash
swent --json . > baseline.json
```

### Regular Monitoring
```bash
# Weekly check
swent . --threshold 0.6

# Compare to baseline
swent . --compare baseline.json
```

### Success Metrics
- Entropy trend (should decrease)
- Component improvements
- Technical debt reduction
- Fewer high-complexity files

## Common Patterns and Solutions

### Pattern: "Big Ball of Mud"
**Symptoms**: High complexity, high coupling, poor structure
**Solution**: Gradual modularization, establish boundaries

### Pattern: "Copy-Paste Programming"
**Symptoms**: High duplication, similar files
**Solution**: Extract libraries, use DRY principle

### Pattern: "God Object"
**Symptoms**: Huge files, high complexity
**Solution**: Split responsibilities, single purpose principle

### Pattern: "Spaghetti Code"
**Symptoms**: High coupling, circular dependencies
**Solution**: Dependency injection, clear interfaces

## Getting Help

If entropy remains high after refactoring:
1. Focus on highest-impact components
2. Consider architectural review
3. Get team input on problem areas
4. Plan incremental improvements
5. Set realistic targets

Remember: Perfect score (0.0) isn't the goal - aim for sustainable, maintainable code!