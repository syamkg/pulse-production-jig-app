from . import Factory as Factory, Pin as Pin
from ..compat import WeakMethod as WeakMethod
from ..exc import (
    PinInvalidPin as PinInvalidPin,
    PinNoPins as PinNoPins,
    PinNonPhysical as PinNonPhysical,
    SPIBadArgs as SPIBadArgs,
    SPISoftwareFallback as SPISoftwareFallback,
)
from .data import PiBoardInfo as PiBoardInfo
from collections import defaultdict as defaultdict
from threading import Lock as Lock
from typing import Any

str: Any
SPI_HARDWARE_PINS: Any

def spi_port_device(clock_pin, mosi_pin, miso_pin, select_pin): ...

class PiFactory(Factory):
    pins: Any
    pin_class: Any
    def __init__(self) -> None: ...
    def close(self) -> None: ...
    def reserve_pins(self, requester, *pins) -> None: ...
    def release_pins(self, reserver, *pins) -> None: ...
    def pin(self, spec): ...
    def spi(self, **spi_args): ...

class PiPin(Pin):
    def __init__(self, factory, number) -> None: ...
    @property
    def number(self): ...
    @property
    def factory(self): ...
