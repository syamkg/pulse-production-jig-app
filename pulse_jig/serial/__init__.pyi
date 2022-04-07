from serial.serialutil import *
from serial.serialjava import Serial as Serial
from serial.serialposix import PosixPollSerial as PosixPollSerial, VTIMESerial as VTIMESerial
from typing import Any

VERSION: Any
protocol_handler_packages: Any

def serial_for_url(url, *args, **kwargs): ...
