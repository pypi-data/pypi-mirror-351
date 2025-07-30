"""
Fast Python bindings for reading Intan RHS files.

This package provides high-performance reading of Intan Technologies RHS files
using Rust for the core parsing logic.
"""
from __future__ import annotations

__version__ = "0.1.0"

# Import main API
from .io import load
from .core import Recording

# Define public API
__all__ = [
    "load",
    "Recording", 
    "__version__",
]