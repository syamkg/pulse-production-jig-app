import enum
import logging
from typing import Optional

from transitions import Machine

from pulse_jig.config import settings
from .common_states import CommonStates
from .pulse_provisioner import PulseProvisioner
from ..hwspec import HWSpec
from ..jig_client import JigClientException
from lib.target import Target

logger = logging.getLogger("provisioner")


class States(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    WAITING_FOR_SERIAL = enum.auto()
    WAITING_FOR_PCB = enum.auto()
    LOADING_TEST_FIRMWARE = enum.auto()
    WAITING_FOR_NETWORK = enum.auto()
    LOADING_DEVICE_REGO = enum.auto()
    SUBMITTING_PROVISIONING_RECORD = enum.auto()
    LOADING_PROD_FIRMWARE = enum.auto()


class PulseProvisionerPhase3(PulseProvisioner, CommonStates):
    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar, pulse_manager, dev)
        self.mode.target = Target.PULSE_PHASE_3

    def _init_state_machine(self):
        m = Machine(
            model=self,
            states=States,
            initial=States.WAITING_FOR_SERIAL,
        )

        # Expected working path
        m.add_transition("proceed", States.WAITING_FOR_SERIAL, States.WAITING_FOR_PCB)
        m.add_transition("proceed", States.WAITING_FOR_PCB, States.LOADING_TEST_FIRMWARE, conditions="has_network")
        m.add_transition("proceed", States.LOADING_TEST_FIRMWARE, States.LOADING_DEVICE_REGO)
        m.add_transition(
            "proceed",
            States.LOADING_DEVICE_REGO,
            States.LOADING_PROD_FIRMWARE,
            before="set_status_passed",
            conditions="has_hwspec",
        )
        m.add_transition("proceed", States.LOADING_PROD_FIRMWARE, States.SUBMITTING_PROVISIONING_RECORD)
        m.add_transition(
            "proceed", States.SUBMITTING_PROVISIONING_RECORD, States.WAITING_FOR_SERIAL, before="update_qrcode"
        )

        # Wait for network if API is unreachable
        m.add_transition("proceed", States.WAITING_FOR_PCB, States.WAITING_FOR_NETWORK, unless="has_network")
        m.add_transition("proceed", States.WAITING_FOR_NETWORK, States.WAITING_FOR_PCB, conditions="has_network")

        # On retry set state to RETRY and wait for the device to be removed
        m.add_transition("retry", "*", States.WAITING_FOR_SERIAL, before="set_status_retry")

        # On failure set state to FAILED if we can't read the hwspec (this is done implictly from loading_device_rego)
        m.add_transition("fail", "*", States.WAITING_FOR_SERIAL, before="set_status_fail")

        # Start from the beginning if the xDot or PCB lost
        m.add_transition("device_lost", "*", States.WAITING_FOR_SERIAL)

        m.on_exit_WAITING_FOR_PCB("reset")
        m.on_exit_WAITING_FOR_PCB("reset_logs")
        m.on_enter_LOADING_TEST_FIRMWARE("set_status_inprogress")
        m.on_enter_WAITING_FOR_PCB("promote_provision_status")

        # only allow 'reset' button during "PCB" wait
        m.on_enter_WAITING_FOR_PCB("pcb_reset_button_enable")
        m.on_exit_WAITING_FOR_PCB("pcb_reset_button_disable")

    def waiting_for_pcb(self):
        test = lambda: self.is_running()
        # check_for_header will block until we have a header or we've stopped running
        self._pulse_manager.check_for_header(self._port, continue_test=test)
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

    def reset(self):
        super().reset()
        self.prod_firmware_version: Optional[str] = "0.0.0"
        self.dev_eui: Optional[str] = None

    def submitting_provisioning_record(self):
        success = self._registrar.submit_provisioning_record(
            hwspec=self.hwspec,
            status=self.provisional_status.name,
            logs=self._ftf.log,
            test_firmware_version=self.test_firmware_version,
            prod_firmware_version=self.prod_firmware_version,
            region_ch_plan=self.mode.region_ch_plan,
        )
        if success:
            self.proceed()
        else:
            self.retry()

    def reset_device(self):
        # self._running = False
        self.state = States.LOADING_TEST_FIRMWARE
        self.set_status_inprogress()
        self.loading_test_firmware()
        if self.state == States.LOADING_DEVICE_REGO:
            self.loading_device_rego()
        else:
            self.reset_device()
