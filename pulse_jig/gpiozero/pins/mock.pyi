from ..compat import isclose as isclose
from ..devices import Device as Device
from ..exc import (
    PinFixedPull as PinFixedPull,
    PinInvalidBounce as PinInvalidBounce,
    PinInvalidFunction as PinInvalidFunction,
    PinInvalidPull as PinInvalidPull,
    PinPWMUnsupported as PinPWMUnsupported,
    PinSetInput as PinSetInput,
)
from .local import LocalPiFactory as LocalPiFactory, LocalPiPin as LocalPiPin
from typing import Any, NamedTuple

str: Any

class PinState(NamedTuple):
    timestamp: Any
    state: Any

class MockPin(LocalPiPin):
    def __init__(self, factory, number) -> None: ...
    when_changed: Any
    function: str
    def close(self) -> None: ...
    def drive_high(self) -> None: ...
    def drive_low(self) -> None: ...
    states: Any
    def clear_states(self) -> None: ...
    def assert_states(self, expected_states) -> None: ...
    def assert_states_and_times(self, expected_states) -> None: ...

class MockConnectedPin(MockPin):
    input_pin: Any
    def __init__(self, factory, number, input_pin: Any | None = ...) -> None: ...

class MockChargingPin(MockPin):
    charge_time: Any
    def __init__(self, factory, number, charge_time: float = ...) -> None: ...

class MockTriggerPin(MockPin):
    echo_pin: Any
    echo_time: Any
    def __init__(self, factory, number, echo_pin: Any | None = ..., echo_time: float = ...) -> None: ...

class MockPWMPin(MockPin):
    def __init__(self, factory, number) -> None: ...
    frequency: Any
    def close(self) -> None: ...

class MockSPIClockPin(MockPin):
    spi_devices: Any
    def __init__(self, factory, number) -> None: ...

class MockSPISelectPin(MockPin):
    spi_device: Any
    def __init__(self, factory, number) -> None: ...

class MockSPIDevice:
    clock_pin: Any
    mosi_pin: Any
    miso_pin: Any
    select_pin: Any
    clock_polarity: Any
    clock_phase: Any
    lsb_first: Any
    bits_per_word: Any
    select_high: Any
    rx_bit: int
    rx_buf: Any
    tx_buf: Any
    def __init__(
        self,
        clock_pin,
        mosi_pin: Any | None = ...,
        miso_pin: Any | None = ...,
        select_pin: Any | None = ...,
        clock_polarity: bool = ...,
        clock_phase: bool = ...,
        lsb_first: bool = ...,
        bits_per_word: int = ...,
        select_high: bool = ...,
    ) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_value, exc_tb) -> None: ...
    def close(self) -> None: ...
    def on_select(self) -> None: ...
    def on_clock(self) -> None: ...
    def on_start(self) -> None: ...
    def on_bit(self) -> None: ...
    def rx_word(self): ...
    def tx_word(self, value, bits_per_word: Any | None = ...) -> None: ...

class MockFactory(LocalPiFactory):
    pin_class: Any
    def __init__(self, revision: Any | None = ..., pin_class: Any | None = ...) -> None: ...
    def reset(self) -> None: ...
    def pin(self, spec, pin_class: Any | None = ..., **kwargs): ...
