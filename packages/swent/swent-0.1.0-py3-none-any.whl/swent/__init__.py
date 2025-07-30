"""swent - Software entropy measurement tool."""

__version__ = "0.1.0"
__author__ = "swent contributors"

from swent.core import analyze_project, calculate_entropy
from swent.metrics import EntropyMetrics

__all__ = ["analyze_project", "calculate_entropy", "EntropyMetrics"]