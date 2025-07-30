"""Documentation coverage analysis."""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

from swent.analyzers.base import BaseAnalyzer


class DocumentationAnalyzer(BaseAnalyzer):
    """Analyzes documentation coverage in Python code."""
    
    # No custom __init__ needed, uses BaseAnalyzer's __init__
    
    def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze documentation coverage for all Python files.
        
        Returns dict with:
            - total_items: Total documentable items (functions, classes, modules)
            - documented_items: Items with docstrings
            - documentation_coverage: Percentage of documented items
            - undocumented_items: List of items missing documentation
        """
        python_files = self.find_python_files(project_path)
        
        total_items = 0
        documented_items = 0
        undocumented_list = []
        file_coverage = {}
        
        for file_path in python_files:
            file_stats = self._analyze_file_documentation(file_path, project_path)
            if file_stats:
                total_items += file_stats["total"]
                documented_items += file_stats["documented"]
                undocumented_list.extend(file_stats["undocumented"])
                
                rel_path = str(file_path.relative_to(project_path))
                file_coverage[rel_path] = file_stats["coverage"]
        
        coverage = documented_items / total_items if total_items > 0 else 0.0
        
        # Sort undocumented items by type for better reporting
        undocumented_by_type: Dict[str, List[Dict[str, Any]]] = {
            "modules": [],
            "classes": [],
            "functions": [],
            "methods": []
        }
        
        for item in undocumented_list:
            undocumented_by_type[item["type"]].append(item)
        
        return {
            "total_items": total_items,
            "documented_items": documented_items,
            "documentation_coverage": coverage,
            "undocumented_by_type": undocumented_by_type,
            "file_coverage": file_coverage,
            "files_with_low_coverage": self._find_low_coverage_files(file_coverage),
        }
    
    def _analyze_file_documentation(self, file_path: Path, project_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze documentation in a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check module docstring
            has_module_docstring = ast.get_docstring(tree) is not None
            
            total_items = 1  # The module itself
            documented_items = 1 if has_module_docstring else 0
            undocumented = []
            
            if not has_module_docstring:
                undocumented.append({
                    "type": "modules",
                    "name": str(file_path.relative_to(project_path)),
                    "line": 1,
                })
            
            # Walk the AST to find all documentable items
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    total_items += 1
                    if ast.get_docstring(node):
                        documented_items += 1
                    else:
                        undocumented.append({
                            "type": "classes",
                            "name": node.name,
                            "line": node.lineno,
                            "file": str(file_path.relative_to(project_path)),
                        })
                    
                    # Check methods in the class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            total_items += 1
                            if ast.get_docstring(item):
                                documented_items += 1
                            else:
                                # Skip __init__ without docstring if it's simple
                                if not (item.name == "__init__" and len(item.body) <= 2):
                                    undocumented.append({
                                        "type": "methods",
                                        "name": f"{node.name}.{item.name}",
                                        "line": item.lineno,
                                        "file": str(file_path.relative_to(project_path)),
                                    })
                
                elif isinstance(node, ast.FunctionDef) and not self._is_nested_function(node, tree):
                    # Only count top-level functions
                    total_items += 1
                    if ast.get_docstring(node):
                        documented_items += 1
                    else:
                        # Skip private functions and test functions
                        if not (node.name.startswith("_") or node.name.startswith("test_")):
                            undocumented.append({
                                "type": "functions",
                                "name": node.name,
                                "line": node.lineno,
                                "file": str(file_path.relative_to(project_path)),
                            })
            
            coverage = documented_items / total_items if total_items > 0 else 0.0
            
            return {
                "total": total_items,
                "documented": documented_items,
                "coverage": coverage,
                "undocumented": undocumented,
            }
            
        except Exception as e:
            print(f"Warning: Could not analyze documentation in {file_path}: {e}")
            return None
    
    def _is_nested_function(self, func_node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if a function is nested inside a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item is func_node:
                        return True
        return False
    
    def _find_low_coverage_files(self, file_coverage: Dict[str, float], threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Find files with low documentation coverage."""
        low_coverage = []
        
        for file_path, coverage in file_coverage.items():
            if coverage < threshold:
                low_coverage.append({
                    "file": file_path,
                    "coverage": coverage,
                })
        
        # Sort by coverage (lowest first)
        low_coverage.sort(key=lambda x: float(x["coverage"]))  # type: ignore[arg-type]
        return low_coverage[:10]  # Top 10 worst documented files