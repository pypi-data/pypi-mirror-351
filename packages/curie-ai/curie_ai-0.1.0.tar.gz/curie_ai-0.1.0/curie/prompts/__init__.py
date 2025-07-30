"""
Prompts package for Curie - Contains various prompt templates used by the system
"""

from .base import BasePrompt
from .experiment import ExperimentPrompt
from .analysis import AnalysisPrompt

__all__ = [
    "BasePrompt",
    "ExperimentPrompt",
    "AnalysisPrompt",
] 