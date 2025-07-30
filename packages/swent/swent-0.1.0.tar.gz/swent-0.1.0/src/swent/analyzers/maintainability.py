"""Maintainability Index calculation details and validation."""

import math
from typing import Dict, Any, Optional


class MaintainabilityCalculator:
    """
    Provides detailed maintainability index calculations.
    
    The Maintainability Index (MI) is calculated using the formula:
    MI = max(0, (171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
    
    Where:
    - HV = Halstead Volume
    - CC = Cyclomatic Complexity  
    - LOC = Lines of Code
    
    The index ranges from 0 to 100, where:
    - 85-100: High maintainability (green)
    - 65-85: Moderate maintainability (yellow)
    - 0-65: Low maintainability (red)
    """
    
    @staticmethod
    def calculate_mi(
        halstead_volume: float,
        cyclomatic_complexity: float,
        lines_of_code: int,
        comment_percentage: Optional[float] = None
    ) -> float:
        """
        Calculate maintainability index from raw metrics.
        
        Args:
            halstead_volume: Halstead volume metric
            cyclomatic_complexity: McCabe cyclomatic complexity
            lines_of_code: Source lines of code (excluding blanks/comments)
            comment_percentage: Optional percentage of comment lines (0-1)
            
        Returns:
            Maintainability index (0-100)
        """
        if lines_of_code == 0:
            return 100.0  # Empty file is perfectly maintainable
        
        # Prevent log(0) errors
        hv = max(1, halstead_volume)
        loc = max(1, lines_of_code)
        
        # Base MI calculation
        mi = 171 - 5.2 * math.log(hv) - 0.23 * cyclomatic_complexity - 16.2 * math.log(loc)
        
        # Add comment bonus if provided (Microsoft's enhanced formula)
        if comment_percentage is not None and comment_percentage > 0:
            # sin(sqrt(2.4 * comment_percentage))
            comment_bonus = 50 * math.sin(math.sqrt(2.4 * comment_percentage))
            mi += comment_bonus
        
        # Normalize to 0-100 scale
        mi = max(0, mi * 100 / 171)
        
        return min(100, mi)  # Cap at 100
    
    @staticmethod
    def interpret_mi(mi: float) -> Dict[str, Any]:
        """
        Interpret maintainability index value.
        
        Args:
            mi: Maintainability index (0-100)
            
        Returns:
            Dictionary with interpretation details
        """
        if mi >= 85:
            category = "high"
            description = "Code is highly maintainable"
            color = "green"
            recommendation = "No immediate action needed"
        elif mi >= 65:
            category = "moderate"
            description = "Code has moderate maintainability"
            color = "yellow"
            recommendation = "Consider refactoring complex areas"
        else:
            category = "low"
            description = "Code has low maintainability"
            color = "red"
            recommendation = "Refactoring strongly recommended"
        
        return {
            "value": mi,
            "category": category,
            "description": description,
            "color": color,
            "recommendation": recommendation,
        }
    
    @staticmethod
    def calculate_mi_components(metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Break down MI calculation to show component contributions.
        
        Args:
            metrics: Dictionary with halstead_volume, cyclomatic_complexity, lines_of_code
            
        Returns:
            Dictionary showing how each component affects MI
        """
        hv = max(1, metrics.get("halstead_volume", 1))
        cc = metrics.get("cyclomatic_complexity", 0)
        loc = max(1, metrics.get("lines_of_code", 1))
        
        # Calculate individual penalties
        volume_penalty = 5.2 * math.log(hv)
        complexity_penalty = 0.23 * cc
        size_penalty = 16.2 * math.log(loc)
        
        # Calculate percentages of total penalty
        total_penalty = volume_penalty + complexity_penalty + size_penalty
        
        return {
            "volume_impact": volume_penalty / total_penalty if total_penalty > 0 else 0,
            "complexity_impact": complexity_penalty / total_penalty if total_penalty > 0 else 0,
            "size_impact": size_penalty / total_penalty if total_penalty > 0 else 0,
            "volume_penalty": volume_penalty,
            "complexity_penalty": complexity_penalty,
            "size_penalty": size_penalty,
            "total_penalty": total_penalty,
        }