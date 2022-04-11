import time
import enum
from provisioner import Provisioner
from transitions import Machine
import sys


def bg_input(prompt):
    sys.stdout.write(prompt + "\n")
    return sys.stdin.readline().strip()


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


class FakeProvisioner(Provisioner):
    def __init__(self, registrar):
        super().__init__(registrar)

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

        # Some error conditions
        m.add_transition("serial_lost", "*", States.WAITING_FOR_SERIAL)
        m.add_transition("pcb_lost", "*", States.WAITING_FOR_PCB)
        m.add_transition("target_lost", "*", States.WAITING_FOR_TARGET)

        m.on_exit_WAITING_FOR_TARGET("reset")
        m.on_enter_WAITING_FOR_TARGET("set_status_waiting")
        m.on_enter_LOADING_DEVICE_REGO("set_status_inprogress")
        m.on_enter_WAITING_FOR_TARGET_REMOVAL("promote_provision_status")

    def waiting_for_target(self):
        bg_input("press ENTER to insert target")
        self.proceed()

    def loading_device_rego(self):
        inp = bg_input("has hwspec? [y: yes, n: no]")
        print(f"input: {inp}")
        if inp == "y":
            self.hwspec = Provisioner.HWSpec(serial="W0-123-456789")
        else:
            self.hwspec = None
        self.proceed()

    def running_tests(self):
        if bg_input("Tests passed? [y: yes, n: no]") == "y":
            self.set_status_passed()
        else:
            self.set_status_failed()
        self.proceed()

    def waiting_for_target_removal(self):
        bg_input("press ENTER to remove target")
        self.proceed()

    def waiting_for_serial(self):
        time.sleep(0.4)
        self.proceed()

    def waiting_for_pcb(self):
        time.sleep(0.4)
        self.proceed()

    def loading_test_firmware(self):
        time.sleep(0.4)
        self.proceed()

    def registering_device(self):
        resp = bg_input("registration status? [p:pass, f:fail registration, w: fail write hwspec]:")
        if resp == "w":
            self.fail()
        elif resp == "f":
            self.retry()
        else:
            serial = "W0-234-12345678"
            self._registrar.register_serial(serial)
            self.hwspec = Provisioner.HWSpec(serial=serial)
            self.proceed()

    def submitting_provisioning_record(self):
        if bg_input("submitted? [y: yes, n: no]") == "y":
            self._registrar.submit_provisioning_record(self.provisional_status, self.hwspec, self.logs)
            self.proceed()
        else:
            self.retry()
