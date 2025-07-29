"""
HSV: Hit Score Visualization

A Pydantic-based module for creating, managing, and visualizing hit score judgments
with support for colored text art generation from images.
"""

__version__ = "1.0.0"

from bs_hsv.core import Color, Judgment, HSVConfig
from bs_hsv.generators import TextArtGenerator
from bs_hsv.exceptions import HSVError, ValidationError, FileError

# Create a default instance for easier imports
config = HSVConfig()

__all__ = [
    'Color', 'Judgment', 'HSVConfig', 'TextArtGenerator', 
    'HSVError', 'ValidationError', 'FileError'
]