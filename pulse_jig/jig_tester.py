#!/usr/bin/env python3
import logging
import time
import textwrap
from typing import Callable, Dict, Optional
from enum import Enum
import serial
import gpiozero
from transitions import Machine
import requests
from pulse_jig.device_provisioner import DeviceProvisioner, DeviceProvisioningFailure
from pulse_jig.check_for_serial import check_for_serial


class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class JigTester:
    def __init__(
        self,
        dev: str,
        registrar_url: str,
        pcb_sense_gpio_pin: int = 5,
        reset_gpio_pin: int = 21,
    ):
        """Jig Tester loop. When run it will wait for a device to be plugged in,
        provision a serial, test the device, and save the results to the cloud
        before looping to do it all over again.

        :param dev: The path to the XDOT Programmer serial port. eg.
                    macos: /dev/cu.usbmodem11202
                    linux: /dev/ttyACM1
        """

        self._port = serial.Serial()
        self._port.port = dev
        self._port.baudrate = 115200
        self._listeners = []
        self._pcb_sense_gpio = gpiozero.Button(pcb_sense_gpio_pin, pull_up=True)
        self._registrar_url = registrar_url
        self._device_provisioner = DeviceProvisioner(reset_gpio_pin=reset_gpio_pin)

        self.machine = Machine(
            model=self,
            states=[
                "stopped",
                "waiting_for_serial",
                "waiting_for_pcb",
                "provisioning",
                "waiting_for_pcb_removal",
            ],
            initial="stopped",
        )

        self.machine.add_transition(
            "start",
            "stopped",
            "waiting_for_serial",
        )

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
            "provisioning",
        )

        self.machine.add_transition(
            "provisioning_successful",
            "provisioning",
            "waiting_for_pcb_removal",
            before="_handle_provisioning_successful",
        )

        self.machine.add_transition(
            "provisioning_failed",
            "provisioning",
            "waiting_for_pcb_removal",
            before="_handle_provisioning_failed",
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

    def _handle_provisioning_successful(self, serial_no: str, log: str):
        logging.info(
            f"_handled_provisioning_successful({serial_no})\n{textwrap.indent(log, '+ ')}"
        )
        self._send_event("provisioning_successful", dict(serial_no=serial_no))

    def _handle_provisioning_failed(
        self, msg: str, *, log: str = None, serial_no: str = None
    ):
        logging.info(
            f"_handled_provisioning_failed({msg}, {serial_no})\n{textwrap.indent(log, '+ ')}"
        )
        self._send_event(
            "provisioning_failed", dict(msg=msg, serial_no=serial_no, log=log)
        )

    def _handle_serial_detected(self, serial_no: str):
        self._send_event("serial_detected", dict(serial_no=serial_no))

    def _close_port(self):
        self._port.close()

    def _send_event(self, event: str, data: Dict = {}):
        for listener in self._listeners:
            listener(event, data)

    def add_listener(self, listener: Callable[[str, Dict], None]):
        """Add a listener function that will be called on any events.

        :param listener: The function that will be called on an event.
        """
        self._listeners.append(listener)

    def run(self):
        """Runs the event loop. This function will never return and will
        loop forever."""
        self.start()

        def fn_not_found():
            raise RuntimeError("Could not find state handler: ")

        while True:
            self._send_event(self.state)
            fn = getattr(self, self.state, fn_not_found)
            if fn:
                logging.info(f"{self.state}()")
                fn()

    def waiting_for_serial(self):
        """Blocks until the serial port is detected. When found it will
        result in a `serial_found` transition."""
        while True:
            try:
                self._port.open()
                self.serial_found()
                return
            except serial.serialutil.SerialException:
                time.sleep(1)

    def waiting_for_pcb(self):
        """Waits for a pcb to be connected (detected via the pcb sense pin)
        while monitoring the UART for a device serial number output in a
        production firmware boot message.

        This method will block until one of the conditions is detected. It
        may be terminated with one of the following transitions:
        * serial_detected
        * pcb_connected
        * serial_local
        """

        while True:
            try:
                if self._is_pcb_connected():
                    self.pcb_connected()
                    return
                else:
                    serial = check_for_serial(self._port)
                    if serial:
                        self.serial_detected(serial)
                        return
                    time.sleep(1)
            except OSError as err:
                # These OSErrors will be thrown if the serial port disappears. This
                # handling could be improved
                # 6 on macos
                # 5 on pi
                if err.errno == 6 or err.errno == 5:
                    self.serial_lost()
                    return
                else:
                    raise err

    def provisioning(self) -> bool:
        """Tests and provisions the device. The state will
        terminate with one of the following transitions:
        * provisioning_successful
        * provisioning_failed
        * serial_lost
        """
        try:
            serial_no, log = self._device_provisioner.run(self._port)

            if not self._record_results(
                TestStatus.PASS, serial_no=serial_no, test_logs=log
            ):
                self.provisioning_failed(
                    "Failed to record results", serial_no=serial_no, log=log
                )
            else:
                self.provisioning_successful(serial_no, log)

        except serial.serialutil.SerialException as err:
            self.serial_lost(str(err))
        except DeviceProvisioningFailure as err:
            if err.serial_no is not None:
                self._record_results(
                    TestStatus.FAIL,
                    serial_no=err.serial_no,
                    test_logs=err.log,
                    failure_reason=err.msg,
                )
            self.provisioning_failed(err.msg, serial_no=err.serial_no, log=err.log)

    def waiting_for_pcb_removal(self):
        """Blocks until the pcb is removed (detected via the pcb sense pin).
        The function will terminate with the `pcb_removed` transition."""
        self._pcb_sense_gpio.wait_for_release()
        self._send_event("pcb_removed")
        self.pcb_removed()

    def _is_pcb_connected(self):
        return self._pcb_sense_gpio.is_pressed

    def _record_results(
        self,
        test_status: TestStatus,
        *,
        serial_no: str,
        test_logs: Optional[str],
        failure_reason: Optional[str] = None,
    ):
        # TODO: Auth requests - tbc: IAM auth on the gateway and allow the device's role, sign with requests_aws4auth
        r = requests.post(
            f"{self._registrar_url}/device",
            json=dict(
                testStatus=str(test_status),
                testLogs=test_logs,
                failureReason=failure_reason,
            ),
        )
        if r.status_code != requests.codes.ok:
            logging.error(
                f"Failed to record results ({serial_no}, {test_status}): {r.text}"
            )
            return False
        return True
