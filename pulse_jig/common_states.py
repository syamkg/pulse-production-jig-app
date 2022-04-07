import time
import serial
import logging
import sys


def bg_input(prompt):
    sys.stdout.write(prompt + "\n")
    return sys.stdin.readline().strip()


class CommonStates:
    def waiting_for_serial(self):
        """Blocks until the serial port is detected."""
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
        resp = bg_input("registeration status? [p:pass, f:fail registration, w: fail write hwspec")
        if resp == "w":
            self.fail()
        elif resp == "f":
            self.retry()
        else:
            serial = "W0-234-12345678"
            self._registrar.register_serial(serial)
            self.hwspec = {"serial": serial}
            self.proceed()

    def submitting_provisioning_record(self):
        if bg_input("submitted? [y: yes, n: no]") == "y":
            self._registrar.submit_provisioning_record(self.provisional_status, self.hwspec, self._ftf.log)
            self.proceed()
        else:
            self.retry()
