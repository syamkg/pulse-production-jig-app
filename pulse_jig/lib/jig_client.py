import logging
import os
import time
from typing import Optional

import serial

from .timeout import Timeout, TimeoutNever

logger = logging.getLogger("jig_client")

# Import the correct platform specific comports implementation.
# There doesn't seem to be a better way of doing this at the moment.
if os.name == "nt":  # sys.platform == 'win32':
    # Commented out to avoid mypy errors and we don't use windows - reenable and fix if you use windows :)
    # from serial.tools.list_ports_windows import comports
    pass
elif os.name == "posix":
    from serial.tools.list_ports_posix import comports
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))


def _to_port_flags(port_number: int):
    """Convert a port number to equivalent hex bit field value"""
    return hex(pow(2, port_number - 1))


class JigClientException(Exception):
    """JigClient exception. Raised if the device doesn't respond to the Jig
    Function Test Protocol correctly."""

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class JigClient:
    class CommandFailed(Exception):
        """JigClient exception. Raised if the device doesn't respond to the Jig
        Function Test Protocol correctly."""

        def __init__(self, msg):
            super().__init__(msg)
            self.msg = msg

    def __init__(self, port: serial.Serial):
        """Creates a JigClient for communicating over the given port with the
        Function Test Protocol. Methods will raise a JigClientException if a
        device does not respond to the protocol as expected.

        All communication with the device is recorded and can be retrieved via
        `jig_client.log`.

        :param port: The device to communicate over.
        """
        self._port = port
        self._write_timeout = 1
        self._ack_timeout = 0.5
        self._last_error = None
        self._log = ""
        self._terminator = "\r\n"
        self._prompt = "> "
        self._boot_header_separator = "=" * 62

    @staticmethod
    def _is_end_of_body(line: str) -> bool:
        return line == "."

    def skip_boot_header(self) -> None:
        self._read_until_prompt(5)
        time.sleep(0.1)

    def _read_until_prompt(self, timeout: float) -> None:
        # Read until the "prompt ("> ") is found.
        # But if the prompt is in the first line read, will ignore that.
        # The reason being, that's not the prompt we're after.
        # That prompt is from the last command - not the one from the boot header
        self._port.timeout = 0.1
        timer = Timeout(timeout)
        lines_read = 0
        while timer.active:
            lines_read += 1
            if self._readline() == self._prompt and lines_read > 1:
                break

    def read_boot_header(self) -> str:
        reading_header = False
        header = ""

        self._port.timeout = 0.1
        timer = Timeout(2)

        while timer.active:
            line = self._readline()

            # Boot header separator is in the beginning and the end of the boot header.
            # So we'll toggle-on the `reading_header` when we found the beginning separator
            # and toggle-off it when we have end separator
            if line == self._boot_header_separator:
                reading_header = not reading_header
                header += line + "\n"
                continue

            if reading_header:
                header += line + "\n"

        return header.strip()

    def _readline(self) -> str:
        line = self._port.readline().decode("utf-8")
        self._log += line
        line = line.rstrip(self._terminator)
        if line != "":
            logger.debug("DEV: " + line)
        return line

    def _writeline(self, line: str) -> None:
        logger.debug("JIG: " + line)
        line += "\r"
        self._port.write(f"{line}".encode("utf-8"))
        self._log += line

    def _is_response_successful(self, body: str) -> bool:
        return body.strip().split("\n")[-1] == "PASS"

    @property
    def log(self):
        return self._log

    def reset_logs(self):
        self._log = ""

    def send_command(self, cmd: str, has_body: bool = True, timeout: int = 2) -> str:
        """Sends the given command to the device and returns
        the body from the response.
        :param cmd: the command to send, including any parameters.
        :param has_body: True if the command is expected to return a body.
        :param timeout: Timeout for reading from device
                        No timeout == (timeout <= 0)

        :return: The body of the command's response, None if has_body
        was False.
        """
        self._port.write_timeout = self._write_timeout
        self._port.timeout = self._ack_timeout
        self._writeline(cmd)

        self._parse_command_echo(cmd)
        self._parse_command_ack()

        body = None
        if has_body:
            body = self._parse_command_body(timeout)

        return body or ""

    def _parse_command_echo(self, cmd):
        # Parse command echo. Ignore any prompt at the start of the
        # response if present
        line = self._readline()
        if line.lstrip(self._prompt) != cmd:
            raise JigClientException(f"Line not echoed back: {line}")

    def _parse_command_ack(self):
        # Parse command acknowledgement
        ack = self._readline()
        if ack.startswith("-ERR"):
            raise JigClient.CommandFailed(ack[4:])  # Strip -ERR prefix
        elif ack != "+OK":
            raise JigClientException(f"Command not acknowledged: {ack}")

    def _parse_command_body(self, timeout: int):
        # Parse command body
        line = ""
        lines = []

        timer = Timeout(timeout) if timeout >= 0 else TimeoutNever()

        while not timer.expired:
            self._port.timeout = timer.remaining
            line = self._readline()

            if self._is_end_of_body(line):
                break

            if len(line) != 0:
                lines.append(line)

        body = "\n".join(lines)

        # We didn't receive the end of body marker before timeout
        if not self._is_end_of_body(line):
            raise JigClientException("Did not receive end of body marker")

        return body

    def platform(self, cmd: str) -> str:
        """Sends a `platform` command to the device.

        :param cmd: the platform command to run
        :return: The command's response body.
        """
        return self.send_command(f"platform {cmd}", False)

    def enable_external_port(self, port_number: int):
        """Need to run these commands in-order to enable
        external ports to read hw-spec"""
        self.platform("prp-enable")
        self.platform("extern-ports-enable")
        self.send_command(f"port-enable {port_number}", False)

    def disable_external_port(self):
        """After doing what we want, we need to disable
        previously enabled external ports"""
        self.send_command("port-enable none", False)
        self.platform("extern-ports-disable")
        self.platform("prp-disable")

    def hwspec_load(self, target: str) -> bool:
        """Sends a `hwspec-load` command to the device.
        :param target: the target to load hwspec from
        :return: The command's response body.
        """
        try:
            self.send_command(f"hwspec-load {target}", False)
            return True
        except JigClient.CommandFailed:
            return False

    def hwspec_get(self, key: str) -> str:
        """Sends a `hwspec-get` command to the device.
        :param key: the key to read
        :return: The command's response body.
        """
        return self.send_command(f"hwspec-get {key}")

    def hwspec_set(self, key: str, value: str) -> str:
        """Sends a `hwspec-set` command to the device.
        :param key: the key to write
        :param value: the value to write against the key
        :return: The command's response body.
        """
        return self.send_command(f"hwspec-set {key} {value}", has_body=False)

    def hwspec_save(self, target: str) -> str:
        """Sends a `hwspec-set` command to the device.
        :param target: the target to save the hwspec to
        :return: The command's response body.
        """
        return self.send_command(f"hwspec-save {target}", has_body=False)

    def hwspec_destroy(self, target: str) -> str:
        """Sends a `hwspec-destroy` command to the device.
        :param target: the target to destroy the hwspec from
        :return: The command's response body.
        """
        return self.send_command(f"hwspec-destroy {target}", has_body=False)

    def test_ta3k(self, port: int) -> bool:
        """Run `test-ta3k` command on the given port
        :param port: Port number as an int
        :return bool: If test command is a pass or fail
        """
        return self.run_test_cmd(f"test-ta3k -v {_to_port_flags(port)} 1", timeout=10)

    def test_self(self) -> bool:
        """Run `test-self` command on the device
        :return bool: If test command is a pass or fail
        """
        return self.run_test_cmd("test-self -v", timeout=10)

    def test_port(self) -> bool:
        """Run `test-port` command on all ports of the device
        :return bool: If test command is a pass or fail
        """
        return self.run_test_cmd("test-port -v 0x0f 1", timeout=30)

    def test_lora_connect(self, sub_band: str, join_eui: str, app_key: str) -> bool:
        """Run `test-lora-connect` command on the device
        :return bool: If test command is a pass or fail
        """
        return self.run_test_cmd(f"test-lora-connect {sub_band} {join_eui} {app_key}", timeout=90)

    def probe_await_connect(self) -> Optional[int]:
        """Sends `probe-await connect` command to the device.
        This will wait indefinitely until a probe is connected.
        :return: Optional connected port number.
        """
        resp = self.send_command("probe-await connect", timeout=-1)
        if "Found on port" not in resp:
            return None
        return int((resp.split(":", 1)[1]).strip())

    def probe_await_recovery(self):
        """Sends `probe-await recovery` command to the device.
        This will wait indefinitely until the probe is removed.
        :return: The command's response body.
        """
        return self.send_command("probe-await recovery", timeout=-1)

    def run_test_cmd(self, cmd: str, timeout: int = 2) -> bool:
        """Runs the given test command and whether it passed or
        not. The test command is expected to conform to the standard
        test output - the last line of the body should be either
        `PASS` or `FAIL` to indicate the status.

        :param cmd: the command str to send, including parameters.
        :param timeout: The timeout for each command
        :return: True if the test passed, false otherwise.
        """
        resp = self.send_command(cmd, timeout=timeout)
        return self._is_response_successful(resp)

    def lora_deveui(self) -> str:
        """Sends a `lora-deveui` command to the device.
        :return: The command's response body.
        """
        return self.send_command("lora-deveui get")

    def lora_config(self, join_eui: str, app_key: str) -> str:
        """Sends a `lora-config` command to the device.
        This will configure the LoRa settings on the device.

        :param join_eui: LoRa join_eui str
        :param app_key: LoRa app_key str
        :return: The command's response body.
        """
        return self.send_command(f"lora-config {join_eui} {app_key}")

    def pulse_cfg_init(self) -> str:
        """Sends a `pulse-cfg init` command to the device.
        Initializes nvm with a default config.
        (overwrites any existing config.)
        :return: The command's response body.
        """
        return self.send_command(f"pulse-cfg init")

    def pulse_cfg_load(self) -> str:
        """Sends a `pulse-cfg load` command to the device.
        :return: The command's response body.
        """
        return self.send_command(f"pulse-cfg load")

    def pulse_cfg_save(self) -> str:
        """Sends a `pulse-cfg save` command to the device.
        :return: The command's response body.
        """
        return self.send_command(f"pulse-cfg save")

    def pulse_cfg_set_pulse(self, key: str, value: int) -> str:
        """Configure the pulse with the given values
        :param key: the key to write
        :param value: the value to write against the key
        :return: The command's response body.
        """
        return self.send_command(f"pulse-cfg set pulse {key} {value}")

    def firmware_version(self) -> str:
        """Sends a `firmware_version` command to the device.
        :return: The command's response body.
        """
        return self.send_command("firmware-version")

    def hwchunk_get_probe(self) -> str:
        """Read from the "probe" chunk of a probe
        :return ProbeSpec: Parsed output
        """
        return self.send_command(f"hwchunk dump probe probe")

    def hwchunk_write_probe(self, cable_length: int) -> str:
        """Write to the "probe" chunk of a probe
        :probe_spec: What's going to be written
        :return: The command's response body.
        """
        return self.send_command(f"hwchunk write probe probe {cable_length}")

    def hwchunk_verify(self, target: str) -> bool:
        """Sends hwchunk verify command to the device
        :target: Target device pulse or probe
        :return bool: If the chunk list is correct and all CRCs match."""
        resp = self.send_command(f"hwchunk verify {target}")
        return self._is_response_successful(resp)

    def hwchunk_clear(self, target: str) -> str:
        """Sends hwchunk clear command to the device
        :target: Target device pulse or probe
        :return str: The command's response body."""
        return self.send_command(f"hwchunk clear {target}")

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
