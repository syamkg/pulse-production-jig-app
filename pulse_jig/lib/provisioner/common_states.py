import logging
import sys
import time

import serial

logger = logging.getLogger("provisioner")


def bg_input(prompt: str):
    sys.stdout.write(prompt + "\n")
    return sys.stdin.readline().strip()


class CommonStates:
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
