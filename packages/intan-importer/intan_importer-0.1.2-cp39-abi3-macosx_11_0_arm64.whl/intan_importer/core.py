"""Core data structures for intan_importer."""
from __future__ import annotations
from typing import Optional, List
import numpy as np
from numpy.typing import NDArray

from . import _lib

class Recording:
    """
    Intan RHS recording with computed properties and methods.
    
    This class wraps the Rust data structures and provides a more
    Pythonic interface with additional computed properties.
    """
    
    def __init__(self, rust_file: _lib.RhsFile):
        """Initialize from Rust RhsFile object."""
        self._rust_file = rust_file
        self._time_cached = None
        
    # ---- Core Properties (from Rust) ----
    
    @property
    def header(self) -> _lib.RhsHeader:
        """Recording header with metadata."""
        return self._rust_file.header
    
    @property
    def data(self) -> Optional[_lib.RhsData]:
        """Raw data arrays if present."""
        return self._rust_file.data
    
    @property
    def data_present(self) -> bool:
        """Whether data is present (vs header only)."""
        return self._rust_file.data_present
    
    @property
    def source_files(self) -> Optional[List[str]]:
        """List of source files if loaded from directory."""
        return self._rust_file.source_files
    
    # ---- Computed Properties ----
    
    @property
    def time(self) -> Optional[NDArray[np.float64]]:
        """
        Time vector in seconds.
        
        Computed from timestamps and sample rate. Cached after first access.
        
        Returns:
            Time in seconds for each sample, or None if no data.
        """
        if not self.data:
            return None
            
        if self._time_cached is None:
            # Convert timestamps to seconds and cache
            self._time_cached = (
                self.data.timestamps.astype(np.float64) / self.header.sample_rate
            )
        
        return self._time_cached
    
    @property
    def duration(self) -> float:
        """Recording duration in seconds."""
        return self._rust_file.duration()
    
    @property
    def num_samples(self) -> int:
        """Total number of samples."""
        return self._rust_file.num_samples()
    
    @property
    def sample_rate(self) -> float:
        """Sampling rate in Hz (convenience property)."""
        return self.header.sample_rate
    
    @property
    def num_channels(self) -> int:
        """Number of amplifier channels (convenience property)."""
        return self.header.num_amplifier_channels
    
    # ---- Data Access Methods ----
    
    def get_channel_data(
        self, 
        channel: int | str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Optional[NDArray[np.int32]]:
        """
        Get data for a specific channel.
        
        Args:
            channel: Channel index (int) or custom name (str)
            start_time: Start time in seconds (None = start of recording)
            end_time: End time in seconds (None = end of recording)
            
        Returns:
            Channel data or None if no data present.
            
        Raises:
            ValueError: If channel not found or time range invalid.
        """
        if not self.data or self.data.amplifier_data is None:
            return None
            
        # Handle channel name lookup
        if isinstance(channel, str):
            channel_idx = self._find_channel_by_name(channel)
        else:
            channel_idx = channel
            
        # Validate channel index
        if not 0 <= channel_idx < self.num_channels:
            raise ValueError(f"Channel index {channel_idx} out of range")
            
        # Get time slice
        if start_time is not None or end_time is not None:
            start_sample = 0 if start_time is None else int(start_time * self.sample_rate)
            end_sample = self.num_samples if end_time is None else int(end_time * self.sample_rate)
            return self.data.amplifier_data[channel_idx, start_sample:end_sample]
        else:
            return self.data.amplifier_data[channel_idx, :]
    
    def _find_channel_by_name(self, name: str) -> int:
        """Find channel index by custom name."""
        for i, ch in enumerate(self.header.amplifier_channels):
            if ch.custom_channel_name == name:
                return i
        raise ValueError(f"Channel '{name}' not found")
    
    def get_time_slice(
        self,
        start_time: float,
        end_time: float,
        data_type: str = "amplifier"
    ) -> Optional[NDArray]:
        """
        Extract data for a time window.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds  
            data_type: Type of data ("amplifier", "adc", "digital_in", etc.)
            
        Returns:
            Data array for time window or None.
        """
        if not self.data:
            return None
            
        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate)
        
        # Get appropriate data array
        data_arrays = {
            "amplifier": self.data.amplifier_data,
            "dc_amplifier": self.data.dc_amplifier_data,
            "stim": self.data.stim_data,
            "adc": self.data.board_adc_data,
            "dac": self.data.board_dac_data,
            "digital_in": self.data.board_dig_in_data,
            "digital_out": self.data.board_dig_out_data,
        }
        
        data_array = data_arrays.get(data_type)
        if data_array is None:
            return None
            
        return data_array[:, start_sample:end_sample]
    
    # ---- String Representations ----
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Recording(duration={self.duration:.1f}s, "
            f"channels={self.num_channels}, "
            f"fs={self.sample_rate}Hz)"
        )
    
    def summary(self) -> str:
        """Detailed summary of recording."""
        lines = [
            f"Intan RHS Recording",
            f"{'='*50}",
            f"Duration: {self.duration:.2f} seconds",
            f"Sample rate: {self.sample_rate} Hz",
            f"Total samples: {self.num_samples:,}",
            f"",
            f"Channels:",
            f"  Amplifier: {self.header.num_amplifier_channels}",
            f"  Board ADC: {self.header.num_board_adc_channels}",
            f"  Board DAC: {self.header.num_board_dac_channels}",
            f"  Digital In: {self.header.num_board_dig_in_channels}",
            f"  Digital Out: {self.header.num_board_dig_out_channels}",
        ]
        
        if self.header.notch_filter_frequency:
            lines.append(f"  Notch filter: {self.header.notch_filter_frequency} Hz")
            
        if self.source_files:
            lines.extend([
                f"",
                f"Source files ({len(self.source_files)}):",
            ])
            for i, f in enumerate(self.source_files, 1):
                lines.append(f"  {i}. {f}")
                
        return "\n".join(lines)