from pulse_jig.jig_client import JigClient, JigClientException
import logging
import time
import serial
import re
import gpiozero
import shutil
from pathlib import Path
import threading
import uuid
from typing import Tuple


class FunctionalTestFailure(Exception):
    """Exception raised when a functional test fails
    for any expected reason"""

    def __init__(self, msg, *, serial_no=None, log=None):
        super().__init__(msg)
        self.msg = msg
        self.serial_no = serial_no
        self.log = log


class FunctionalTest:
    def __init__(self, port: serial.Serial):
        """Tests and provisions a serial number to the device on the given port.
        :param port: the port the device is on
        """
        self._port = port
        self._reset_xdot_gpio = gpiozero.OutputDevice(21, initial_value=True)
        self._production_firmware_path = Path("firmware/prod-firmware.bin")
        self._test_firmware_path = Path("firmware/test-firmware.bin")
        self._xdot_volume = Path("/media/pi/XDOT")

        if not self._production_firmware_path.is_file():
            raise RuntimeError(
                f"Couldn't find production firmware at: {self.production_firmware_path}"
            )
        if not self._test_firmware_path.is_file():
            raise RuntimeError(
                f"Couldn't find production firmware at: {self.test_firmware_path}"
            )
        if not self._xdot_volume.exists():
            raise RuntimeError(f"Couldn't find xdot volume at: {self.xdot_volume}")

    def run(self) -> Tuple[str, str]:
        """Runs the test and returns the provisioned serial number and test logs on
        success. If the test fails a `FunctionalTestFailure` will be raised. If
        communication to the serial port is interrupted a
        `serial.serialutil.SerialException` will be raised.

        :return: A tuple containing of (serial_no, log).
        """
        logging.debug("running_test() - loading test firmware")
        self._port.reset_output_buffer()
        self._port.reset_input_buffer()

        self._load_test_firmware()
        self._reset_device()

        client = JigClient(self._port, logger=logging.getLogger("JigClient"))

        def run_test(cmd: str):
            logging.info(f"running test for: {cmd}")
            if not client.run_test_cmd(cmd):
                raise FunctionalTestFailure(f"test failed: {cmd}")

        logging.debug("running_test() - skipping functional test firmware boot header")
        client.skip_boot_header()

        serial_no = None
        try:
            serial_no = client.read_eeprom("serial")
            if serial_no == "":
                serial_no = self.generate_serial()
                client.write_eeprom("serial", serial_no)
                logging.info(f"running_test() - serial generated: {serial_no}")

            run_test("SELF_TEST")
            run_test("TEST_LORA_CONNECT")

            for port in range(1, 5):
                run_test(f"TEST_PORT_I2C {port}")
                run_test(f"TEST_PORT_SPI {port}")
                run_test(f"TEST_PORT_GIN_GOUT_LOOP {port}")
        except JigClientException as err:
            raise FunctionalTestFailure(
                f"test failed: {str(err)}", serial_no=serial_no, log=client.log
            ) from err

        logging.debug("running_test() - loading production firmware")
        self._load_production_firmware()
        self._reset_device()

        logging.info("running_test() - checking for serial")
        detected_serial_no = self._check_for_serial(timeout=2)
        # We should check the serial is the same as that we generated
        # but we can't do that until the firmware actually persists
        # the serial across restarts
        # if (detected_serial_no is not None) or (detected_serial_no != serial_no):
        if detected_serial_no is None:
            raise FunctionalTestFailure("detected serial mismatch")
        logging.info(f"running_test() - serial found: {detected_serial_no}")

        return (serial_no, client.log)

    def _check_for_serial(self, timeout=0):
        resp = ""
        end_time = time.monotonic() + timeout
        while timeout == 0 or end_time > time.monotonic():
            while self._port.in_waiting > 0:
                resp += self._port.read(self._port.in_waiting).decode("utf-8")
            matches = re.search(r"^Serial: (.*)$", resp, re.MULTILINE)
            if matches:
                return matches.group(1).strip()
            if timeout == 0:
                break
        return None

    def _reset_device(self):
        logging.debug("reset_device()")
        self._reset_xdot_gpio.off()
        time.sleep(0.5)
        self._reset_xdot_gpio.on()

    def _generate_serial(self):
        return uuid.uuid4()

    def _load_test_firmware(self):
        self._load_firmware(self._test_firmware_path)

    def _load_production_firmware(self):
        self._load_firmware(self._production_firmware_path)

    def _load_firmware(self, firmware: Path):
        # Note that on macos the copy returns instantly but on linux
        # it doesn't appear to return until after the reset pin is
        # released.
        # Improve error checking - take into account that it is
        # being run in a thread.
        def do_copy():
            shutil.copy(firmware, self._xdot_volume / firmware.name)

        self._reset_xdot_gpio.off()
        logging.debug("_load_firmware() - starting copy")
        copy_thread = threading.Thread(target=do_copy)
        copy_thread.start()
        time.sleep(0.5)
        self._reset_xdot_gpio.on()
        logging.debug("_load_firmware() - waiting for copy")
        copy_thread.join()
        logging.debug("_load_firmware() - giving xdot 10 seconds")
        time.sleep(10)
