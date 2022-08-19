import enum
import logging
from typing import Optional

from transitions import Machine

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
    RUNNING_TESTS = enum.auto()
    SUBMITTING_PROVISIONING_RECORD = enum.auto()
    LOADING_PROD_FIRMWARE = enum.auto()
    UPDATE_QRCODE = enum.auto()
    WAITING_FOR_PCB_REMOVAL = enum.auto()


class PulseProvisionerPhase2(PulseProvisioner, CommonStates):
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

    def waiting_for_pcb(self):
        while not self._pulse_manager.check_for_header(self._port) and not self._pulse_manager.is_connected:
            pass
        self.proceed()

    def loading_device_rego(self):
        try:
            self._ftf.platform("prp-enable")

            if self._ftf.hwspec_load("pulse"):
                self.hwspec = HWSpec()
                self.hwspec.get(self._ftf)
            else:
                self.fail()
                return

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
            logger.info("Tests Passed!")
            self.set_status_passed()
            self.proceed()
        else:
            logger.error("Tests Failed!")
            self.fail()

    def reset(self):
        super().reset()
        self.prod_firmware_version: Optional[str] = "0.0.0"
        self.dev_eui: Optional[str] = None