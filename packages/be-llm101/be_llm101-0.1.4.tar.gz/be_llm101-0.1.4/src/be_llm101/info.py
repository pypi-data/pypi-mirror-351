"""
Package information utilities for be-llm101.
"""

import sys
from typing import Dict, Any


def get_package_info() -> Dict[str, Any]:
    """
    Get information about the be-llm101 package.

    Returns:
        Dict[str, Any]: A dictionary containing package information.

    Example:
        >>> from be_llm101 import get_package_info
        >>> info = get_package_info()
        >>> print(info['version'])
        0.1.3
    """
    from . import __version__, __author__, __email__

    return {
        "name": "be-llm101",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "python_version": sys.version,
        "description": "A Python package for the BearingPoint LLM101 course",
    }
