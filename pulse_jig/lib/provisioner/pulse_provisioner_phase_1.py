import enum
import logging
from random import randrange
from typing import Optional

from transitions import Machine

from pulse_jig.config import settings
from .common_states import CommonStates
from .pulse_provisioner import PulseProvisioner
from ..hwspec import HWSpec
from ..jig_client import JigClientException

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
    UPDATE_QRCODE = enum.auto()
    WAITING_FOR_PCB_REMOVAL = enum.auto()


class PulseProvisionerPhase1(PulseProvisioner, CommonStates):
    def _init_state_machine(self):
        m = Machine(
            model=self,
            states=States,
            initial=States.WAITING_FOR_SERIAL,
        )

        # Expected working path
        m.add_transition("proceed", States.WAITING_FOR_SERIAL, States.WAITING_FOR_PCB)
        m.add_transition("proceed", States.WAITING_FOR_PCB, States.LOADING_TEST_FIRMWARE)
        m.add_transition("proceed", States.LOADING_TEST_FIRMWARE, States.LOADING_DEVICE_REGO, conditions="has_network")
        m.add_transition("proceed", States.LOADING_DEVICE_REGO, States.RUNNING_TESTS, conditions="has_hwspec")
        m.add_transition("proceed", States.RUNNING_TESTS, States.SUBMITTING_PROVISIONING_RECORD)
        m.add_transition(
            "proceed", States.SUBMITTING_PROVISIONING_RECORD, States.WAITING_FOR_PCB_REMOVAL, before="update_qrcode"
        )
        m.add_transition("proceed", States.WAITING_FOR_PCB_REMOVAL, States.WAITING_FOR_SERIAL)

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
        m.on_enter_WAITING_FOR_PCB("start_iteration")
        m.on_enter_LOADING_TEST_FIRMWARE("set_status_inprogress")
        m.on_enter_WAITING_FOR_PCB_REMOVAL("promote_provision_status")
        m.on_exit_WAITING_FOR_PCB_REMOVAL("reset")
        m.on_exit_WAITING_FOR_PCB_REMOVAL("reset_logs")

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

            # Read & save dev_eui for future reference
            self.dev_eui = self._ftf.lora_deveui()

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
            logger.info("Tests Passed!")
            self.set_status_passed()
            self.proceed()
        else:
            logger.error("Tests Failed!")
            self.fail()

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

    def registering_device(self):
        registered = self._registrar.register_serial(
            self.hwspec,
            dev_eui=self.dev_eui,
            join_eui=settings.lora.config.join_eui,
            app_key=self.config_app_key,
        )
        if registered:
            self.proceed()
        else:
            self.retry()

    def reset(self):
        super().reset()
        self.prod_firmware_version: Optional[str] = "0.0.0"

    def start_iteration(self):
        # Before starting an iteration we need
        # to generate a new app key.
        self.config_app_key = generate_app_key()
        self.dev_eui: Optional[str] = None


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
