"""
XER Technologies Metadata Extractor

A Python package for extracting and processing metadata from CSV and binary files.
Supports both local file processing and cloud storage streaming.
"""

from .adapters import LocalFileAdapter, S3Adapter
from .extract import MetadataExtractor
from .validation import FileValidator, ValidationResult

__version__ = "0.1.0"
__author__ = "Jakob Wiren"
__email__ = "jakob.wiren@xer-tech.com"

__all__ = [
    "MetadataExtractor",
    "LocalFileAdapter",
    "S3Adapter",
    "FileValidator",
    "ValidationResult",
]
