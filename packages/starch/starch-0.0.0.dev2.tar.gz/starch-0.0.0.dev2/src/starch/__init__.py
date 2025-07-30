"""Initialization

This module exposes Starch's public API.
"""
from . import config, constants, formatter
from .constants import (
    __author__, __version__, __package__,
    CACHE_DIR, CONFIG_DIR, DATA_DIR, LOG_DIR, LOGFILE
)

from .formatter import CommentFormatter
from .config import Configuration

__all__ = [
    "__author__", "__version__", "__package__",
    "CACHE_DIR", "CONFIG_DIR", "DATA_DIR", "LOG_DIR", "LOGFILE",

    "CommentFormatter", "Configuration",

    "config", "constants", "formatter"
]
