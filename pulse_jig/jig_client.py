import serial
import time
from typing import Union
import os


if os.name == "nt":  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == "posix":
    from serial.tools.list_ports_posix import comports
else:
    raise ImportError(
        "Sorry: no implementation for your platform ('{}') available".format(os.name)
    )


class JigClientException(Exception):
    """JigClient exception"""


class JigClient:
    def __init__(self, port: Union[str, serial.Serial], logger=None):
        if type(port) is str:
            self.port = serial.Serial(port, 115200)
        else:
            self.port = port
        self.write_timeout = 1
        self.ack_timeout = 0.5
        self.body_timeout = 2
        self.last_error = None
        self.log = ""
        self.terminator = "\r\n"
        self.prompt = "> "
        self.logger = logger

    def _is_end_of_body(self, line: str) -> None:
        return line == "."

    def skip_boot_header(self) -> None:
        self._read_until_prompt(2)

    def _read_until_prompt(self, timeout) -> None:
        self.port.timeout = 0.1
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            if self._readline() == self.prompt:
                break

    def _readline(self) -> str:
        line = self.port.readline().decode("utf-8")
        self.log += line
        line = line.rstrip(self.terminator)
        if self.logger is not None and line != "":
            self.logger.debug("S: " + line)
        return line

    def _writeline(self, line: str) -> None:
        if self.logger is not None:
            self.logger.debug("C: " + line)
        line += "\r"
        self.port.write(f"{line}".encode("utf-8"))
        self.log += line

    def _is_response_successful(self, body: str) -> bool:
        return body.strip().split("\n")[-1] == "PASS"

    def send_command(self, cmd: str, has_body=True) -> str:
        self.port.write_timeout = self.write_timeout
        self.port.timeout = self.ack_timeout
        self._writeline(cmd)

        # Parse command echo
        line = self._readline()
        if line.lstrip(self.prompt) != f"{cmd}":
            raise JigClientException(f"Line not echoed back: {line}")

        # Parse command acknowledgement
        ack = self._readline()
        if ack != "+OK":
            raise JigClientException(f"Command not acknowledged: {ack}")

        # Parse command body
        if has_body:
            lines = []
            timeout = time.monotonic() + self.body_timeout
            while time.monotonic() < timeout:
                self.port.timeout = timeout - time.monotonic()
                line = self._readline()
                if self._is_end_of_body(line):
                    break
                lines.append(line)
            body = "\n".join(lines)

            # We didn't receive the end of body marker before timeout
            if not self._is_end_of_body(line):
                raise JigClientException("Did not receive end of body marker")

        return body

    def read_eeprom(self, key: str) -> bool:
        return self.send_command(f"READ_EEPROM_KEY {key}")

    def write_eeprom(self, key: str, value: str) -> bool:
        return self.send_command(f"WRITE_EEPROM {key}={value}")

    def run_test_cmd(self, cmd: str) -> bool:
        resp = self.send_command(cmd)
        return self._is_response_successful(resp)

    @staticmethod
    def find_device():
        """Returns the device name/path for the first XDOT developer board
        found connected. Identified by the device with: VID:PID=0D28:0204"""
        for p in comports():
            if p.vid == 0x0D28 and p.pid == 0x0204:
                return p.device
        return None
