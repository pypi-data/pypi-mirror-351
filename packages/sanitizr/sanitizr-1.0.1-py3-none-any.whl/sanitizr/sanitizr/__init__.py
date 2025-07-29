"""
Sanitizr URL cleaner - Clean URLs by removing tracking parameters and decoding redirects.

This package provides tools to:
- Remove tracking parameters from URLs
- Decode redirect URLs
- Support custom parameter whitelisting/blacklisting
- Handle custom domain-specific rules
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("sanitizr")
except importlib.metadata.PackageNotFoundError:
    __version__ = "1.0.1"

# Import core components for easier access
from .core.cleaner import URLCleaner
from .config.config import ConfigManager

__all__ = ["URLCleaner", "ConfigManager", "__version__"]
