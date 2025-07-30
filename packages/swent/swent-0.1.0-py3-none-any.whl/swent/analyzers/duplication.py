"""Code duplication detection using AST analysis."""

import ast
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from swent.analyzers.base import BaseAnalyzer


class DuplicationAnalyzer(BaseAnalyzer):
    """Detects code duplication using AST fingerprinting."""
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None, config: Any = None, min_lines: Optional[int] = None):
        """
        Initialize duplication analyzer.
        
        Args:
            exclude_patterns: Patterns to exclude
            config: SwentConfig instance
            min_lines: Minimum lines for a code block to be considered for duplication
        """
        super().__init__(exclude_patterns, config)
        # Use min_lines from config if not explicitly provided
        config_dict = getattr(self.config, 'config', {}) if self.config else {}
        self.min_lines = min_lines or config_dict.get("min_duplicate_lines", 6)
    
    def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze code duplication in the project.
        
        Returns dict with:
            - duplication_ratio: Percentage of duplicated lines
            - duplicated_blocks: List of duplicated code blocks with details
            - files_with_duplication: Number of files containing duplicates
            - duplication_hotspots: Files with most duplication
            - duplication_summary: High-level summary statistics
        """
        python_files = self.find_python_files(project_path)
        
        # Map of fingerprint to list of (file, node, lines) tuples
        fingerprint_map = defaultdict(list)
        total_lines = 0
        duplicated_lines = 0
        file_line_counts = {}
        
        # First pass: collect all code blocks
        for file_path in python_files:
            blocks = self._extract_code_blocks(file_path, project_path)
            for fingerprint, node_info in blocks:
                fingerprint_map[fingerprint].append(node_info)
            
            # Count total lines per file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    file_line_counts[str(file_path.relative_to(project_path))] = lines
            except:
                continue
        
        # Second pass: identify duplicates
        duplicated_blocks = []
        processed_files = set()
        file_duplication_counts: Dict[Path, int] = defaultdict(int)
        
        for fingerprint, locations in fingerprint_map.items():
            if len(locations) > 1:
                # This code block appears multiple times
                block_info = {
                    "fingerprint": fingerprint,
                    "occurrences": len(locations),
                    "locations": [],
                    "lines": locations[0]["lines"],  # Number of lines in the block
                    "type": locations[0]["type"],
                    "name": locations[0]["name"],
                    "impact_score": locations[0]["lines"] * len(locations),  # Lines × occurrences
                }
                
                # Extract code snippet from first occurrence
                first_loc = locations[0]
                snippet = self._extract_code_snippet(
                    Path(project_path) / first_loc["file"],
                    first_loc["start_line"],
                    first_loc["end_line"]
                )
                if snippet:
                    block_info["code_snippet"] = snippet
                
                for loc in locations:
                    block_info["locations"].append({
                        "file": loc["file"],
                        "start_line": loc["start_line"],
                        "end_line": loc["end_line"],
                        "function_name": loc["name"],
                    })
                    processed_files.add(loc["file"])
                    file_duplication_counts[loc["file"]] += loc["lines"]
                    duplicated_lines += loc["lines"]
                
                duplicated_blocks.append(block_info)
        
        # Sort by impact (lines × occurrences)
        duplicated_blocks.sort(key=lambda x: x["impact_score"], reverse=True)
        
        # Calculate duplication hotspots
        duplication_hotspots = []
        for file_path, dup_lines in file_duplication_counts.items():
            total_file_lines = file_line_counts.get(str(file_path), 1)
            duplication_hotspots.append({
                "file": file_path,
                "duplicated_lines": dup_lines,
                "total_lines": total_file_lines,
                "duplication_percentage": (dup_lines / total_file_lines) * 100 if total_file_lines > 0 else 0,
            })
        
        duplication_hotspots.sort(key=lambda x: float(x["duplication_percentage"]), reverse=True)  # type: ignore[arg-type]
        
        duplication_ratio = duplicated_lines / total_lines if total_lines > 0 else 0.0
        
        # Create summary statistics
        duplication_summary = {
            "total_duplicated_blocks": len(duplicated_blocks),
            "total_duplicated_lines": duplicated_lines,
            "unique_patterns": len(fingerprint_map),
            "patterns_duplicated": len([f for f, locs in fingerprint_map.items() if len(locs) > 1]),
            "max_duplications": max([len(locs) for locs in fingerprint_map.values()]) if fingerprint_map else 0,
            "files_affected": len(processed_files),
            "duplication_categories": self._categorize_duplications(duplicated_blocks),
        }
        
        return {
            "duplication_ratio": duplication_ratio,
            "duplicated_blocks": duplicated_blocks,  # All duplications for detailed report
            "files_with_duplication": len(processed_files),
            "total_duplicated_lines": duplicated_lines,
            "total_lines": total_lines,
            "duplication_hotspots": duplication_hotspots[:10],  # Top 10 hotspots
            "duplication_summary": duplication_summary,
        }
    
    def _extract_code_blocks(self, file_path: Path, project_path: Path) -> List[Tuple[str, Dict[str, Any]]]:
        """Extract code blocks from a Python file."""
        blocks = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
            
            tree = ast.parse(content)
            
            # Extract function and class definitions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                        num_lines = (node.end_lineno or node.lineno) - node.lineno + 1
                        
                        if num_lines >= self.min_lines:
                            # Create a fingerprint of the node
                            fingerprint = self._create_fingerprint(node)
                            
                            node_info = {
                                "file": str(file_path.relative_to(project_path)),
                                "start_line": node.lineno,
                                "end_line": node.end_lineno,
                                "lines": num_lines,
                                "type": type(node).__name__,
                                "name": node.name,
                            }
                            
                            blocks.append((fingerprint, node_info))
        
        except Exception as e:
            # Skip files that can't be parsed
            pass
        
        return blocks
    
    def _create_fingerprint(self, node: ast.AST) -> str:
        """Create a fingerprint of an AST node for comparison."""
        # Remove position information and names for structural comparison
        cleaned = self._clean_ast(node)
        
        # Convert to string representation
        ast_str = ast.dump(cleaned, annotate_fields=False)
        
        # Create hash
        return hashlib.md5(ast_str.encode()).hexdigest()
    
    def _clean_ast(self, node: ast.AST) -> ast.AST:
        """Remove position info and normalize names from AST."""
        class Cleaner(ast.NodeTransformer):
            def visit(self, node: ast.AST) -> Any:
                # Remove position attributes
                for attr in ["lineno", "col_offset", "end_lineno", "end_col_offset"]:
                    if hasattr(node, attr):
                        delattr(node, attr)
                
                # Normalize variable names but keep structure
                if isinstance(node, ast.Name):
                    node.id = "VAR"
                elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    node.name = "ENTITY"
                elif isinstance(node, ast.arg):
                    node.arg = "ARG"
                
                return self.generic_visit(node)
        
        import copy
        cleaned = copy.deepcopy(node)
        return Cleaner().visit(cleaned)  # type: ignore[no-any-return]
    
    def _extract_code_snippet(self, file_path: Path, start_line: int, end_line: int, max_lines: int = 10) -> Optional[str]:
        """Extract a code snippet from a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Adjust for 0-based indexing
            start_idx = start_line - 1
            end_idx = end_line
            
            # Limit snippet size
            if end_idx - start_idx > max_lines:
                end_idx = start_idx + max_lines
                truncated = True
            else:
                truncated = False
            
            snippet_lines = lines[start_idx:end_idx]
            snippet = "".join(snippet_lines)
            
            if truncated:
                snippet += "... (truncated)\n"
            
            return snippet.rstrip()
            
        except Exception:
            return None
    
    def _categorize_duplications(self, duplicated_blocks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize duplications by type and size."""
        categories = {
            "small": 0,      # 6-20 lines
            "medium": 0,     # 21-50 lines
            "large": 0,      # 51-100 lines
            "very_large": 0, # 100+ lines
            "functions": 0,
            "classes": 0,
            "high_impact": 0,  # 3+ occurrences
        }
        
        for block in duplicated_blocks:
            lines = block["lines"]
            
            # Size categories
            if lines <= 20:
                categories["small"] += 1
            elif lines <= 50:
                categories["medium"] += 1
            elif lines <= 100:
                categories["large"] += 1
            else:
                categories["very_large"] += 1
            
            # Type categories
            if block["type"] == "FunctionDef":
                categories["functions"] += 1
            elif block["type"] == "ClassDef":
                categories["classes"] += 1
            
            # Impact categories
            if block["occurrences"] >= 3:
                categories["high_impact"] += 1
        
        return categories