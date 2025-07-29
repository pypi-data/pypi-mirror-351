"""
Snavro: A unified file reader for Parquet and Avro files with automatic
detection.

This package provides a simple interface to read and display data from
Parquet and Avro files, automatically detecting the file format based on the
file extension.
"""

from .reader import read_and_display_file, FileReader, get_supported_files

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installations
    __version__ = "dev"

__author__ = "SkinnyPigeon"

__all__ = ["read_and_display_file", "FileReader", "get_supported_files"]
