from serial.serialutil import (
    PortNotOpenError as PortNotOpenError,
    SerialBase as SerialBase,
    SerialException as SerialException,
    SerialTimeoutException as SerialTimeoutException,
    Timeout as Timeout,
    to_bytes as to_bytes,
)
from typing import Any

LOGGER_LEVELS: Any
POLL_TIMEOUT: int

class Serial(SerialBase):
    BAUDRATES: Any
    logger: Any
    is_open: bool
    def open(self) -> None: ...
    def close(self) -> None: ...
    def from_url(self, url): ...
    @property
    def in_waiting(self): ...
    def read(self, size: int = ...): ...
    def write(self, data): ...
    def reset_input_buffer(self) -> None: ...
    def reset_output_buffer(self) -> None: ...
    def send_break(self, duration: float = ...) -> None: ...
    @property
    def cts(self): ...
    @property
    def dsr(self): ...
    @property
    def ri(self): ...
    @property
    def cd(self): ...
    def fileno(self): ...
