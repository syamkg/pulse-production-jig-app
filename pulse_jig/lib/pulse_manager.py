import logging
import shutil
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import gpiozero
import serial

from .timeout import Timeout, TimeoutNever

logger = logging.getLogger(__name__)


class PulseManager:
    def __init__(self, reset_pin: int, pcb_sense_pin: int, xdot_volume: str):
        self._reset_pin = gpiozero.OutputDevice(reset_pin, initial_value=True)
        self._pcb_sense_pin = gpiozero.Button(pcb_sense_pin, pull_up=True)
        self._xdot_volume = Path(xdot_volume)

    def reset_device(self):
        logger.debug("reset_device()")
        self._reset_pin.off()
        time.sleep(0.2)
        self._reset_pin.on()
        time.sleep(0.2)

    @property
    def is_connected(self):
        return self._pcb_sense_pin.is_pressed

    def await_removal(self):
        self._pcb_sense_pin.wait_for_release()

    def on_removal(self, callback):
        self._pcb_sense_pin.when_released = callback

    def load_firmware(self, firmware_path: Path):
        firmware_path = Path(firmware_path)
        # Note that on macos the copy returns instantly but on linux
        # it doesn't appear to return until after the reset pin is
        # released.
        # Improve error checking - take into account that it is
        # being run in a thread.

        def do_copy():
            try:
                shutil.copy(str(firmware_path), self._xdot_volume / firmware_path.name)
            except IOError as e:
                logger.error(str(e))

        self._reset_pin.off()
        logger.debug("starting copy")
        copy_thread = threading.Thread(target=do_copy)
        copy_thread.start()
        time.sleep(0.2)
        self._reset_pin.on()
        logger.debug("waiting for copy")
        copy_thread.join()
        time.sleep(0.2)

    def check_for_header(
        self, port: serial.Serial, timeout: float = None, continue_test: Optional[Callable[[], bool]] = None
    ) -> bool:
        """Monitors the port for a boot header from the firmware.
        Keep reading until the end of the boot header to verify.
        If found return True.
        The check consumes all available data
        from the port.

        :param port: the serial port to monitor
        :param timeout: The maximum number of seconds to monitor for.
                        None to wait indefinitely
        :return bool:
        """
        terminator = "\r\n"
        boot_header_separator = "=" * 62
        if continue_test is None:
            continue_test = lambda: True

        timer = Timeout(timeout) if timeout else TimeoutNever()
        while continue_test() and not timer.expired:
            time.sleep(0.2)
            boot_header_size = 10  # Number of lines including the separator & starting blank line
            boot_header_separator_count = 0
            line_count = 0
            while port.in_waiting > 0:
                line = port.readline().decode("utf-8")
                line = line.rstrip(terminator)
                line_count += 1
                if line == boot_header_separator:
                    boot_header_separator_count += 1
                if boot_header_separator_count == 2 and line_count == boot_header_size:
                    return True
        return False
