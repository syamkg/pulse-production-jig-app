from . import SPI as SPI
from ..exc import (
    DeviceClosed as DeviceClosed,
    PinFixedPull as PinFixedPull,
    PinInvalidBounce as PinInvalidBounce,
    PinInvalidFunction as PinInvalidFunction,
    PinInvalidPull as PinInvalidPull,
    PinInvalidState as PinInvalidState,
    PinPWMFixedValue as PinPWMFixedValue,
    PinSetInput as PinSetInput,
    SPIBadArgs as SPIBadArgs,
    SPIInvalidClockMode as SPIInvalidClockMode,
)
from ..mixins import SharedMixin as SharedMixin
from .local import LocalPiFactory as LocalPiFactory, LocalPiPin as LocalPiPin
from .pi import spi_port_device as spi_port_device
from typing import Any

str: Any

class LGPIOFactory(LocalPiFactory):
    pin_class: Any
    def __init__(self, chip: int = ...) -> None: ...
    def close(self) -> None: ...
    @property
    def chip(self): ...

class LGPIOPin(LocalPiPin):
    GPIO_IS_KERNEL: Any
    GPIO_IS_OUT: Any
    GPIO_IS_ACTIVE_LOW: Any
    GPIO_IS_OPEN_DRAIN: Any
    GPIO_IS_OPEN_SOURCE: Any
    GPIO_IS_BIAS_PULL_UP: Any
    GPIO_IS_BIAS_PULL_DOWN: Any
    GPIO_IS_BIAS_DISABLE: Any
    GPIO_IS_LG_INPUT: Any
    GPIO_IS_LG_OUTPUT: Any
    GPIO_IS_LG_ALERT: Any
    GPIO_IS_LG_GROUP: Any
    GPIO_LINE_FLAGS_MASK: Any
    GPIO_EDGES: Any
    GPIO_EDGES_NAMES: Any
    def __init__(self, factory, number) -> None: ...
    def close(self) -> None: ...

class LGPIOHardwareSPI(SPI):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory) -> None: ...
    def close(self) -> None: ...
    @property
    def closed(self): ...
    def read(self, n): ...
    def write(self, data): ...
    def transfer(self, data): ...

class LGPIOHardwareSPIShared(SharedMixin, LGPIOHardwareSPI): ...
