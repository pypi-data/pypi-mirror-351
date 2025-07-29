"""
Sanitizr - Clean URLs by removing tracking parameters and decoding redirects.

This package provides tools for cleaning URLs and removing privacy-invasive tracking parameters.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("sanitizr")
except importlib.metadata.PackageNotFoundError:
    __version__ = "1.0.0"

# Import from subpackage for easier access
from sanitizr.cleanurl import URLCleaner, ConfigManager

__all__ = ["URLCleaner", "ConfigManager"]