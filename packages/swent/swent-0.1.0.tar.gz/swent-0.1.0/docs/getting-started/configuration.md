# Configuration

swent supports flexible configuration through multiple methods, allowing you to customize analysis behavior for your specific needs.

## Configuration Methods

### 1. Configuration Files

swent looks for configuration in the following locations (in priority order):

1. **Current Working Directory** (highest priority)
   - `.swentrc`
   - `.swentrc.json`
   - `.swentrc.yaml` / `.swentrc.yml`
   - `.swentrc.toml`
   - `swent.toml`

2. **Project Directory** (being analyzed)
   - `.swentrc`
   - `.swentrc.json`
   - `.swentrc.yaml` / `.swentrc.yml`
   - `.swentrc.toml`
   - `swent.toml`

3. **Home Directory** (lowest priority)
   - `~/.swentrc`
   - `~/.config/swent/config.toml`

4. **pyproject.toml** (checked in both CWD and project directory)
   - In `[tool.swent]` section

The first found configuration file is used. This allows you to:
- Have a global config in your home directory
- Override with a project-specific config
- Override both with a config in your current directory

### 2. Command Line Options

CLI options override configuration file settings:

```bash
swent --exclude "vendor/*" --threshold 0.5 .
```

## Generating a Configuration File

To create a default configuration file in your project:

```bash
swent --init
```

This creates `.swentrc.toml` with all available options and documentation.

## Configuration Options

### Exclude Patterns

Control which files and directories are excluded from analysis:

```toml
# Extend default excludes (recommended)
extend_default_excludes = true
exclude_patterns = [
    "vendor/",
    "third_party/",
    "legacy/",
]

# Or replace defaults entirely
extend_default_excludes = false
exclude_patterns = [
    "*.pyc",
    "__pycache__/",
    # ... your complete list
]
```

#### Default Exclusions

swent excludes common Python build/cache directories by default:

- **Build artifacts**: `build/`, `dist/`, `*.egg-info/`, `wheels/`
- **Virtual environments**: `venv/`, `.venv/`, `env/`, `.env/`
- **Cache directories**: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- **Test coverage**: `.coverage`, `htmlcov/`, `*.cover`
- **IDE files**: `.idea/`, `.vscode/`, `*.swp`
- **Version control**: `.git/`, `.svn/`, `.hg/`
- **Package managers**: `node_modules/`, `.tox/`, `.nox/`

[Full list in source code](https://git.ligo.org/greg/swent/-/blob/main/src/swent/config.py)

### Entropy Thresholds

Define what constitutes good/warning/poor entropy levels:

```toml
[entropy_thresholds]
good = 0.3     # Below this is excellent
warning = 0.6  # Below this needs attention
# Above warning is poor
```

### Component Weights

Adjust the importance of different metrics (must sum to 1.0):

```toml
[weights]
complexity = 0.25
duplication = 0.20
size = 0.15
coverage = 0.15
dependencies = 0.15
change = 0.10
```

### Analysis Parameters

Fine-tune analysis behavior:

```toml
[analysis]
git_history_days = 180        # How far back to analyze
max_file_size = 10000         # Lines before warning
complexity_threshold = 10     # Cyclomatic complexity threshold
min_duplicate_lines = 6       # Minimum lines for duplication
```

## Usage Scenarios

### Working with Multiple Projects

Create a `.swentrc.toml` in your workspace directory:

```bash
cd ~/workspace
swent --init  # Creates .swentrc.toml

# Now analyze any project from this directory
swent ./project-a
swent ./project-b
swent ../other-project

# All will use ~/workspace/.swentrc.toml configuration
```

### Team Configuration

Share configuration across your team:

```bash
# In project root
swent --init
git add .swentrc.toml
git commit -m "Add team swent configuration"

# Team members automatically use this config
git pull
swent .
```

## Example Configurations

### Strict Quality Standards

```toml
# .swentrc.toml - Strict configuration
[entropy_thresholds]
good = 0.2
warning = 0.4

[weights]
complexity = 0.30    # Emphasize code complexity
duplication = 0.25   # Heavily penalize duplication
size = 0.10
coverage = 0.20      # Enforce documentation
dependencies = 0.10
change = 0.05

[analysis]
complexity_threshold = 7  # Lower threshold
min_duplicate_lines = 4   # Catch smaller duplicates
```

### Legacy Project

```toml
# .swentrc.toml - Lenient for legacy code
extend_default_excludes = true
exclude_patterns = [
    "legacy/",
    "deprecated/",
    "*_old.py",
]

[entropy_thresholds]
good = 0.4
warning = 0.7

[weights]
complexity = 0.20
duplication = 0.15   # More tolerant of duplication
size = 0.20          # Legacy often has large files
coverage = 0.10      # Don't penalize missing docs heavily
dependencies = 0.20
change = 0.15
```

### Data Science Project

```toml
# .swentrc.toml - For Jupyter-heavy projects
extend_default_excludes = true
exclude_patterns = [
    "notebooks/",
    "experiments/",
    "*.ipynb",
    "data/",
    "models/",
]

[analysis]
max_file_size = 500  # Notebooks can be large
```

## pyproject.toml Integration

If you're already using `pyproject.toml`, add swent configuration under `[tool.swent]`:

```toml
[tool.swent]
extend_default_excludes = true
exclude_patterns = ["tests/fixtures/"]

[tool.swent.entropy_thresholds]
good = 0.3
warning = 0.6

[tool.swent.weights]
complexity = 0.25
duplication = 0.20
size = 0.15
coverage = 0.15
dependencies = 0.15
change = 0.10
```

## Configuration Validation

swent validates configuration on load:
- Weights must sum to 1.0
- Thresholds must be between 0.0 and 1.0
- Invalid patterns are warned about

## Best Practices

1. **Start with defaults**: Generate config with `--init` and adjust as needed
2. **Version control**: Commit your `.swentrc.toml` for team consistency
3. **Extend, don't replace**: Use `extend_default_excludes = true` unless you have specific needs
4. **Document changes**: Comment why you're excluding specific patterns
5. **Regular review**: Adjust thresholds as your project matures

## Troubleshooting

### Files still being analyzed

Check pattern syntax:
- `"build/"` - Excludes directory
- `"*.pyc"` - Excludes files by extension
- `"test_*.py"` - Excludes by pattern

Use `--verbose` to see which files are being analyzed:
```bash
swent --verbose . | grep "Analyzing"
```

### Configuration not loaded

Check file location and syntax:
```bash
# Validate TOML syntax
python -m toml .swentrc.toml

# Check if file is found
swent --verbose . 2>&1 | grep "config"
```