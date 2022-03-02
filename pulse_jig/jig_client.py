import logging
import os
import time
from typing import Optional

import serial

# Import the correct platform specific comports implementation.
# There doesn't seem to be a better way of doing this at the moment.
if os.name == "nt":  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == "posix":
    from serial.tools.list_ports_posix import comports
else:
    raise ImportError(
        "Sorry: no implementation for your platform ('{}') available".format(os.name)
    )


class JigClientException(Exception):
    """JigClient exception. Raised if the device doesn't respond to the Jig
    Function Test Protocol correctly."""


class JigClient:
    def __init__(self, port: serial.Serial, logger: Optional[logging.Logger] = None):
        """Creates a JigClient for communicating over the given port with the
        Function Test Protocol. Methods will raise a JigClientException if a
        device does not respond to the protocol as expected.

        All communication with the device is recorded and can be retrieved via
        `jig_client.log`.

        :param port: The device to communicate over.
        :param logger: If provided then all communication will be sent to the
        logger at the debug level.
        """
        self._port = port
        self._write_timeout = 1
        self._ack_timeout = 0.5
        self._body_timeout = 2
        self._last_error = None
        self._log = ""
        self._terminator = "\r\n"
        self._prompt = "> "
        self._logger = logger

    def _is_end_of_body(self, line: str) -> None:
        return line == "."

    def skip_boot_header(self) -> None:
        self._read_until_prompt(2)

    def _read_until_prompt(self, timeout: float) -> None:
        self._port.timeout = 0.1
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            if self._readline() == self._prompt:
                break

    def _readline(self) -> str:
        line = self._port.readline().decode("utf-8")
        self._log += line
        line = line.rstrip(self._terminator)
        if self._logger is not None and line != "":
            self._logger.debug("DEV: " + line)
        return line

    def _writeline(self, line: str) -> None:
        if self._logger is not None:
            self._logger.debug("JIG: " + line)
        line += "\r"
        self._port.write(f"{line}".encode("utf-8"))
        self._log += line

    def _is_response_successful(self, body: str) -> bool:
        return body.strip().split("\n")[-1] == "PASS"

    @property
    def log(self):
        return self._log

    def send_command(self, cmd: str, has_body=True) -> str:
        """Sends the given command to the device and returns
        the body from the response.
        :param cmd: the command to send, including any parameters.
        :param has_body: True if the command is expected to return a body.
        :return: The body of the command's response, None if has_body
        was False.
        """
        self._port.write_timeout = self._write_timeout
        self._port.timeout = self._ack_timeout
        self._writeline(cmd)

        # Parse command echo. Ignore any prompt at the start of the
        # response if present
        line = self._readline()
        if line.lstrip(self._prompt) != cmd:
            raise JigClientException(f"Line not echoed back: {line}")

        # Parse command acknowledgement
        ack = self._readline()
        if ack != "+OK":
            raise JigClientException(f"Command not acknowledged: {ack}")

        # Parse command body
        body = None
        if has_body:
            lines = []
            timeout = time.monotonic() + self._body_timeout
            while time.monotonic() < timeout:
                self._port.timeout = timeout - time.monotonic()
                line = self._readline()
                if self._is_end_of_body(line):
                    break
                lines.append(line)
            body = "\n".join(lines)

            # We didn't receive the end of body marker before timeout
            if not self._is_end_of_body(line):
                raise JigClientException("Did not receive end of body marker")

        return body

    def read_eeprom(self, key: str) -> str:
        """Sends a ``hwsoec-load & `hwspec-get` commands to the device.
        :param key: the key to read
        :return: The command's response body.
        """
        self.send_command(f"hwspec-load")
        return self.send_command(f"hwspec-get {key}")

    def write_eeprom(self, key: str, value: str) -> str:
        """Sends a `hwspec-set` & `hwspec-save` commands to the device.
        :param key: the key to write
        :param value: the value to write against the key
        :return: The command's response body.
        """
        self.send_command(f"hwspec-set {key} {value}")
        return self.send_command(f"hwspec-save")

    def run_test_cmd(self, cmd: str) -> bool:
        """Runs the given test command and whether it passed or
        not. The test command is expected to conform to the standard
        test output - the last line of the body should be either
        `PASS` or `FAIL` to indicate the status.

        :param cmd: the command str to send, including parameters.
        :return: True if the test passed, false otherwise.
        """
        resp = self.send_command(cmd)
        return self._is_response_successful(resp)

    @staticmethod
    def find_device() -> Optional[str]:
        """Returns the device name/path for the first XDOT developer board
        found connected. Identified by the device with: VID:PID=0D28:0204.

        :return: if found, the path to the device (eg. /dev/ttyACM1), otherwise
        None if not found.
        """
        for p in comports():
            if p.vid == 0x0D28 and p.pid == 0x0204:
                return p.device
        return None
