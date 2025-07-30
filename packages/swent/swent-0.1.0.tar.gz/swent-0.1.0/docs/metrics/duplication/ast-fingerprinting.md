# AST Fingerprinting for Code Duplication

## Overview

swent uses Abstract Syntax Tree (AST) fingerprinting to detect code duplication. This technique identifies structurally similar code even when variable names or formatting differ.

## How AST Fingerprinting Works

### 1. Parse Code to AST
```python
import ast
tree = ast.parse(source_code)
```

### 2. Extract Code Blocks
We analyze:
- Function definitions
- Class definitions
- Method definitions
- Blocks with ≥6 lines (configurable)

### 3. Normalize AST
Remove non-structural elements:
- Variable names → `VAR`
- Function names → `ENTITY`
- Position information
- Comments

### 4. Generate Fingerprint
```python
ast_string = ast.dump(normalized_tree)
fingerprint = hashlib.md5(ast_string.encode()).hexdigest()
```

### 5. Compare Fingerprints
Identical fingerprints = structural duplicates

## Example Detection

### Original Code Blocks
```python
# Block A
def calculate_total(items):
    total = 0
    for item in items:
        if item.is_valid():
            total += item.value
    return total

# Block B (duplicate despite different names)
def sum_valid_entries(entries):
    sum_val = 0
    for entry in entries:
        if entry.is_valid():
            sum_val += entry.value
    return sum_val
```

### After Normalization
Both blocks become:
```
FunctionDef(
  name='ENTITY',
  args=arguments(args=[arg(arg='ARG')]),
  body=[
    Assign(targets=[Name(id='VAR')], value=Constant(value=0)),
    For(
      target=Name(id='VAR'),
      iter=Name(id='VAR'),
      body=[
        If(
          test=Call(
            func=Attribute(value=Name(id='VAR'), attr='is_valid')
          ),
          body=[
            AugAssign(
              target=Name(id='VAR'),
              op=Add(),
              value=Attribute(value=Name(id='VAR'), attr='value')
            )
          ]
        )
      ]
    ),
    Return(value=Name(id='VAR'))
  ]
)
```

**Result**: Same fingerprint → Duplication detected!

## Algorithm Details

### AST Cleaning Process
```python
class Cleaner(ast.NodeTransformer):
    def visit(self, node):
        # Remove position attributes
        for attr in ["lineno", "col_offset", 
                    "end_lineno", "end_col_offset"]:
            if hasattr(node, attr):
                delattr(node, attr)
        
        # Normalize identifiers
        if isinstance(node, ast.Name):
            node.id = "VAR"
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            node.name = "ENTITY"
        elif isinstance(node, ast.arg):
            node.arg = "ARG"
        
        return self.generic_visit(node)
```

### Fingerprint Generation
```python
def create_fingerprint(node: ast.AST) -> str:
    cleaned = clean_ast(node)
    ast_str = ast.dump(cleaned, annotate_fields=False)
    return hashlib.md5(ast_str.encode()).hexdigest()
```

## Advantages

1. **Structure-Aware**: Detects semantic duplicates, not just textual
2. **Rename-Resistant**: Variable/function names don't affect detection
3. **Format-Independent**: Whitespace and comments ignored
4. **Fast**: O(n) parsing, O(1) comparison

## Limitations

1. **Language-Specific**: Only works for Python
2. **No Partial Matches**: All-or-nothing detection
3. **Type-3 Clones**: Can't detect similar logic with different structure
4. **Small Blocks**: May over-report on common patterns

## Configuration

### Minimum Block Size
```python
min_lines = 6  # Don't report duplicates smaller than this
```

### Excluded Patterns
Common patterns can be excluded:
- Simple getters/setters
- Initialization methods
- Test setup/teardown

## Metrics Produced

- **Duplication Ratio**: % of lines that are duplicated
- **Duplicate Blocks**: List of cloned code sections
- **Clone Locations**: Where each duplicate appears
- **Impact Score**: Lines × occurrences for prioritization

## Example Output

```json
{
  "duplication_ratio": 0.124,
  "duplicated_blocks": [
    {
      "fingerprint": "a3f2b1c4...",
      "occurrences": 3,
      "lines": 15,
      "locations": [
        {"file": "utils.py", "start": 45, "end": 60},
        {"file": "helpers.py", "start": 12, "end": 27},
        {"file": "common.py", "start": 88, "end": 103}
      ]
    }
  ]
}
```

## Best Practices

1. **Extract Common Code**: Move duplicates to shared functions
2. **Use Inheritance**: For duplicated class methods
3. **Apply DRY Principle**: Don't Repeat Yourself
4. **Regular Scans**: Check for duplication in PRs

## Integration with Entropy

Duplication directly increases entropy:
- Harder to maintain (changes needed in multiple places)
- Increased bug risk (fixes may miss some copies)
- Confusion about which version is "correct"

Weight in total entropy: **20%**