"""
TFQ0tool - A powerful text extraction utility for multiple file formats.

This package provides tools for extracting text from various file formats including
PDFs, Word documents, Excel files, and more, with support for parallel processing
and advanced text processing features.
"""

from .tfq0tool import main
__version__ = "2.0.0"
__author__ = "Talal"
__description__ = "is a command-line utility for extracting text from various file formats, including text files, PDFs, Word documents, spreadsheets, and code files in popular programming languages."
__all__ = ["TextExtractor", "FileProcessor", "utils"]