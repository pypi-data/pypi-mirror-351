"""Type stubs for the Rust extension module."""
from typing import Optional, List
import numpy as np
from numpy.typing import NDArray

class ChannelInfo:
    port_name: str
    native_channel_name: str
    custom_channel_name: str
    native_order: int
    chip_channel: int
    electrode_impedance_magnitude: float
    electrode_impedance_phase: float

class RhsHeader:
    sample_rate: float
    num_samples_per_data_block: int
    dc_amplifier_data_saved: bool
    notch_filter_frequency: Optional[int]
    reference_channel: str
    num_amplifier_channels: int
    num_board_adc_channels: int
    num_board_dac_channels: int
    num_board_dig_in_channels: int
    num_board_dig_out_channels: int
    amplifier_channels: List[ChannelInfo]
    board_adc_channels: List[ChannelInfo]
    note1: str
    note2: str
    note3: str

class RhsData:
    @property
    def timestamps(self) -> NDArray[np.int32]: ...
    @property
    def amplifier_data(self) -> Optional[NDArray[np.int32]]: ...
    @property
    def dc_amplifier_data(self) -> Optional[NDArray[np.int32]]: ...
    @property
    def stim_data(self) -> Optional[NDArray[np.int32]]: ...
    @property
    def board_adc_data(self) -> Optional[NDArray[np.int32]]: ...
    @property
    def board_dac_data(self) -> Optional[NDArray[np.int32]]: ...
    @property
    def board_dig_in_data(self) -> Optional[NDArray[np.int32]]: ...
    @property
    def board_dig_out_data(self) -> Optional[NDArray[np.int32]]: ...
    @property
    def compliance_limit_data(self) -> Optional[NDArray[np.bool_]]: ...
    @property
    def charge_recovery_data(self) -> Optional[NDArray[np.bool_]]: ...
    @property
    def amp_settle_data(self) -> Optional[NDArray[np.bool_]]: ...

class RhsFile:
    header: RhsHeader
    data: Optional[RhsData]
    data_present: bool
    source_files: Optional[List[str]]
    def duration(self) -> float: ...
    def num_samples(self) -> int: ...

def load(path: str) -> RhsFile: ...

__version__: str