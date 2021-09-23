import time
import re
import serial
from typing import Optional


def check_for_serial(port: serial.Serial, timeout: float = 0) -> Optional[str]:
    """Monitors the port for a device serial number from the production
    firmware. If found it is return. The check consumes all available data
    from the port.

    :param port: the serial port to monitor
    :param timeout: The maximum number of seconds to monitor for. Zero to
    return immediately after checking available data.
    :return: returns the serial number if found, else None
    """
    resp = ""
    end_time = time.monotonic() + timeout
    while timeout == 0 or end_time > time.monotonic():
        while port.in_waiting > 0:
            resp += port.read(port.in_waiting).decode("utf-8")
        matches = re.search(r"^Serial: (.*)$", resp, re.MULTILINE)
        if matches:
            return matches.group(1).strip()
        if timeout == 0:
            break
    return None
