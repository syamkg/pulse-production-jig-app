from ..exc import (
    PinFixedPull as PinFixedPull,
    PinInvalidEdges as PinInvalidEdges,
    PinInvalidFunction as PinInvalidFunction,
    PinInvalidPull as PinInvalidPull,
    PinSetInput as PinSetInput,
)
from .local import LocalPiFactory as LocalPiFactory, LocalPiPin as LocalPiPin
from collections import Counter as Counter
from collections.abc import Generator
from threading import Thread
from typing import Any

range = xrange
nstr = str
str: Any

def dt_resolve_alias(alias, root: str = ...): ...
def dt_peripheral_reg(node, root: str = ...) -> Generator[None, None, Any]: ...

class GPIOMemory:
    GPIO_BASE_OFFSET: int
    PERI_BASE_OFFSET: Any
    GPFSEL_OFFSET: Any
    GPSET_OFFSET: Any
    GPCLR_OFFSET: Any
    GPLEV_OFFSET: Any
    GPEDS_OFFSET: Any
    GPREN_OFFSET: Any
    GPFEN_OFFSET: Any
    GPHEN_OFFSET: Any
    GPLEN_OFFSET: Any
    GPAREN_OFFSET: Any
    GPAFEN_OFFSET: Any
    GPPUD_OFFSET: Any
    GPPUDCLK_OFFSET: Any
    GPPUPPDN_OFFSET: Any
    fd: Any
    mem: Any
    reg_fmt: Any
    def __init__(self, soc) -> None: ...
    def close(self) -> None: ...
    def gpio_base(self, soc): ...
    def __getitem__(self, index): ...
    def __setitem__(self, index, value) -> None: ...

class GPIOFS:
    GPIO_PATH: str
    def __init__(self, factory, queue) -> None: ...
    def close(self) -> None: ...
    def path(self, name): ...
    def path_value(self, pin): ...
    def path_dir(self, pin): ...
    def path_edge(self, pin): ...
    def exported(self, pin): ...
    def export(self, pin): ...
    def unexport(self, pin) -> None: ...
    def watch(self, pin) -> None: ...
    def unwatch(self, pin) -> None: ...

class NativeWatchThread(Thread):
    daemon: bool
    def __init__(self, factory, queue) -> None: ...
    def close(self) -> None: ...
    def watch(self, fd, pin) -> None: ...
    def unwatch(self, fd) -> None: ...

class NativeDispatchThread(Thread):
    daemon: bool
    def __init__(self, factory, queue) -> None: ...
    def close(self) -> None: ...

class NativeFactory(LocalPiFactory):
    mem: Any
    fs: Any
    dispatch: Any
    pin_class: Any
    def __init__(self) -> None: ...
    def close(self) -> None: ...

class NativePin(LocalPiPin):
    GPIO_FUNCTIONS: Any
    GPIO_FUNCTION_NAMES: Any
    function: str
    pull: Any
    bounce: Any
    edges: str
    def __init__(self, factory, number) -> None: ...
    frequency: Any
    when_changed: Any
    def close(self) -> None: ...

class Native2835Pin(NativePin):
    GPIO_PULL_UPS: Any
    GPIO_PULL_UP_NAMES: Any

class Native2711Pin(NativePin):
    GPIO_PULL_UPS: Any
    GPIO_PULL_UP_NAMES: Any
