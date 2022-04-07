from ..exc import (
    PinFixedPull as PinFixedPull,
    PinInvalidBounce as PinInvalidBounce,
    PinInvalidFunction as PinInvalidFunction,
    PinInvalidPull as PinInvalidPull,
    PinInvalidState as PinInvalidState,
    PinPWMError as PinPWMError,
    PinSetInput as PinSetInput,
)
from .data import pi_info as pi_info
from .local import LocalPiFactory as LocalPiFactory, LocalPiPin as LocalPiPin
from typing import Any

str: Any

class RPIOFactory(LocalPiFactory):
    pin_class: Any
    def __init__(self) -> None: ...
    def close(self) -> None: ...

class RPIOPin(LocalPiPin):
    GPIO_FUNCTIONS: Any
    GPIO_PULL_UPS: Any
    GPIO_FUNCTION_NAMES: Any
    GPIO_PULL_UP_NAMES: Any
    def __init__(self, factory, number) -> None: ...
    frequency: Any
    when_changed: Any
    def close(self) -> None: ...
