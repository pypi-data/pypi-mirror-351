"""Initialization

This module exposes Starch's public API.
"""
from . import formatter
from .formatter import CommentFormatter

__all__ = ["CommentFormatter", "formatter"]
