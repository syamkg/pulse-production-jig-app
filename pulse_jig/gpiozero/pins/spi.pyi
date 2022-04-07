from ..devices import Device as Device, SharedMixin as SharedMixin
from ..input_devices import InputDevice as InputDevice
from ..output_devices import OutputDevice as OutputDevice
from typing import Any

str: Any

class SPISoftwareBus(SharedMixin, Device):
    lock: Any
    clock: Any
    mosi: Any
    miso: Any
    def __init__(self, clock_pin, mosi_pin, miso_pin) -> None: ...
    def close(self) -> None: ...
    @property
    def closed(self): ...
    def transfer(self, data, clock_phase: bool = ..., lsb_first: bool = ..., bits_per_word: int = ...): ...
