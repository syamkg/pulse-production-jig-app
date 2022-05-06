import logging
import sys
import time

import serial


def bg_input(prompt: str):
    sys.stdout.write(prompt + "\n")
    return sys.stdin.readline().strip()


class CommonStates:
    def waiting_for_serial(self):
        """Blocks until the serial port is detected."""
        self._port.close()
        while True:
            try:
                self._port.open()
                break
            except serial.serialutil.SerialException as e:
                logging.error(str(e))
                logging.info("Retrying...")
                time.sleep(1)
        self.proceed()

    def registering_device(self):
        registered = self._registrar.register_serial(self.hwspec)
        if registered:
            self.proceed()
        else:
            self.retry()

    def submitting_provisioning_record(self):
        success = self._registrar.submit_provisioning_record(self.hwspec, self.provisional_status.name, self._ftf.log)
        if success:
            self.proceed()
        else:
            self.retry()
