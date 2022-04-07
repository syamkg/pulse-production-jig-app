from serial.tools import list_ports_common as list_ports_common
from typing import Any

class SysFS(list_ports_common.ListPortInfo):
    usb_device_path: Any
    device_path: Any
    subsystem: Any
    usb_interface_path: Any
    vid: Any
    pid: Any
    serial_number: Any
    location: Any
    manufacturer: Any
    product: Any
    interface: Any
    description: Any
    hwid: Any
    def __init__(self, device) -> None: ...
    def read_line(self, *args): ...

def comports(include_links: bool = ...): ...
