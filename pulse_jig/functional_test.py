from .jig_client import JigClient, JigClientException
import logging
import time
import serial
import os
from transitions import Machine
import re
import gpiozero
import shutil
from pathlib import Path
import threading
import uuid


class FunctionalTestFailedException(Exception):
    '''Exception raised when a the functional test fails
    for any expected reason'''


class FakeGPIO:
    def __init__(self, filename: str):
        self.filename = filename
        if not os.path.exists(self.filename):
            os.mkfifo(self.filename)
        fd = os.open(
            self.filename,
            os.O_RDONLY | os.O_NONBLOCK)
        self.pipe = os.fdopen(fd, 'rb')

    def __del__(self):
        self.pipe.close()
        os.unlink(self.filename)

    def test(self):
        return self.pipe.read().strip() != b''

    def wait(self):
        while self.pipe.read().strip() == b'':
            time.sleep(1)


class FunctionalTest:
    def __init__(self, dev):
        self.port = serial.Serial()
        self.port.port = dev
        self.port.baudrate = 115200
        self.listeners = []
        self.reset_xdot_gpio = gpiozero.OutputDevice(21)
        self.reset_xdot_gpio.on()
        self.pcb_sense_gpio = gpiozero.Button(5, pull_up=True)
        self.production_firmware = "firmware/prod-firmware"
        self.test_firmware = "firmware/test-firmware"
        self.xdot_volume = Path("/media/pi/XDOT")

        self.machine = Machine(
            model=self,
            states=[
                'stopped',
                'waiting_for_serial',
                'waiting_for_pcb',
                'running_test'
            ],
            initial='stopped')

        self.machine.add_transition(
            'start',
            'stopped',
            'waiting_for_serial',
        )

        self.machine.add_transition(
            'stop',
            '*',
            'stopped'
        )

        self.machine.add_transition(
            'serial_lost',
            '*',
            'waiting_for_serial',
            after='_close_port'
        )

        self.machine.add_transition(
            'serial_found',
            'waiting_for_serial',
            'waiting_for_pcb',
        )

        self.machine.add_transition(
            'pcb_connected',
            'waiting_for_pcb',
            'running_test',
        )

        self.machine.add_transition(
            'test_successful',
            'running_test',
            'waiting_for_pcb'
        )

        self.machine.add_transition(
            'test_failed',
            'running_test',
            'waiting_for_pcb',
            '_log_test_failed'
        )

        self.machine.add_transition(
            'serial_detected',
            'waiting_for_pcb',
            'waiting_for_pcb',
            after='display_serial'
        )

    def _log_test_failed(self):
        logging.info("TEST FAILED")

    def _close_port(self):
        self.port.close()

    def _send_event(self, event, data={}):
        for listener in self.listeners:
            listener(event, data)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def run(self):
        self.start()

        def fn_not_found():
            raise RuntimeError("Could not find state handler: ")

        while self.state != 'stopped' and self.state != "test_failed":
            self._send_event(self.state)
            fn = getattr(self, self.state, fn_not_found)
            if fn:
                logging.info(f"running state {self.state}")
                fn()

    def display_serial(self, serial):
        logging.info(f"display_serial({serial})")
        self._send_event('serial_detected', serial)

    def waiting_for_serial(self):
        logging.info("waiting_for_serial()")
        while True:
            try:
                self.port.open()
                self.serial_found()
                return
            except serial.serialutil.SerialException:
                time.sleep(1)

    def waiting_for_pcb(self):
        logging.info("waiting_for_pcb()")
        while True:
            try:
                if self.is_pcb_connected():
                    self.pcb_connected()
                    return
                else:
                    serial = self.check_for_serial()
                    if serial:
                        self.serial_detected(serial)
                        return
                    time.sleep(1)
            except OSError as err:
                # TODO improve
                # 6 on macos
                # 5 on pi
                if err.errno == 6 or err.errno == 5:
                    self.serial_lost()
                    return
                else:
                    raise err

    def running_test(self) -> bool:
        self.load_test_firmware()
        self.reset_device()

        try:
            self.port.reset_output_buffer()
            self.port.reset_input_buffer()
            client = JigClient(
                self.port,
                logger=logging.getLogger("JigClient"))
        except serial.serialutil.SerialException:
            logging.error("could not connect to serial device")
            self.test_failed()
            return

        logging.info(
            "running_test() - skipping functional test firmware boot header")
        client.skip_boot_header()

        try:
            serial_no = client.read_eeprom('serial')
            if serial_no == '':
                serial_no = self.generate_serial()
                client.write_eeprom('serial', serial_no)
                logging.info(f"running_test() - serial generated: {serial_no}")

            def run_test(cmd):
                logging.info(f"running test for: {cmd}")
                if not client.run_test_cmd(cmd):
                    raise FunctionalTestFailedException(f"test failed: {cmd}")

            run_test("SELF_TEST")
            run_test("TEST_LORA_CONNECT")

            for port in range(1, 5):
                run_test(f"TEST_PORT_I2C {port}")
                run_test(f"TEST_PORT_SPI {port}")
                run_test(f"TEST_PORT_GIN_GOUT_LOOP {port}")
        except (FunctionalTestFailedException, JigClientException) as err:
            logging.error(err)
            self.test_failed()
            return False
        except serial.serialutil.SerialException as err:
            logging.error(err)
            self.serial_lost()
            return False

        self.load_production_firmware()
        self.reset_device()

        logging.info("running_test() - checking for serial")
        detected_serial = self.check_for_serial(timeout=2, debug=True)
        # We should check the serial is the same as that we generated
        # but we can't do that until the firmware actually persists
        # the serial across restarts
        #if (detected_serial is not None) or (detected_serial != serial_no):
        if (detected_serial is None):
            self.test_failed()
            return False

        logging.info(f"running_test() - serial found: {detected_serial}")
        self._send_event('test_passed', serial_no)

        logging.warn("waiting_for_pcb_removal()")
        self.waiting_for_pcb_removal()
        self.test_successful()
        self._send_event('test_finished')
        return True

    def check_for_serial(self, timeout=0, debug=False):
        resp = ""
        end_time = time.monotonic() + timeout
        while timeout == 0 or end_time > time.monotonic():
            while self.port.in_waiting > 0:
                resp += self.port\
                    .read(self.port.in_waiting)\
                    .decode('utf-8')
            matches = re.search(r"^Serial: (.*)$", resp, re.MULTILINE)
            if matches:
                return matches.group(1).strip()
            if timeout == 0:
                break
        return None

    def waiting_for_pcb_removal(self):
        self.pcb_sense_gpio.wait_for_release()

    def is_pcb_connected(self):
        return self.pcb_sense_gpio.is_held

    def reset_device(self):
        logging.info("reset_device()")
        self.reset_xdot_gpio.off()
        time.sleep(0.5)
        self.reset_xdot_gpio.on()

    def generate_serial(self):
        return uuid.uuid4()

    def _load_firmware(self, firmware):
        def do_copy():
            shutil.copy(firmware, self.xdot_volume / Path(firmware).name)

        self.reset_xdot_gpio.off()
        logging.debug("_load_firmware() - starting copy")
        copy_thread = threading.Thread(target=do_copy)
        copy_thread.start()
        time.sleep(0.5)
        self.reset_xdot_gpio.on()
        logging.debug("_load_firmware() - waiting for copy")
        copy_thread.join()
        logging.debug("_load_firmware() - giving xdot 10 seconds")
        time.sleep(10)

    def load_test_firmware(self):
        logging.info("load_test_firmware()")
        self._load_firmware('firmware/test-firmware.bin')

    def load_production_firmware(self):
        logging.info("load_production_firmware()")
        self._load_firmware('firmware/prod-firmware.bin')
