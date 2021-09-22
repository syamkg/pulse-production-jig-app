#!/usr/bin/env python3
import logging
import time
import serial
from transitions import Machine
import re
import gpiozero
from pulse_jig.functional_test import FunctionalTest, FunctionalTestFailure
import textwrap


class JigTester:
    def __init__(self, dev):
        self.port = serial.Serial()
        self.port.port = dev
        self.port.baudrate = 115200
        self.listeners = []
        self.pcb_sense_gpio = gpiozero.Button(5, pull_up=True)

        self.machine = Machine(
            model=self,
            states=[
                "stopped",
                "waiting_for_serial",
                "waiting_for_pcb",
                "waiting_for_pcb_removal",
                "running_test",
            ],
            initial="stopped",
        )

        self.machine.add_transition(
            "start",
            "stopped",
            "waiting_for_serial",
        )

        self.machine.add_transition("stop", "*", "stopped")

        self.machine.add_transition(
            "serial_lost", "*", "waiting_for_serial", before="_close_port"
        )

        self.machine.add_transition(
            "serial_found",
            "waiting_for_serial",
            "waiting_for_pcb",
        )

        self.machine.add_transition(
            "pcb_connected",
            "waiting_for_pcb",
            "running_test",
        )

        self.machine.add_transition(
            "test_passed",
            "running_test",
            "waiting_for_pcb_removal",
            before="_handle_test_passed",
        )

        self.machine.add_transition(
            "test_failed",
            "running_test",
            "waiting_for_pcb_removal",
            before="_handle_test_failed",
        )

        self.machine.add_transition(
            "serial_detected",
            "waiting_for_pcb",
            "waiting_for_pcb",
            after="_handle_serial_detected",
        )

        self.machine.add_transition(
            "pcb_removed", "waiting_for_pcb_removal", "waiting_for_pcb"
        )

    def _handle_test_passed(self, serial_no: str, log: str):
        logging.info(f"_handled_test_passed({serial_no})\n{textwrap.indent(log, '+ ')}")
        self._send_event("test_passed", dict(serial_no=serial_no))

    def _handle_test_failed(self, msg, *, log=None, serial_no=None):
        logging.info(
            f"_handled_test_failed({msg}, {serial_no})\n{textwrap.indent(log, '+ ')}"
        )
        self._send_event("test_failed", dict(msg=msg, serial_no=serial_no, log=log))

    def _handle_serial_detected(self, serial_no):
        self._send_event("serial_detected", dict(serial_no=serial_no))

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

        while self.state != "stopped" and self.state != "test_failed":
            self._send_event(self.state)
            fn = getattr(self, self.state, fn_not_found)
            if fn:
                logging.info(f"{self.state}()")
                fn()

    def waiting_for_serial(self):
        while True:
            try:
                self.port.open()
                self.serial_found()
                return
            except serial.serialutil.SerialException:
                time.sleep(1)

    def waiting_for_pcb(self):
        while True:
            try:
                if self._is_pcb_connected():
                    self.pcb_connected()
                    return
                else:
                    serial = self._check_for_serial()
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
        test = FunctionalTest(self.port)
        try:
            serial_no, log = test.run()
            self.test_passed(serial_no, log)
        except serial.serialutil.SerialException as err:
            self.serial_lost(str(err))
        except FunctionalTestFailure as err:
            self.test_failed(err.msg, serial_no=err.serial_no, log=err.log)

    def waiting_for_pcb_removal(self):
        self.pcb_sense_gpio.wait_for_release()
        self._send_event("pcb_removed")
        self.pcb_removed()

    def _check_for_serial(self, timeout=0):
        resp = ""
        end_time = time.monotonic() + timeout
        while timeout == 0 or end_time > time.monotonic():
            while self.port.in_waiting > 0:
                resp += self.port.read(self.port.in_waiting).decode("utf-8")
            matches = re.search(r"^Serial: (.*)$", resp, re.MULTILINE)
            if matches:
                return matches.group(1).strip()
            if timeout == 0:
                break
        return None

    def _is_pcb_connected(self):
        return self.pcb_sense_gpio.is_pressed
