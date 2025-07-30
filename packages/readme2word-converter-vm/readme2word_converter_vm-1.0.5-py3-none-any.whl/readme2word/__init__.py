"""
README to Word Converter

A powerful Python package that converts README.md files to professional Word documents
with full support for Mermaid diagrams, tables, and advanced formatting.

Author: Vishal Mishra
License: MIT
"""

from typing import Dict, Tuple

__version__ = "1.0.5"
__author__ = "Vishal Mishra"
__email__ = "vishal@example.com"
__license__ = "MIT"
__description__ = "Convert README.md files to professional Word documents with Mermaid diagram support"

from .cli import main as cli_main

# Main imports
from .converter import ReadmeToWordConverter
from .web import main as web_main

# Package metadata
__all__ = [
    "ReadmeToWordConverter",
    "cli_main",
    "web_main",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]

# Version info tuple
VERSION_INFO = tuple(map(int, __version__.split(".")))


def get_version() -> str:
    """Get the package version."""
    return __version__


def get_version_info() -> Tuple[int, ...]:
    """Return the version info tuple."""
    return VERSION_INFO


def get_package_info() -> Dict[str, str]:
    """Return package information."""
    return {
        "name": "readme2word-converter-vm",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": __description__,
    }
