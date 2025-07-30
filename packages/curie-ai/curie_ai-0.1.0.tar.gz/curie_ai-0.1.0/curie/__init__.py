"""
Curie - A scientific research experimentation agent

This package provides tools for automated scientific research experimentation,
including experiment design, execution, analysis, and visualization.

Main usage:
    import curie
    curie.experiment(
        dataset_dir="path/to/dataset",
        workspace_name="experiment_name",
        question_file="path/to/questions.txt"
    )
"""

__version__ = "0.1.0"

from .main import experiment
from .model import Model
from .tool import Tool
from .scheduler import Scheduler
from .reporter import Reporter
from .utils import setup_logging, setup_environment

__all__ = [
    "experiment",
    "Model",
    "Tool",
    "Scheduler",
    "Reporter",
    "setup_logging",
    "setup_environment",
]
