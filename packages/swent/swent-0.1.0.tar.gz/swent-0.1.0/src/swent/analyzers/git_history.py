"""Git history analysis for code churn and change patterns."""

from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import git

from swent.analyzers.base import BaseAnalyzer


class GitHistoryAnalyzer(BaseAnalyzer):
    """Analyzes git history for code churn and change patterns."""
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None, config: Any = None, days_back: Optional[int] = None):
        """
        Initialize git history analyzer.
        
        Args:
            exclude_patterns: Patterns to exclude
            config: SwentConfig instance
            days_back: Number of days to look back in history (overrides config)
        """
        super().__init__(exclude_patterns, config)
        # Use days_back from config if not explicitly provided
        analysis_config = getattr(self.config, 'config', {}).get("analysis", {}) if self.config else {}
        self.days_back = days_back or analysis_config.get("git_history_days", 180)
    
    def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze git history for the project.
        
        Returns dict with:
            - total_commits: Number of commits in the period
            - files_changed: Number of unique files changed
            - code_churn: Lines added + deleted
            - hot_files: Files with most changes
            - commit_frequency: Commits per week
            - author_stats: Contribution statistics
        """
        try:
            repo = git.Repo(project_path)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            # Not a git repository
            return {
                "is_git_repo": False,
                "total_commits": 0,
                "files_changed": 0,
                "code_churn": 0,
                "hot_files": [],
                "commit_frequency": 0,
                "author_stats": {},
            }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days_back)
        
        # Collect commit data
        file_changes: Dict[str, Dict[str, int]] = defaultdict(lambda: {"commits": 0, "additions": 0, "deletions": 0})
        author_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"commits": 0, "additions": 0, "deletions": 0})
        weekly_commits: Dict[Any, int] = defaultdict(int)
        total_commits = 0
        
        try:
            for commit in repo.iter_commits(since=start_date.isoformat()):
                total_commits += 1
                
                # Track weekly commits
                week = commit.committed_datetime.isocalendar()[:2]
                weekly_commits[week] += 1
                
                # Track author stats
                author = str(commit.author)
                author_stats[author]["commits"] += 1
                
                # Analyze file changes
                for diff in commit.diff(commit.parents[0] if commit.parents else None):
                    if diff.a_path and diff.a_path.endswith(".py"):
                        file_path = diff.a_path
                        
                        # Skip if matches exclude patterns
                        if any(Path(file_path).match(pattern) for pattern in self.exclude_patterns):
                            continue
                        
                        file_changes[file_path]["commits"] += 1
                        
                        # Count lines changed
                        if diff.diff:
                            diff_content = diff.diff if isinstance(diff.diff, str) else diff.diff.decode('utf-8', errors='ignore')
                            lines = diff_content.split('\n')
                            additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
                            deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))
                            
                            file_changes[file_path]["additions"] += additions
                            file_changes[file_path]["deletions"] += deletions
                            author_stats[author]["additions"] += additions
                            author_stats[author]["deletions"] += deletions
        
        except Exception as e:
            print(f"Warning: Error analyzing git history: {e}")
        
        # Calculate metrics
        total_churn = sum(f["additions"] + f["deletions"] for f in file_changes.values())
        
        # Find hot files (most frequently changed)
        hot_files = []
        for file_path, stats in file_changes.items():
            hot_files.append({
                "path": file_path,
                "commits": stats["commits"],
                "churn": stats["additions"] + stats["deletions"],
                "additions": stats["additions"],
                "deletions": stats["deletions"],
            })
        
        hot_files.sort(key=lambda x: int(x["commits"]), reverse=True)  # type: ignore[call-overload]
        
        # Calculate average commits per week
        avg_commits_per_week = len(weekly_commits) / max(1, len(weekly_commits)) if weekly_commits else 0
        
        # Find top contributors
        top_authors = sorted(
            [(author, stats) for author, stats in author_stats.items()],
            key=lambda x: int(x[1]["commits"]),
            reverse=True
        )[:5]
        
        # Calculate file stability (files that haven't changed recently)
        python_files = self.find_python_files(project_path)
        stable_files = 0
        for file_path_obj in python_files:
            rel_path_str = str(file_path_obj.relative_to(project_path))
            if rel_path_str not in file_changes:
                stable_files += 1
        
        stability_ratio = stable_files / len(python_files) if python_files else 0
        
        return {
            "is_git_repo": True,
            "total_commits": total_commits,
            "files_changed": len(file_changes),
            "code_churn": total_churn,
            "hot_files": hot_files[:20],  # Top 20 most changed files
            "commit_frequency": avg_commits_per_week,
            "author_stats": dict(top_authors),
            "days_analyzed": self.days_back,
            "stability_ratio": stability_ratio,
            "average_churn_per_file": total_churn / len(file_changes) if file_changes else 0,
        }