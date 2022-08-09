import enum
import logging
from random import randrange
from typing import Optional

import serial
from transitions import Machine

from pulse_jig.config import settings
from .common_states import CommonStates
from .provisioner import Provisioner
from ..hwspec import HWSpec
from ..jig_client import JigClientException, JigClient

logger = logging.getLogger("provisioner")


class States(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    WAITING_FOR_SERIAL = enum.auto()
    WAITING_FOR_PCB = enum.auto()
    LOADING_TEST_FIRMWARE = enum.auto()
    WAITING_FOR_NETWORK = enum.auto()
    LOADING_DEVICE_REGO = enum.auto()
    GENERATE_HWSPEC = enum.auto()
    REGISTERING_DEVICE = enum.auto()
    SAVE_HWSPEC = enum.auto()
    RUNNING_TESTS = enum.auto()
    CONFIGURING_DEVICE = enum.auto()
    SUBMITTING_PROVISIONING_RECORD = enum.auto()
    LOADING_PROD_FIRMWARE = enum.auto()
    UPDATE_QRCODE = enum.auto()
    WAITING_FOR_PCB_REMOVAL = enum.auto()


class PulseProvisioner(Provisioner, CommonStates):
    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar)
        self._init_state_machine()
        self._pulse_manager = pulse_manager
        self._port = serial.Serial(baudrate=115200)
        self._port.port = dev
        self._test_firmware_path = settings.app.test_firmware_path
        self._prod_firmware_path = settings.app.prod_firmware_path
        self.mode = self.Mode()

    def _init_state_machine(self):
        m = Machine(
            model=self,
            states=States,
            initial=States.WAITING_FOR_SERIAL,
        )

        # Expected working path
        m.add_transition("proceed", States.WAITING_FOR_SERIAL, States.WAITING_FOR_PCB)
        m.add_transition("proceed", States.WAITING_FOR_PCB, States.LOADING_TEST_FIRMWARE, before="reset")
        m.add_transition("proceed", States.LOADING_TEST_FIRMWARE, States.LOADING_DEVICE_REGO, conditions="has_network")
        m.add_transition("proceed", States.LOADING_DEVICE_REGO, States.RUNNING_TESTS, conditions="has_hwspec")
        m.add_transition("proceed", States.RUNNING_TESTS, States.LOADING_PROD_FIRMWARE, conditions="has_passed")
        m.add_transition("proceed", States.LOADING_PROD_FIRMWARE, States.SUBMITTING_PROVISIONING_RECORD)
        m.add_transition(
            "proceed", States.SUBMITTING_PROVISIONING_RECORD, States.WAITING_FOR_PCB_REMOVAL, before="update_qrcode"
        )
        m.add_transition("proceed", States.WAITING_FOR_PCB_REMOVAL, States.WAITING_FOR_SERIAL)

        # Submit provision record if tests fail
        m.add_transition("proceed", States.RUNNING_TESTS, States.SUBMITTING_PROVISIONING_RECORD, unless="has_passed")

        # Wait for network if API is unreachable
        m.add_transition("proceed", States.WAITING_FOR_PCB, States.WAITING_FOR_NETWORK, unless="has_network")
        m.add_transition("proceed", States.WAITING_FOR_NETWORK, States.WAITING_FOR_PCB, conditions="has_network")

        # Register device if it doesn't have a hwspec
        m.add_transition("proceed", States.LOADING_DEVICE_REGO, States.GENERATE_HWSPEC, unless="has_hwspec")
        m.add_transition("proceed", States.GENERATE_HWSPEC, States.CONFIGURING_DEVICE, conditions="has_hwspec")
        m.add_transition("proceed", States.CONFIGURING_DEVICE, States.REGISTERING_DEVICE)
        m.add_transition("proceed", States.REGISTERING_DEVICE, States.SAVE_HWSPEC)
        m.add_transition("proceed", States.SAVE_HWSPEC, States.RUNNING_TESTS)

        # On retry set state to RETRY and wait for the device to be removed
        m.add_transition("retry", "*", States.WAITING_FOR_PCB_REMOVAL, before="set_status_retry")

        # On failure set state to FAILED and submit results if there is hwspec, else prompt to remove target
        m.add_transition(
            "fail", "*", States.SUBMITTING_PROVISIONING_RECORD, before="set_status_fail", conditions="has_hwspec"
        )
        m.add_transition("fail", "*", States.WAITING_FOR_PCB_REMOVAL, before="set_status_fail", unless="has_hwspec")

        # Start from the beginning if the xDot or PCB lost
        m.add_transition("device_lost", "*", States.WAITING_FOR_SERIAL)

        m.on_enter_WAITING_FOR_PCB("set_status_waiting")
        m.on_enter_LOADING_DEVICE_REGO("set_status_inprogress")
        m.on_enter_WAITING_FOR_PCB_REMOVAL("promote_provision_status")
        m.on_exit_WAITING_FOR_PCB_REMOVAL("reset")

    def run(self):
        while True:
            try:
                self._inner_loop()
            except Exception as e:
                logger.error(str(e))
                self.device_lost()

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

    def loading_prod_firmware(self):
        if not settings.app.skip_firmware_load:
            self._pulse_manager.load_firmware(self._prod_firmware_path)

        self._pf = JigClient(self._port)
        self._pulse_manager.reset_device()
        header = self._pf.read_boot_header()

        if not validate_prod_firmware_load(header):
            logger.error("Failed to load the Production firmware")
            self.retry()
            return

        self.prod_firmware_version = get_prod_firmware_version(header)
        self.proceed()

    def loading_device_rego(self):
        try:
            self._ftf.platform("prp-enable")

            # If repair_mode is set we'll clear the hwspec on probe
            # before attempting to read. This will ensure to re-write
            # the hwspec to the device
            if settings.app.hwspec_repair_mode:
                self._ftf.hwspec_destroy("pulse")

            if self._ftf.hwspec_load("pulse"):
                self.hwspec = HWSpec()
                self.hwspec.get(self._ftf)
            else:
                self.hwspec = None

            self._ftf.platform("prp-disable")
            self.proceed()
        except JigClientException as e:
            # If an JigClientException occurred then it could be the pulse
            # is not connected properly or jig can't read from the serial.
            # We'll ask to "retry" in this case.
            logger.error(str(e))
            self.retry()

    def running_tests(self):
        passed = self._ftf.test_self()

        if passed:
            passed = self._ftf.test_port()

        if passed:
            passed = self._ftf.test_lora_connect(
                settings.lora.test.sub_band, settings.lora.test.join_eui, settings.lora.test.app_key
            )

        if passed:
            logger.info("Tests Passed!")
            self.set_status_passed()
            self.proceed()
        else:
            logger.error("Tests Failed!")
            self.fail()

    def waiting_for_pcb_removal(self):
        self._pulse_manager.await_removal()
        self.proceed()

    def configuring_device(self):
        # Configure Pulse
        self._ftf.pulse_cfg_init()
        self._ftf.pulse_cfg_load()
        self._ftf.pulse_cfg_set_pulse("polling_rate", 1800)
        self._ftf.pulse_cfg_save()

        # Configure LoRa
        self._ftf.lora_config(settings.lora.config.join_eui, self.config_app_key)

        self.proceed()

    def generate_hwspec(self):
        self.hwspec = HWSpec()
        self.hwspec.set()
        self.proceed()

    def save_hwspec(self):
        self.hwspec.save(self._ftf)
        self._ftf.platform("prp-enable")
        self._ftf.hwspec_save("pulse")
        self._ftf.platform("prp-disable")
        self.proceed()

    def update_qrcode(self):
        if self.has_passed():
            self.qrcode = self.QRCode(
                sn=self.hwspec.serial,
                rev=self.hwspec.hw_revision,
                dom=self.hwspec.assembly_timestamp,
                cert=self.hwspec.iecex_cert,
            )

    def registering_device(self):
        dev_eui = self._ftf.lora_deveui()
        registered = self._registrar.register_serial(
            self.hwspec,
            dev_eui=dev_eui,
            join_eui=settings.lora.config.join_eui,
            app_key=self.config_app_key,
        )
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
            prod_firmware_version=self.prod_firmware_version,
        )
        if success:
            self.proceed()
        else:
            self.retry()

    def reset(self):
        super().reset()
        self.reset_gui_logs: bool = True
        self.prod_firmware_version: Optional[str] = "0.0.0"
        self.config_app_key = generate_app_key()


def generate_app_key():
    groups = 16  # How many groups
    group_size = 2  # Number of hex digits' in each group
    length = groups * group_size

    app_key = ""

    for i in range(length):
        if (i != 0) & (i % 2 == 0):
            app_key += ":"
        app_key += f"{randrange(16):x}"

    return app_key


def validate_prod_firmware_load(header: str) -> bool:
    return "Starting Production Firmware" in header


def get_prod_firmware_version(header: str) -> str:
    version = ""
    for ln in header.splitlines(True):
        if ln.startswith("Firmware Version:"):
            version = ln[17:].strip()  # Strip - "Firmware Version:"
    return version
