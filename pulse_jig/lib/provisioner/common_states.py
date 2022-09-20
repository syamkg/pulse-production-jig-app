import logging
import time

import serial

from pulse_jig.config import settings
from ..jig_client import JigClient

logger = logging.getLogger("provisioner")


class CommonStates:
    def loading_test_firmware(self):
        self._ftf = JigClient(self._port)

        # Skip the boot header from the device plugging in
        # Then we need to clear logs, so we don't have junk in cloud logs
        self._ftf.skip_boot_header()
        self._ftf.reset_logs()

        if not settings.app.skip_firmware_load:
            self._pulse_manager.load_firmware(self._test_firmware_path)

        # Now we reset the device manually
        # and read the header from that.
        self._pulse_manager.reset_device()
        header = self._ftf.read_boot_header(with_prompt=True)

        if not settings.app.skip_firmware_load and not validate_test_firmware_load(header):
            logger.error("Failed to load the Test firmware")
            self.fail()
            return

        self.test_firmware_version = self._ftf.firmware_version()

        self.proceed()

    def waiting_for_network(self):
        """Blocks until internet is connected & API endpoints are reachable"""
        while True:
            if self.has_network():
                self.proceed()
                break

    def waiting_for_serial(self):
        """Blocks until the serial port is detected."""
        self._port.close()
        while True:
            try:
                self._port.open()
                break
            except serial.serialutil.SerialException as e:
                logger.error(str(e))
                logger.info("Retrying...")
                time.sleep(1)
        self.proceed()


def validate_test_firmware_load(header: str) -> bool:
    return ("Starting Functional Tests Firmware" and ">") in header
