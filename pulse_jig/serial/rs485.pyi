import serial
from typing import Any

class RS485Settings:
    rts_level_for_tx: Any
    rts_level_for_rx: Any
    loopback: Any
    delay_before_tx: Any
    delay_before_rx: Any
    def __init__(
        self,
        rts_level_for_tx: bool = ...,
        rts_level_for_rx: bool = ...,
        loopback: bool = ...,
        delay_before_tx: Any | None = ...,
        delay_before_rx: Any | None = ...,
    ) -> None: ...

class RS485(serial.Serial):
    def __init__(self, *args, **kwargs) -> None: ...
    def write(self, b) -> None: ...
    @property
    def rs485_mode(self): ...
    @rs485_mode.setter
    def rs485_mode(self, rs485_settings) -> None: ...
