# python/intan_importer/__init__.py
"""
Fast Python bindings for reading Intan RHS files.

This package provides high-performance reading of Intan Technologies RHS files
using Rust for the core parsing logic.
"""

from __future__ import annotations

__version__ = "0.1.0"

# Import the main load function from our Rust extension
from ._lib import load

__all__ = ["load", "__version__"]