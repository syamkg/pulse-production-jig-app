import logging
import shutil
import threading
import time
from pathlib import Path

import gpiozero


def main():
    logging.basicConfig(level=logging.DEBUG)

    reset_gpio_pin = 6
    xdot_volume = Path("/media/pi/XDOT")
    firmware = Path("firmware/test-firmware.bin")

    def do_copy():
        try:
            shutil.copy(firmware, xdot_volume / firmware.name)
        except:
            logging.exception("Oops:")

    reset_xdot_gpio = gpiozero.OutputDevice(reset_gpio_pin, initial_value=True)

    reset_xdot_gpio.off()
    logging.debug("_load_firmware() - starting copy")
    copy_thread = threading.Thread(target=do_copy)
    copy_thread.start()
    time.sleep(0.5)
    reset_xdot_gpio.on()
    logging.debug("_load_firmware() - waiting for copy")
    copy_thread.join()
    logging.debug("_load_firmware() - giving xdot 10 seconds")
    time.sleep(10)


if __name__ == "__main__":
    main()

"""
Run the following after copying the firmware 

screen /dev/ttyACM1 115200
test-port -n 0x0f 1
 
"""
