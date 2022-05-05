import logging
import shutil
import threading
import time
from pathlib import Path

import gpiozero

logger = logging.getLogger(__name__)


class PulseManager:
    def __init__(self, reset_pin: int, pcb_sense_pin: int, xdot_volume: str):
        self._reset_pin = gpiozero.OutputDevice(reset_pin, initial_value=True)
        self._pcb_sense_pin = gpiozero.Button(pcb_sense_pin, pull_up=True)
        self._xdot_volume = Path(xdot_volume)

    def reset_device(self):
        logger.debug("reset_device()")
        self._reset_pin.off()
        time.sleep(0.5)
        self._reset_pin.on()

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
        time.sleep(0.5)
        self._reset_pin.on()
        logger.debug("waiting for copy")
        copy_thread.join()
        logger.debug("giving xdot 10 seconds")
        time.sleep(10)
