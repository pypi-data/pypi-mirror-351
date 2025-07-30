"""
dstack Management Tool - A TUI for managing dstack YAML configurations
"""

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A Terminal User Interface for managing dstack YAML configurations"

from .manager import DStackYAMLManager
from .config import ConfigManager

__all__ = ["DStackYAMLManager", "ConfigManager"]