"""
Constant Contact Google Sheets Unsubscriber

A Python package for automatically unsubscribing emails from Constant Contact
using Google Sheets as the data source.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import ConstantContactUnsubscriber
from .sheets import GoogleSheetsReader
from .config import Config
from .utils import process_sheet, validate_setup, get_status_summary

__all__ = [
    "ConstantContactUnsubscriber",
    "GoogleSheetsReader", 
    "Config",
    "process_sheet",
    "validate_setup", 
    "get_status_summary",
] 