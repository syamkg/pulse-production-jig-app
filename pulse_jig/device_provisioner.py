import logging
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Tuple, Optional

import gpiozero
import serial

from check_for_serial import check_for_serial
from jig_client import JigClient, JigClientException


class DeviceProvisioningFailure(Exception):
    """Exception raised when a functional test fails
    for any expected reason"""

    def __init__(
        self, msg, *, serial_no: Optional[str] = None, log: Optional[str] = None
    ):
        super().__init__(msg)
        self.msg = msg
        self.serial_no = serial_no
        self.log = log


class DeviceProvisioner:
    """Runs a functional test of a device and, if it passes, provisions the device with
    a serial number and other required details.
    """

    def __init__(self, reset_gpio_pin: int = 21):
        """Creates a device provisioner.
        :param port: the port the device is on
        """
        self._reset_xdot_gpio = gpiozero.OutputDevice(
            reset_gpio_pin, initial_value=True
        )
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

    def run(self, port: serial.Serial) -> Tuple[str, str]:
        """Runs a functional test of the device on the given port. If it
        passes, the device is provisioned with a serial number, manufacturer
        and the require LoRaWan details. If the device fails the functional
        tests or fails to respond as expected then the
        `DeviceProvisioningFailure` exception will be raised. If
        communication to the serial port is interrupted a
        `serial.serialutil.SerialException` will be raised.

        If a device already has a serial number no new serial will be
        provisioned.

        :param port: The port to communicate with the device on.

        :return: A tuple containing of (serial_no, log).
        """
        logging.debug("running_test() - loading test firmware")
        port.reset_output_buffer()
        port.reset_input_buffer()

        self._load_test_firmware()
        self._reset_device()

        client = JigClient(port, logger=logging.getLogger("JigClient"))

        def run_test(cmd: str):
            logging.info(f"running test for: {cmd}")
            if not client.run_test_cmd(cmd):
                raise DeviceProvisioningFailure(f"test failed: {cmd}", log=client.log)

        logging.debug("running_test() - skipping functional test firmware boot header")
        client.skip_boot_header()

        serial_no = None
        try:
            serial_no = client.read_eeprom("serial")
            if serial_no == "":
                serial_no = self.generate_serial()
                client.write_eeprom("serial", serial_no)
                logging.info(f"running_test() - serial generated: {serial_no}")

            run_test("test-self")
            run_test("test-lora-connect")
            run_test(f"test-port -n 0x0f 1")
        except JigClientException as err:
            raise DeviceProvisioningFailure(
                f"test failed: {str(err)}", serial_no=serial_no, log=client.log
            ) from err

        logging.debug("running_test() - loading production firmware")
        self._load_production_firmware()
        self._reset_device()

        logging.info("running_test() - checking for serial")
        detected_serial_no = check_for_serial(port, timeout=2)
        # We should check the serial is the same as that we generated
        # but we can't do that until the firmware actually persists
        # the serial across restarts
        # if (detected_serial_no is not None) or (detected_serial_no != serial_no):
        if detected_serial_no is None:
            raise DeviceProvisioningFailure(
                "detected serial mismatch", serial_no=detected_serial_no, log=client.log
            )
        logging.info(f"running_test() - serial found: {detected_serial_no}")

        return (serial_no, client.log)

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
            try:
                shutil.copy(firmware, self._xdot_volume / firmware.name)
            except:
                logging.exception("Oops:")

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