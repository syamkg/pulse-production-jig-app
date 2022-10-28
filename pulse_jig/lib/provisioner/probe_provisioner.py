import enum
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import serial
from transitions import Machine

from pulse_jig.config import settings
from .common_states import CommonStates
from .provisioner import Provisioner
from ..hwspec import HWSpec
from ..jig_client import JigClientException, JigClient
from ..probe_spec import ProbeSpec

logger = logging.getLogger("provisioner")


class States(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    WAITING_FOR_SERIAL = enum.auto()
    WAITING_FOR_PCB = enum.auto()
    LOADING_TEST_FIRMWARE = enum.auto()
    WAITING_FOR_TARGET = enum.auto()
    WAITING_FOR_NETWORK = enum.auto()
    LOADING_DEVICE_REGO = enum.auto()
    GENERATE_HWSPEC = enum.auto()
    REGISTERING_DEVICE = enum.auto()
    SAVE_HWSPEC = enum.auto()
    RUNNING_TESTS = enum.auto()
    SUBMITTING_PROVISIONING_RECORD = enum.auto()
    UPDATE_QRCODE = enum.auto()
    WAITING_FOR_TARGET_REMOVAL = enum.auto()


class ProbeProvisioner(Provisioner, CommonStates):
    @dataclass
    class QRCode(Provisioner.QRCode):
        len: str

        def __str__(self):
            """
            DO NOT CHANGE THIS STRUCTURE OR ORDER!!!
            Laser engraver relies on this exact order
            """
            return (
                f"{self.sn}\n"
                f"{self.rev}\n"
                f"{datetime.fromtimestamp(self.dom).strftime('%m/%y')}\n"
                f"{self.cert}\n"
                f"{self.len}"
            )

    @dataclass
    class Mode(Provisioner.Mode):
        cable_length: float = 0

    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar)
        self._init_state_machine()
        self._pulse_manager = pulse_manager
        self._port = serial.Serial(baudrate=115200)
        self._port.port = dev
        self._test_firmware_path = settings.app.test_firmware_path
        self.mode = self.Mode()

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
        m.add_transition("proceed", States.WAITING_FOR_TARGET, States.LOADING_DEVICE_REGO, conditions="has_network")
        m.add_transition("proceed", States.LOADING_DEVICE_REGO, States.RUNNING_TESTS, conditions="has_hwspec")
        m.add_transition("proceed", States.RUNNING_TESTS, States.SUBMITTING_PROVISIONING_RECORD)
        m.add_transition(
            "proceed", States.SUBMITTING_PROVISIONING_RECORD, States.WAITING_FOR_TARGET_REMOVAL, before="update_qrcode"
        )
        m.add_transition("proceed", States.WAITING_FOR_TARGET_REMOVAL, States.WAITING_FOR_TARGET)

        # Wait for network if API is unreachable
        m.add_transition("proceed", States.WAITING_FOR_TARGET, States.WAITING_FOR_NETWORK, unless="has_network")
        m.add_transition("proceed", States.WAITING_FOR_NETWORK, States.WAITING_FOR_TARGET, conditions="has_network")

        # Register device if it doesn't have a hwspec
        m.add_transition("proceed", States.LOADING_DEVICE_REGO, States.GENERATE_HWSPEC, unless="has_hwspec")
        m.add_transition("proceed", States.GENERATE_HWSPEC, States.REGISTERING_DEVICE, conditions="has_hwspec")
        m.add_transition("proceed", States.REGISTERING_DEVICE, States.SAVE_HWSPEC)
        m.add_transition("proceed", States.SAVE_HWSPEC, States.RUNNING_TESTS)

        # On retry set state to RETRY and wait for the device to be removed
        m.add_transition("retry", "*", States.WAITING_FOR_TARGET_REMOVAL, before="set_status_retry")

        # On failure set state to FAILED and submit results if there is hwspec, else prompt to remove target
        m.add_transition(
            "fail", "*", States.SUBMITTING_PROVISIONING_RECORD, before="set_status_fail", conditions="has_hwspec"
        )
        m.add_transition("fail", "*", States.WAITING_FOR_TARGET_REMOVAL, before="set_status_fail", unless="has_hwspec")

        # Start from the beginning if the xDot or PCB or Probe lost
        m.add_transition("device_lost", "*", States.WAITING_FOR_SERIAL)

        m.on_enter_WAITING_FOR_TARGET("set_status_waiting")
        m.on_enter_WAITING_FOR_TARGET("start_iteration")
        m.on_enter_WAITING_FOR_TARGET("reset_logs")
        m.on_enter_LOADING_DEVICE_REGO("set_status_inprogress")
        m.on_enter_WAITING_FOR_TARGET_REMOVAL("promote_provision_status")
        m.on_exit_WAITING_FOR_TARGET_REMOVAL("reset")

    def run(self):
        while self.is_running():
            try:
                self._inner_loop()
            except Exception as e:
                logger.error(str(e))
                self.device_lost()

        logger.info("probe_provisioner provisioning thread terminated")

    def waiting_for_pcb(self):
        while not self._pulse_manager.is_connected:
            pass

        # Now if the pulse board is removed we will close
        # the port. This way pretty much any action will
        # fail with a serial error which will get caught
        # by the main loop.
        #
        # We can't just raise an exception here because
        # it won't get caught due to threading issues
        def handler():
            self._port.close()

        self._pulse_manager.on_removal(handler)
        self.proceed()

    def waiting_for_target(self):
        port_no = self._ftf.probe_await_connect()
        if port_no is None:
            logger.error("INVALID PROBE DETECTED!")
            self.fail()
            return
        self._port_no = port_no
        self.proceed()

    def loading_device_rego(self):
        try:
            self._ftf.enable_external_port(self._port_no)

            # If repair_mode is set we'll clear the hwspec on probe
            # before attempting to read. This will ensure to re-write
            # the hwspec to the device
            if settings.app.hwspec_repair_mode:
                self._ftf.hwspec_destroy("probe")

            if self._ftf.hwspec_load("probe"):
                self.hwspec = HWSpec()
                self.hwspec.get(self._ftf)
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

    def waiting_for_target_removal(self):
        self._ftf.probe_await_recovery()
        self.proceed()

    def generate_hwspec(self):
        self.hwspec = HWSpec()
        self.hwspec.set(self.mode.iecex_cert)

        # We'll set the probe_spec at the same time as hwspec
        self.probe_spec = ProbeSpec()
        self.probe_spec.set(self.mode.cable_length)
        self.proceed()

    def save_hwspec(self):
        self.hwspec.save(self._ftf)
        self._ftf.enable_external_port(self._port_no)

        # If saving to hwspec failed, it's fair to assume
        # the probe is write-protected
        try:
            self._ftf.hwspec_save("probe")
        except JigClient.CommandFailed:
            self.fail()
            return

        # Need to write probe spec only after `hwspec-save`
        # and attempt to verify the written probe spec
        self.probe_spec.save(self._ftf)
        success = self._ftf.hwchunk_verify("probe")

        self._ftf.disable_external_port()

        if not success:
            self.fail()
            return

        self.proceed()

    def update_qrcode(self):
        if self.has_passed():
            self.probe_spec = ProbeSpec()
            self.qrcode = self.QRCode(
                sn=self.hwspec.serial,
                rev=self.hwspec.hw_revision,
                dom=self.hwspec.assembly_timestamp,
                cert=self.hwspec.iecex_cert,
                len=f"{self.probe_spec_cable_length_m}m",
            )

    def registering_device(self):
        registered = self._registrar.register_serial(self.hwspec, cable_length=self.probe_spec.cable_length)
        if registered:
            self.proceed()
        else:
            self.retry()

    def submitting_provisioning_record(self):
        success = self._registrar.submit_provisioning_record(
            hwspec=self.hwspec,
            status=self.provisional_status.name,
            logs=self._ftf.log,
            test_firmware_version=self.test_firmware_version,
        )
        if success:
            self.proceed()
        else:
            self.retry()

    def reset(self):
        super().reset()
        self.probe_spec: Optional[ProbeSpec] = None

    @property
    def probe_spec_cable_length_m(self) -> float:
        """Reads cable length from hwspec & returns in meters
        If the cable length was not found Fail with ValueError
        """
        try:
            self._ftf.enable_external_port(self._port_no)
            self.probe_spec.get(self._ftf)
            self._ftf.disable_external_port()
            return self.probe_spec.cable_length / 1000
        except IndexError:
            raise ValueError("Cable length not found!")

    def start_iteration(self):
        # Before starting an iteration we need to power cycle the Pulse.
        # This will ensure the Pulse is fresh & have no tasks
        # running / locked by the last iteration.
        self._pulse_manager.reset_device()
        self._ftf.skip_boot_header()
