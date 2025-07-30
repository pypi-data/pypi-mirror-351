"""
MHTML to HTML Converter

A Python wrapper around the Go-based mhtml-to-html tool with automatic
character encoding detection and conversion (supports Chinese GBK/GB18030,
Japanese Shift_JIS, Korean EUC-KR, and more).
"""

__version__ = "1.1.0"

from .converter import convert_mhtml, convert_mhtml_file

__all__ = ["convert_mhtml", "convert_mhtml_file"] 