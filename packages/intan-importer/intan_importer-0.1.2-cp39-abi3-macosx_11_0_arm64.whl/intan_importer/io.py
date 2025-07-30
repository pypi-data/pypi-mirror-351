"""I/O functions for loading Intan files."""
from pathlib import Path
from typing import Union

from . import _lib
from .core import Recording

def load(path: Union[str, Path]) -> Recording:
    """
    Load an Intan RHS file or directory containing RHS files.
    
    Args:
        path: Path to a single .rhs file or directory containing .rhs files.
              Can be string or Path object.
    
    Returns:
        Recording object with loaded data.
        
    Raises:
        IOError: If the file cannot be read or is not a valid RHS file.
        
    Examples:
        >>> # Load single file
        >>> rec = load("data.rhs")
        >>> 
        >>> # Load directory
        >>> rec = load("session_data/")
        >>> 
        >>> # Access time vector
        >>> time = rec.time  # Computed from timestamps
        >>> data = rec.data.amplifier_data
    """
    # Convert Path to string if needed
    if isinstance(path, Path):
        path = str(path)
        
    # Load with Rust function
    rust_file = _lib.load(path)
    
    # Wrap in Python class
    return Recording(rust_file)