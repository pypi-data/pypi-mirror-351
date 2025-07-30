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
