"""Dependency analysis for Python projects."""

import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from swent.analyzers.base import BaseAnalyzer


class DependencyAnalyzer(BaseAnalyzer):
    """Analyzes project dependencies and coupling."""
    
    # No custom __init__ needed, uses BaseAnalyzer's __init__
    
    def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze dependencies and coupling in the project.
        
        Returns dict with:
            - import_count: Total number of imports
            - external_dependencies: Set of external packages
            - internal_modules: Number of internal modules
            - coupling_metrics: Module coupling analysis
            - circular_dependencies: Detected circular imports
        """
        python_files = self.find_python_files(project_path)
        
        # Build import graph
        import_graph: Dict[str, Set[str]] = defaultdict(set)  # module -> set of imported modules
        external_deps: Set[str] = set()
        all_modules: Set[str] = set()
        file_imports: Dict[str, List[str]] = {}  # file -> list of imports
        
        # First pass: collect all imports
        for file_path in python_files:
            module_name = self._get_module_name(file_path, project_path)
            all_modules.add(module_name)
            
            imports = self._extract_imports(file_path)
            file_imports[str(file_path.relative_to(project_path))] = imports
            
            for imp in imports:
                if self._is_external_import(imp, project_path):
                    external_deps.add(imp.split(".")[0])  # Root package
                else:
                    # Internal import
                    imported_module = self._resolve_internal_import(imp, module_name)
                    if imported_module:
                        import_graph[module_name].add(imported_module)
        
        # Analyze coupling
        coupling_metrics = self._analyze_coupling(import_graph, all_modules)
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(import_graph)
        
        # Find most imported modules (hot spots)
        import_counts: Dict[str, int] = defaultdict(int)
        for imports in import_graph.values():  # type: ignore[assignment]
            for imp in imports:
                import_counts[imp] += 1
        
        hot_spots = sorted(
            [(module, count) for module, count in import_counts.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_imports": sum(len(imports) for imports in file_imports.values()),
            "external_dependencies": sorted(list(external_deps)),
            "external_dependency_count": len(external_deps),
            "internal_modules": len(all_modules),
            "coupling_metrics": coupling_metrics,
            "circular_dependencies": circular_deps,
            "hot_spots": hot_spots,
            "average_imports_per_file": sum(len(imports) for imports in file_imports.values()) / len(python_files) if python_files else 0,
        }
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract all imports from a Python file."""
        imports = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Check if this looks like a vendored file with many conditional imports
            # (like bottle.py which has server adapters)
            is_likely_vendored = self._is_likely_vendored_file(file_path, content)
            
            if is_likely_vendored:
                # For vendored files, only get top-level imports
                imports = self._extract_top_level_imports(tree)
            else:
                # For regular files, get all imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        # Skip relative imports (they're always internal)
                        if node.level > 0:  # Relative import like "from . import" or "from .. import"
                            continue
                        if node.module:
                            imports.append(node.module)
                        # Also track what's being imported
                        for alias in node.names:
                            if node.module:
                                imports.append(f"{node.module}.{alias.name}")
        
        except Exception:
            # Skip files that can't be parsed
            pass
        
        return imports
    
    def _extract_top_level_imports(self, tree: ast.Module) -> List[str]:
        """Extract only top-level imports (not inside functions/classes)."""
        imports = []
        
        # Only look at direct children of the module
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                # Skip relative imports
                if node.level > 0:
                    continue
                if node.module:
                    imports.append(node.module)
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
        
        return imports
    
    def _is_likely_vendored_file(self, file_path: Path, content: str) -> bool:
        """Check if file is likely a vendored library with conditional imports."""
        # Heuristics for vendored files
        vendored_indicators = [
            "bottle.py",  # Known vendored file
            "__version__",  # Single-file modules often have version
            "server_names",  # Bottle specific
        ]
        
        filename = file_path.name
        
        # Check filename
        if filename in ["bottle.py", "six.py", "requests.py"]:
            return True
            
        # Check for signs of many server adapters or conditional imports
        if filename.endswith(".py"):
            # Look for multiple server adapter classes
            server_adapters = ["Server", "Adapter", "Handler", "Application"]
            adapter_count = sum(1 for adapter in server_adapters if adapter in content)
            if adapter_count > 10:  # Many adapter classes
                return True
        
        return False
    
    
    def _get_module_name(self, file_path: Path, project_path: Path) -> str:
        """Convert file path to module name."""
        rel_path = file_path.relative_to(project_path)
        
        # Remove .py extension and convert to module notation
        module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        
        # Remove src/ prefix if present
        if module_parts[0] == "src" and len(module_parts) > 1:
            module_parts = module_parts[1:]
        
        return ".".join(module_parts)
    
    def _is_external_import(self, import_name: str, project_path: Path) -> bool:
        """Check if an import is external to the project."""
        # Comprehensive standard library modules list
        # Based on Python 3.x standard library documentation
        stdlib_modules = {
            # Built-in modules
            "os", "sys", "re", "json", "math", "random", "datetime", "time",
            "collections", "itertools", "functools", "pathlib", "typing",
            "ast", "dis", "inspect", "unittest", "doctest", "argparse",
            "logging", "warnings", "copy", "pickle", "shelve", "sqlite3",
            "hashlib", "hmac", "secrets", "uuid", "urllib", "http", "email",
            "csv", "configparser", "tempfile", "glob", "shutil", "zipfile",
            "subprocess", "threading", "multiprocessing", "concurrent", "asyncio",
            "contextlib", "abc", "dataclasses", "enum", "types", "weakref",
            "struct", "io", "gc", "signal", "platform", "traceback", "pdb",
            "importlib", "pkgutil", "runpy", "builtins", "__future__",
            
            # Additional stdlib modules
            "array", "base64", "binascii", "bisect", "calendar", "cmath",
            "codecs", "colorsys", "copyreg", "cProfile", "ctypes", "curses",
            "decimal", "difflib", "errno", "fcntl", "filecmp", "fileinput",
            "fnmatch", "fractions", "ftplib", "getopt", "getpass", "gettext",
            "grp", "gzip", "heapq", "html", "imaplib", "imghdr", "imp",
            "ipaddress", "keyword", "linecache", "locale", "lzma", "mailbox",
            "mimetypes", "mmap", "modulefinder", "netrc", "numbers", "operator",
            "optparse", "ossaudiodev", "parser", "pdb", "pickle", "pipes",
            "pkgutil", "plistlib", "poplib", "posix", "pprint", "profile",
            "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue",
            "quopri", "readline", "reprlib", "resource", "rlcompleter", "sched",
            "select", "selectors", "shelve", "shlex", "site", "smtplib",
            "sndhdr", "socket", "socketserver", "spwd", "stat", "statistics",
            "string", "stringprep", "struct", "sunau", "symtable", "sysconfig",
            "syslog", "tabnanny", "tarfile", "telnetlib", "termios", "textwrap",
            "this", "token", "tokenize", "trace", "traceback", "tracemalloc",
            "tty", "turtle", "unicodedata", "uu", "venv", "wave", "webbrowser",
            "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp", "zipimport", "zlib",
            
            # Common aliases and submodules
            "urllib2", "urllib3",  # urllib aliases
            "httplib", "urlparse", "HTMLParser",  # Python 2 compat names
            "StringIO", "cStringIO", "BytesIO",  # IO compat
            "ConfigParser",  # Python 2 name for configparser
            "cPickle",  # Python 2 optimized pickle
            "Queue", "queue",  # Python 2/3 names
            "thread", "_thread",  # Threading modules
            "socketserver", "SocketServer",  # Python 2/3 names
            
            # Test frameworks often included
            "pytest", "nose", "mock", "unittest2",
            
            # Common internal/private modules
            "_abc", "_ast", "_bisect", "_blake2", "_codecs", "_collections",
            "_collections_abc", "_compat_pickle", "_compression", "_csv",
            "_ctypes", "_datetime", "_decimal", "_elementtree", "_functools",
            "_hashlib", "_heapq", "_imp", "_io", "_json", "_locale", "_lsprof",
            "_md5", "_multiprocessing", "_operator", "_pickle", "_posixsubprocess",
            "_random", "_sha1", "_sha256", "_sha512", "_socket", "_sqlite3",
            "_sre", "_stat", "_string", "_struct", "_symtable", "_thread",
            "_threading_local", "_tracemalloc", "_warnings", "_weakref",
            "_weakrefset", "_version",
            
            # Additional common modules
            "graphlib",  # Added in Python 3.9
            "zoneinfo",  # Added in Python 3.9
            "tomllib",   # Added in Python 3.11
        }
        
        root_module = import_name.split(".")[0]
        
        # Check if it's stdlib
        if root_module in stdlib_modules:
            return False
        
        # Try to detect the actual package name
        package_names = self._detect_package_names(project_path)
        
        # Check if import matches any detected package name
        for pkg_name in package_names:
            if root_module == pkg_name or import_name.startswith(f"{pkg_name}."):
                return False
        
        # Check common patterns for internal imports
        if root_module in ["src", "tests", "test", "docs", "examples"]:
            return False
        
        # Otherwise, it's likely external
        return True
    
    def _detect_package_names(self, project_path: Path) -> Set[str]:
        """Detect the actual package name(s) for the project."""
        package_names = set()
        
        # Check pyproject.toml
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import toml
                data = toml.loads(pyproject_path.read_text())
                # Get package name from project metadata
                if "project" in data and "name" in data["project"]:
                    package_names.add(data["project"]["name"])
            except:
                pass
        
        # Check setup.py or setup.cfg
        setup_py = project_path / "setup.py"
        if setup_py.exists():
            try:
                content = setup_py.read_text()
                # Simple regex to find name in setup()
                import re
                match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    package_names.add(match.group(1))
            except:
                pass
        
        # Check for src layout
        src_dir = project_path / "src"
        if src_dir.exists() and src_dir.is_dir():
            # Add all directories in src/ that have __init__.py
            for item in src_dir.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    package_names.add(item.name)
        
        # Check root directory for packages
        for item in project_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                # Skip common non-package directories
                if item.name not in ["tests", "test", "docs", "examples", "scripts", "build", "dist"]:
                    package_names.add(item.name)
        
        # Fallback to directory name if nothing found
        if not package_names:
            package_names.add(project_path.name)
        
        return package_names
    
    def _resolve_internal_import(self, import_name: str, from_module: str) -> Optional[str]:
        """Resolve internal import to full module name."""
        # This is simplified - real resolution would need to handle relative imports
        return import_name
    
    def _analyze_coupling(self, import_graph: Dict[str, Set[str]], all_modules: Set[str]) -> Dict[str, Any]:
        """Analyze coupling metrics."""
        # Calculate afferent coupling (modules that depend on this module)
        afferent_coupling: Dict[str, int] = defaultdict(int)
        for module, imports in import_graph.items():
            for imported in imports:
                afferent_coupling[imported] += 1
        
        # Calculate efferent coupling (modules this module depends on)
        efferent_coupling = {
            module: len(imports) for module, imports in import_graph.items()
        }
        
        # Calculate instability: I = Ce / (Ca + Ce)
        instability = {}
        for module in all_modules:
            ca = afferent_coupling.get(module, 0)
            ce = efferent_coupling.get(module, 0)
            if ca + ce > 0:
                instability[module] = ce / (ca + ce)
            else:
                instability[module] = 0.0
        
        # Find highly coupled modules
        highly_coupled = []
        for module in all_modules:
            total_coupling = afferent_coupling.get(module, 0) + efferent_coupling.get(module, 0)
            if total_coupling > 10:  # Arbitrary threshold
                highly_coupled.append({
                    "module": module,
                    "afferent": afferent_coupling.get(module, 0),
                    "efferent": efferent_coupling.get(module, 0),
                    "instability": instability.get(module, 0),
                })
        
        highly_coupled.sort(key=lambda x: int(x["afferent"]) + int(x["efferent"]), reverse=True)  # type: ignore[call-overload]
        
        avg_coupling = sum(efferent_coupling.values()) / len(all_modules) if all_modules else 0
        
        return {
            "average_coupling": avg_coupling,
            "highly_coupled_modules": highly_coupled[:10],
            "max_coupling": max(efferent_coupling.values()) if efferent_coupling else 0,
            "modules_with_no_deps": sum(1 for v in efferent_coupling.values() if v == 0),
        }
    
    def _detect_circular_dependencies(self, import_graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs(module: str, path: List[str]) -> None:
            visited.add(module)
            rec_stack.add(module)
            path.append(module)
            
            for imported in import_graph.get(module, set()):
                if imported not in visited:
                    dfs(imported, path.copy())
                elif imported in rec_stack:
                    # Found circular dependency
                    cycle_start = path.index(imported)
                    cycle = path[cycle_start:] + [imported]
                    if len(cycle) > 2:  # Ignore self-imports
                        circular_deps.append(cycle)
            
            rec_stack.remove(module)
        
        for module in import_graph:
            if module not in visited:
                dfs(module, [])
        
        # Remove duplicates
        unique_cycles = []
        for cycle in circular_deps:
            # Normalize cycle to start with smallest element
            min_idx = cycle.index(min(cycle))
            normalized = cycle[min_idx:] + cycle[:min_idx]
            if normalized not in unique_cycles:
                unique_cycles.append(normalized)
        
        return unique_cycles[:5]  # Return top 5 circular dependencies