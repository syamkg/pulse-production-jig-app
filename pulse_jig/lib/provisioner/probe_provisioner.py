import enum
import serial
import os
from transitions import Machine
from .provisioner import Provisioner
from .common_states import CommonStates
from ..jig_client import JigClient, JigClientException
from ..hwspec import HWSpec


class States(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    WAITING_FOR_SERIAL = enum.auto()
    WAITING_FOR_PCB = enum.auto()
    LOADING_TEST_FIRMWARE = enum.auto()
    WAITING_FOR_TARGET = enum.auto()
    LOADING_DEVICE_REGO = enum.auto()
    REGISTERING_DEVICE = enum.auto()
    RUNNING_TESTS = enum.auto()
    SUBMITTING_PROVISIONING_RECORD = enum.auto()
    LOADING_PROD_FIRMWARE = enum.auto()
    WAITING_FOR_TARGET_REMOVAL = enum.auto()


class ProbeProvisioner(Provisioner, CommonStates):
    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar)
        self._init_state_machine()
        self._pulse_manager = pulse_manager
        self._port = serial.Serial(baudrate=115200)
        self._port.port = dev
        self._test_firmware_path = "../firmware/test-firmware.bin"

    def _init_state_machine(self):
        m = Machine(
            model=self,
            states=States,
            initial=States.WAITING_FOR_SERIAL,
        )

        # Expected working path
        m.add_transition("proceed", States.WAITING_FOR_SERIAL, States.WAITING_FOR_PCB)
        m.add_transition("proceed", States.WAITING_FOR_PCB, States.LOADING_TEST_FIRMWARE)
        m.add_transition("proceed", States.LOADING_TEST_FIRMWARE, States.WAITING_FOR_TARGET)
        m.add_transition("proceed", States.WAITING_FOR_TARGET, States.LOADING_DEVICE_REGO)
        m.add_transition("proceed", States.LOADING_DEVICE_REGO, States.RUNNING_TESTS, conditions="has_hwspec")
        m.add_transition("proceed", States.RUNNING_TESTS, States.SUBMITTING_PROVISIONING_RECORD)
        m.add_transition("proceed", States.SUBMITTING_PROVISIONING_RECORD, States.WAITING_FOR_TARGET_REMOVAL)
        m.add_transition("proceed", States.WAITING_FOR_TARGET_REMOVAL, States.WAITING_FOR_TARGET)

        # Register device if it doesn't have a hwspec
        m.add_transition("proceed", States.LOADING_DEVICE_REGO, States.REGISTERING_DEVICE, unless="has_hwspec")
        m.add_transition("proceed", States.REGISTERING_DEVICE, States.RUNNING_TESTS)

        # Load the production firmware if the device passed the tests
        m.add_transition("proceed", States.RUNNING_TESTS, States.LOADING_PROD_FIRMWARE, conditions="has_passed")
        m.add_transition("proceed", States.LOADING_PROD_FIRMWARE, States.WAITING_FOR_TARGET_REMOVAL)

        # On retry set state to RETRY and wait for the device to be removed
        m.add_transition("retry", "*", States.WAITING_FOR_TARGET_REMOVAL, before="set_status_retry")

        # On failure set state to FAILED and submit results
        m.add_transition("fail", "*", States.SUBMITTING_PROVISIONING_RECORD, before="set_status_fail")

        # Handle bad probes being detected while waiting for a target
        m.add_transition("bad_probe", States.WAITING_FOR_TARGET, States.WAITING_FOR_TARGET_REMOVAL)

        # Some error conditions
        m.add_transition("serial_lost", "*", States.WAITING_FOR_SERIAL)
        m.add_transition("pcb_lost", "*", States.WAITING_FOR_SERIAL)
        m.add_transition("target_lost", "*", States.WAITING_FOR_TARGET)

        m.on_exit_WAITING_FOR_TARGET("reset")
        m.on_enter_WAITING_FOR_TARGET("set_status_waiting")
        m.on_enter_LOADING_DEVICE_REGO("set_status_inprogress")
        m.on_enter_WAITING_FOR_TARGET_REMOVAL("promote_provision_status")

    def waiting_for_pcb(self):
        while not self._pulse_manager.is_connected:
            pass

        # Now if the pulse board is removed we will close
        # the port. This way pretty much any action will
        # fail with a serial error which will get caught
        # by the main loop.
        #
        # We can't just raise an exception here because
        # it wont get caught due to threading issues
        # i expect
        def handler():
            self._port.close()

        self._pulse_manager.on_removal(handler)

        self.proceed()

    def loading_test_firmware(self):
        if os.getenv("SKIP_TEST_FIRMWARE_LOAD") != "1":
            self._pulse_manager.load_firmware(self._test_firmware_path)
        self._ftf = JigClient(self._port)
        self._pulse_manager.reset_device()
        self._ftf.skip_boot_header()
        self.proceed()

    def waiting_for_target(self):
        port_no = self._ftf.probe_await_connect()
        if port_no is None:
            self.bad_probe()
        self._port_no = port_no
        self.proceed()

    def run(self):
        while True:
            try:
                self._inner_loop()
            except Exception as e:
                print(f"BOOM: {e}")
                print(type(e))
                self.pcb_lost()

    def loading_device_rego(self):
        try:
            self._ftf.enable_external_port(self._port_no)
        except JigClientException:
            # If a JigClientException occurred here then it
            # shouldn't be the probe because it is isoated
            # from the system until after this command.
            # Going to assume this means the pulse was
            # unplugged.
            self.pcb_lost()

        try:
            if self._ftf.hwspec_load("probe"):
                self.hwspec = HWSpec(serial=self._ftf.hwspec_get("serial"))
            else:
                self.hwspec = None
            self._ftf.disable_external_port()
            self.proceed()
        except JigClientException:
            # If an JigClientException occurred then it could be a problem
            # probe because errors with its I2C bus (ie shorted) will lock
            # up the whole bus. It could also be a problem with the pulse
            # (unlikely - we don't expect working pulses to just die) or
            # the functional test firmware (should have been caught in dev)
            self.fail()

    def running_tests(self):
        passed = self._ftf.test_ta3k(self._port_no)
        if passed:
            self.set_status_passed()
        else:
            self.set_status_failed()
        self.proceed()

    def waiting_for_target_removal(self):
        self._ftf.probe_await_recovery()
        self.proceed()
