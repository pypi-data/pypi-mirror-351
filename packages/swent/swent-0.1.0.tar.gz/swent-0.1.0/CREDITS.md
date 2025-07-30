# Credits and Acknowledgments

swent builds upon the excellent work of many open source projects and research in software engineering metrics.

## Core Dependencies

### Metrics and Analysis

* **[Radon](https://github.com/rubik/radon)** (MIT License)
  - Michele Lacchia and contributors
  - Provides cyclomatic complexity, Halstead metrics, and maintainability index calculations
  - Core metrics engine for complexity analysis

* **[GitPython](https://github.com/gitpython-developers/GitPython)** (BSD License)
  - Sebastian Thiel and contributors
  - Git repository analysis for code churn metrics

* **[AST (Python Standard Library)](https://docs.python.org/3/library/ast.html)**
  - Python Software Foundation
  - Abstract Syntax Tree analysis for code duplication detection

### User Interface

* **[Rich](https://github.com/Textualize/rich)** (MIT License)
  - Will McGugan and contributors
  - Beautiful terminal output and formatting

* **[Click](https://github.com/pallets/click)** (BSD License)
  - Armin Ronacher and contributors
  - Command-line interface framework

### Configuration

* **[TOML](https://github.com/uiri/toml)** (MIT License)
  - William Pearson and contributors
  - Configuration file parsing

* **[PyYAML](https://github.com/yaml/pyyaml)** (MIT License)
  - Kirill Simonov and contributors
  - YAML configuration support

## Concepts and Research

### Software Metrics

* **Cyclomatic Complexity**
  - McCabe, T.J. (1976). "A Complexity Measure". IEEE Transactions on Software Engineering
  - Measures the number of linearly independent paths through code

* **Halstead Metrics**
  - Halstead, Maurice H. (1977). "Elements of Software Science"
  - Quantifies computational complexity based on operators and operands

* **Maintainability Index**
  - Oman, P., and Hagemeister, J. (1992). "Metrics for assessing a software system's maintainability"
  - Coleman, D., et al. (1994). "Using metrics to evaluate software system maintainability"
  - Composite metric combining complexity, size, and documentation

### Software Entropy

* **Software Entropy Concept**
  - Jacobson, Ivar, and Lindström, Fredrik (1991). "Re-engineering of old systems to an object-oriented architecture"
  - Applied thermodynamic entropy concepts to software degradation

* **Technical Debt**
  - Cunningham, Ward (1992). "The WyCash Portfolio Management System"
  - Metaphor for accumulated maintenance burden

### Code Duplication Detection

* **AST-Based Clone Detection**
  - Baxter, I.D., et al. (1998). "Clone detection using abstract syntax trees"
  - Technique for identifying structurally similar code

## Design Inspiration

* **Single Responsibility Tools**
  - Inspired by Unix philosophy: do one thing well
  - Similar to focused tools like black, flake8, pytest

* **Developer Experience**
  - Clear, actionable output inspired by modern linting tools
  - CI/CD integration patterns from successful OSS projects

## Implementation Techniques

### AST Fingerprinting
Our implementation of AST-based duplication detection was inspired by:
- Academic research on code clone detection
- Practical implementations in tools like PMD and Simian

### Entropy Calculation
The weighted entropy formula design was influenced by:
- Multi-criteria decision analysis (MCDA) techniques
- Software quality models like ISO/IEC 25010

### Configuration System
The hierarchical configuration approach was inspired by:
- ESLint's configuration cascade
- Git's configuration levels (system, global, local)

## AI Collaboration

This project was developed in collaboration with Claude (Anthropic), an AI assistant that:
- Helped design the architecture and API
- Implemented core functionality
- Wrote documentation and tests
- Provided software engineering best practices

## License Compliance

All dependencies have been carefully selected for license compatibility:
- MIT License: Radon, Rich, TOML
- BSD License: Click, GitPython, PyYAML
- Python Software Foundation License: Standard library components

## Future Acknowledgments

We welcome contributions! Future contributors will be acknowledged here and in the AUTHORS file.
