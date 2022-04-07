from ..exc import (
    PinFixedPull as PinFixedPull,
    PinInvalidBounce as PinInvalidBounce,
    PinInvalidFunction as PinInvalidFunction,
    PinInvalidPull as PinInvalidPull,
    PinInvalidState as PinInvalidState,
    PinPWMFixedValue as PinPWMFixedValue,
    PinSetInput as PinSetInput,
)
from .local import LocalPiFactory as LocalPiFactory, LocalPiPin as LocalPiPin
from typing import Any

str: Any

class RPiGPIOFactory(LocalPiFactory):
    pin_class: Any
    def __init__(self) -> None: ...
    def close(self) -> None: ...

class RPiGPIOPin(LocalPiPin):
    GPIO_FUNCTIONS: Any
    GPIO_PULL_UPS: Any
    GPIO_EDGES: Any
    GPIO_FUNCTION_NAMES: Any
    GPIO_PULL_UP_NAMES: Any
    GPIO_EDGES_NAMES: Any
    def __init__(self, factory, number) -> None: ...
    frequency: Any
    when_changed: Any
    def close(self) -> None: ...
    def output_with_state(self, state) -> None: ...
    def input_with_pull(self, pull) -> None: ...
