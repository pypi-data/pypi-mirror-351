"""
be-llm101: A Python package for LLM-related utilities and functions.

This package provides utilities and functions for working with Large Language Models (LLMs).
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main functions to make them available at package level
from .core import hello_llm101, get_package_info, LLMUtility

# Define what gets imported with "from be_llm101 import *"
__all__ = [
    "hello_llm101",
    "get_package_info",
    "LLMUtility",
]


def get_data_path(filename: str = "IT_survey.csv") -> str:
    """
    Get the path to a data file included with the package.

    Args:
        filename: Name of the data file (default: "IT_survey.csv")

    Returns:
        Path to the data file

    Example:
        >>> import be_llm101
        >>> path = be_llm101.get_data_path("IT_survey.csv")
        >>> df = pd.read_csv(path)
    """
    import os
    from pathlib import Path

    # Get the directory where this module is located
    package_dir = Path(__file__).parent
    data_dir = package_dir / "data"

    return str(data_dir / filename)


__all__ = ["get_data_path"]
