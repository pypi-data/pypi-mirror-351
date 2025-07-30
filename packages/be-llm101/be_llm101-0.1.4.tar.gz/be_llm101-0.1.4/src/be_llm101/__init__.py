"""
be-llm101: A Python package for LLM-related utilities and functions.

This package provides utilities and functions for working with Large Language Models (LLMs).
"""

try:
    from importlib.metadata import version, metadata
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import version, metadata

__version__ = version("be-llm101")

# Get author info from package metadata
_metadata = metadata("be-llm101")
_authors = _metadata.get("Author", "").split(",") if _metadata.get("Author") else []
__author__ = _authors[0].strip() if _authors else "Unknown"
__email__ = _metadata.get("Author-email", "unknown@example.com")

# Import main functions to make them available at package level
from .info import get_package_info
from .utils import get_data_path, load_data
