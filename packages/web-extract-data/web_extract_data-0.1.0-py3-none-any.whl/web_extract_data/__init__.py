"""
Web Extract Data - A Python package for extracting structured data from websites.

This package provides native functions for each endpoint of the InstantAPI.ai
Web Scraping API, making it easy to extract data from websites without writing
HTML selectors.
"""

from .client import WebExtractClient

__version__ = "0.1.0"
__all__ = ["WebExtractClient"]
