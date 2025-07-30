"""
Setup package for Curie - Contains setup and initialization utilities
"""

from .environment import setup_environment
from .docker import setup_docker
from .logging import setup_logging

__all__ = [
    "setup_environment",
    "setup_docker",
    "setup_logging",
] 