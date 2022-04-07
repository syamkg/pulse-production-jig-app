from serial.serialutil import (
    PortNotOpenError as PortNotOpenError,
    SerialBase as SerialBase,
    SerialException as SerialException,
    SerialTimeoutException as SerialTimeoutException,
    Timeout as Timeout,
    to_bytes as to_bytes,
)
from typing import Any

class PlatformSpecificBase:
    BAUDRATE_CONSTANTS: Any
    def set_low_latency_mode(self, low_latency_settings) -> None: ...

CMSPAR: int
plat: Any
TCGETS2: int
TCSETS2: int
BOTHER: int
TIOCGRS485: int
TIOCSRS485: int
SER_RS485_ENABLED: int
SER_RS485_RTS_ON_SEND: int
SER_RS485_RTS_AFTER_SEND: int
SER_RS485_RX_DURING_TX: int

class PlatformSpecific(PlatformSpecificBase):
    BAUDRATE_CONSTANTS: Any
    def set_low_latency_mode(self, low_latency_settings) -> None: ...
    osx_version: Any
    TIOCSBRK: int
    TIOCCBRK: int

IOSSIOSPEED: int

class ReturnBaudrate:
    def __getitem__(self, key): ...

TIOCMGET: Any
TIOCMBIS: Any
TIOCMBIC: Any
TIOCMSET: Any
TIOCM_DTR: Any
TIOCM_RTS: Any
TIOCM_CTS: Any
TIOCM_CAR: Any
TIOCM_RNG: Any
TIOCM_DSR: Any
TIOCM_CD: Any
TIOCM_RI: Any
TIOCINQ: Any
TIOCOUTQ: Any
TIOCM_zero_str: Any
TIOCM_RTS_str: Any
TIOCM_DTR_str: Any
TIOCSBRK: Any
TIOCCBRK: Any

class Serial(SerialBase, PlatformSpecific):
    fd: Any
    pipe_abort_read_w: Any
    pipe_abort_read_r: Any
    pipe_abort_write_w: Any
    pipe_abort_write_r: Any
    is_open: bool
    def open(self) -> None: ...
    def close(self) -> None: ...
    @property
    def in_waiting(self): ...
    def read(self, size: int = ...): ...
    def cancel_read(self) -> None: ...
    def cancel_write(self) -> None: ...
    def write(self, data): ...
    def flush(self) -> None: ...
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
    @property
    def out_waiting(self): ...
    def fileno(self): ...
    def set_input_flow_control(self, enable: bool = ...) -> None: ...
    def set_output_flow_control(self, enable: bool = ...) -> None: ...
    def nonblocking(self) -> None: ...

class PosixPollSerial(Serial):
    def read(self, size: int = ...): ...

class VTIMESerial(Serial):
    def read(self, size: int = ...): ...
    cancel_read: Any
