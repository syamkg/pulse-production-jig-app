from collections.abc import Generator
from serial.serialutil import (
    PortNotOpenError as PortNotOpenError,
    SerialBase as SerialBase,
    SerialException as SerialException,
    Timeout as Timeout,
    iterbytes as iterbytes,
    to_bytes as to_bytes,
)
from typing import Any

LOGGER_LEVELS: Any
SE: bytes
NOP: bytes
DM: bytes
BRK: bytes
IP: bytes
AO: bytes
AYT: bytes
EC: bytes
EL: bytes
GA: bytes
SB: bytes
WILL: bytes
WONT: bytes
DO: bytes
DONT: bytes
IAC: bytes
IAC_DOUBLED: bytes
BINARY: bytes
ECHO: bytes
SGA: bytes
COM_PORT_OPTION: bytes
SET_BAUDRATE: bytes
SET_DATASIZE: bytes
SET_PARITY: bytes
SET_STOPSIZE: bytes
SET_CONTROL: bytes
NOTIFY_LINESTATE: bytes
NOTIFY_MODEMSTATE: bytes
FLOWCONTROL_SUSPEND: bytes
FLOWCONTROL_RESUME: bytes
SET_LINESTATE_MASK: bytes
SET_MODEMSTATE_MASK: bytes
PURGE_DATA: bytes
SERVER_SET_BAUDRATE: bytes
SERVER_SET_DATASIZE: bytes
SERVER_SET_PARITY: bytes
SERVER_SET_STOPSIZE: bytes
SERVER_SET_CONTROL: bytes
SERVER_NOTIFY_LINESTATE: bytes
SERVER_NOTIFY_MODEMSTATE: bytes
SERVER_FLOWCONTROL_SUSPEND: bytes
SERVER_FLOWCONTROL_RESUME: bytes
SERVER_SET_LINESTATE_MASK: bytes
SERVER_SET_MODEMSTATE_MASK: bytes
SERVER_PURGE_DATA: bytes
RFC2217_ANSWER_MAP: Any
SET_CONTROL_REQ_FLOW_SETTING: bytes
SET_CONTROL_USE_NO_FLOW_CONTROL: bytes
SET_CONTROL_USE_SW_FLOW_CONTROL: bytes
SET_CONTROL_USE_HW_FLOW_CONTROL: bytes
SET_CONTROL_REQ_BREAK_STATE: bytes
SET_CONTROL_BREAK_ON: bytes
SET_CONTROL_BREAK_OFF: bytes
SET_CONTROL_REQ_DTR: bytes
SET_CONTROL_DTR_ON: bytes
SET_CONTROL_DTR_OFF: bytes
SET_CONTROL_REQ_RTS: bytes
SET_CONTROL_RTS_ON: bytes
SET_CONTROL_RTS_OFF: bytes
SET_CONTROL_REQ_FLOW_SETTING_IN: bytes
SET_CONTROL_USE_NO_FLOW_CONTROL_IN: bytes
SET_CONTROL_USE_SW_FLOW_CONTOL_IN: bytes
SET_CONTROL_USE_HW_FLOW_CONTOL_IN: bytes
SET_CONTROL_USE_DCD_FLOW_CONTROL: bytes
SET_CONTROL_USE_DTR_FLOW_CONTROL: bytes
SET_CONTROL_USE_DSR_FLOW_CONTROL: bytes
LINESTATE_MASK_TIMEOUT: int
LINESTATE_MASK_SHIFTREG_EMPTY: int
LINESTATE_MASK_TRANSREG_EMPTY: int
LINESTATE_MASK_BREAK_DETECT: int
LINESTATE_MASK_FRAMING_ERROR: int
LINESTATE_MASK_PARTIY_ERROR: int
LINESTATE_MASK_OVERRUN_ERROR: int
LINESTATE_MASK_DATA_READY: int
MODEMSTATE_MASK_CD: int
MODEMSTATE_MASK_RI: int
MODEMSTATE_MASK_DSR: int
MODEMSTATE_MASK_CTS: int
MODEMSTATE_MASK_CD_CHANGE: int
MODEMSTATE_MASK_RI_CHANGE: int
MODEMSTATE_MASK_DSR_CHANGE: int
MODEMSTATE_MASK_CTS_CHANGE: int
PURGE_RECEIVE_BUFFER: bytes
PURGE_TRANSMIT_BUFFER: bytes
PURGE_BOTH_BUFFERS: bytes
RFC2217_PARITY_MAP: Any
RFC2217_REVERSE_PARITY_MAP: Any
RFC2217_STOPBIT_MAP: Any
RFC2217_REVERSE_STOPBIT_MAP: Any
M_NORMAL: int
M_IAC_SEEN: int
M_NEGOTIATE: int
REQUESTED: str
ACTIVE: str
INACTIVE: str
REALLY_INACTIVE: str

class TelnetOption:
    connection: Any
    name: Any
    option: Any
    send_yes: Any
    send_no: Any
    ack_yes: Any
    ack_no: Any
    state: Any
    active: bool
    activation_callback: Any
    def __init__(
        self,
        connection,
        name,
        option,
        send_yes,
        send_no,
        ack_yes,
        ack_no,
        initial_state,
        activation_callback: Any | None = ...,
    ) -> None: ...
    def process_incoming(self, command) -> None: ...

class TelnetSubnegotiation:
    connection: Any
    name: Any
    option: Any
    value: Any
    ack_option: Any
    state: Any
    def __init__(self, connection, name, option, ack_option: Any | None = ...) -> None: ...
    def set(self, value) -> None: ...
    def is_ready(self): ...
    active: Any
    def wait(self, timeout: int = ...) -> None: ...
    def check_answer(self, suboption) -> None: ...

class Serial(SerialBase):
    BAUDRATES: Any
    logger: Any
    def __init__(self, *args, **kwargs) -> None: ...
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
    @property
    def cts(self): ...
    @property
    def dsr(self): ...
    @property
    def ri(self): ...
    @property
    def cd(self): ...
    def telnet_send_option(self, action, option) -> None: ...
    def rfc2217_send_subnegotiation(self, option, value: bytes = ...) -> None: ...
    def rfc2217_send_purge(self, value) -> None: ...
    def rfc2217_set_control(self, value) -> None: ...
    def rfc2217_flow_server_ready(self) -> None: ...
    def get_modem_state(self): ...

class PortManager:
    serial: Any
    connection: Any
    logger: Any
    mode: Any
    suboption: Any
    telnet_command: Any
    modemstate_mask: int
    last_modemstate: Any
    linstate_mask: int
    def __init__(self, serial_port, connection, logger: Any | None = ...) -> None: ...
    def telnet_send_option(self, action, option) -> None: ...
    def rfc2217_send_subnegotiation(self, option, value: bytes = ...) -> None: ...
    def check_modem_lines(self, force_notification: bool = ...) -> None: ...
    def escape(self, data) -> Generator[Any, None, None]: ...
    def filter(self, data) -> Generator[Any, None, None]: ...
