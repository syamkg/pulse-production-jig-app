from .jig_client import JigClient, JigClientException
import logging
import time
import serial
import os
from transitions import Machine
import traceback
import re


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
        self.fake_gpio = FakeGPIO('./is-pcb-connected')

        self.machine = Machine(
            model=self,
            states=[
                'stopped',
                'wait_for_serial',
                'wait_for_pcb',
                'running_test'
            ],
            initial='stopped')

        self.machine.add_transition(
            'start',
            'stopped',
            'wait_for_serial',
        )

        self.machine.add_transition(
            'serial_lost',
            '*',
            'wait_for_serial',
            after='_close_port'
        )

        self.machine.add_transition(
            'serial_found',
            'wait_for_serial',
            'wait_for_pcb',
        )

        self.machine.add_transition(
            'got_pcb',
            'wait_for_pcb',
            'running_test',
        )

        self.machine.add_transition(
            'test_successful',
            'running_test',
            'wait_for_pcb'
        )

        self.machine.add_transition(
            'test_failed',
            'running_test',
            'wait_for_pcb'
        )

        self.machine.add_transition(
            'serial_detected',
            'wait_for_pcb',
            'wait_for_pcb',
            after='display_serial'
        )

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
            raise RuntimeError("Could not find state handler")

        while True:
            self._send_event(self.state)
            fn = getattr(self, self.state, fn_not_found)
            if fn:
                logging.info(f"running state {self.state}")
                fn()

    def display_serial(self, serial):
        logging.info(f"display_serial({serial})")
        self._send_event('serial_detected', serial)

    def wait_for_serial(self):
        logging.info("wait_for_serial()")
        while True:
            try:
                logging.debug("checking serial connection")
                self.port.open()
                self.serial_found()
                return
            except serial.serialutil.SerialException:
                time.sleep(1)

    def wait_for_pcb(self):
        logging.info("wait_for_pcb()")
        while True:
            try:
                if self.is_pcb_connected():
                    self.got_pcb()
                    return
                else:
                    serial = self.check_for_serial()
                    if serial:
                        self.serial_detected(serial)
                        return
                    time.sleep(1)
            except OSError as err:
                if err.errno == 6:
                    self.serial_lost()
                    return
                else:
                    raise err

    def running_test(self) -> bool:
        self.load_test_firmware()
        self.reset_device()

        try:
            client = JigClient(
                self.port,
                logger=logging.getLogger("JigClient"))
        except serial.serialutil.SerialException:
            logging.error("could not connect to serial device")
            self.test_failed()
            return

        try:
            serial_no = client.read_eeprom('serial')
            if serial_no == '':
                serial_no = self.register_device()

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
        # TODO: detect serial
        # TODO: register pass
        self._send_event('test_passed', '03-239589238692-234')

        self.wait_for_pcb_removal()
        self.test_successful()
        self._send_event('test_finished')
        return True

    def check_for_serial(self):
        resp = ""
        while self.port.in_waiting > 0:
            resp += self.port\
                .read(self.port.in_waiting)\
                .decode('utf-8')
        matches = re.search(r"^Serial: (.*)$", resp, re.MULTILINE)
        if matches:
            return matches.group(1).strip()
        return None

    def wait_for_pcb_removal(self):
        logging.warn("wait_for_pcb_removal() - not implemented")
        self.fake_gpio.wait()

    def reset_device(self):
        time.sleep(1)
        logging.warn("reset_device() - not implemented")

    def register_device(self):
        logging.warn("register_device() - not implemented")

    def is_pcb_connected(self):
        return self.fake_gpio.test()

    def load_test_firmware(self):
        time.sleep(1)
        logging.warn("load_test_firmware() - not implemented")
        pass

    def load_production_firmware(self):
        time.sleep(1)
        logging.warn("load_production_firmware() - not implemented")
        pass
