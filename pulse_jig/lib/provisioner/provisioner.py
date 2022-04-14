import enum
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from ..registrar import Registrar
from ..hwspec import HWSpec


class Provisioner:
    """
    Base class for providers. It contains the provisioning status, event system,
    and main loop of the workflow.
    """

    class Status(enum.Enum):
        """
        Workflow status.
        """

        UNKNOWN = enum.auto()
        INPROGRESS = enum.auto()
        PASSED = enum.auto()
        FAILED = enum.auto()
        RETRY = enum.auto()
        WAITING = enum.auto()

    @dataclass
    class EventData:
        hwspec: Optional[HWSpec]
        status: "Provisioner.Status"

    def __init__(self, registrar: Registrar):
        self.reset()
        self._registrar = registrar
        self._listeners: List[Callable] = []
        self.status = Provisioner.Status.UNKNOWN
        self.provisional_status = Provisioner.Status.UNKNOWN

    def _send_event(self, name: str):
        for listener in self._listeners:
            listener(name, Provisioner.EventData(hwspec=self.hwspec, status=self.status))

    def run(self):
        while True:
            self._inner_loop()

    def _inner_loop(self):
        self._send_event(self.state.value)
        try:
            getattr(self, self.state.value)()
        except ValueError as e:
            print(e)
            self.fail()

    def add_listener(self, listener: Callable[[str, Dict], None]):
        """Add a listener function that will be called on any events.

        :param listener: The function that will be called on an event.
        """
        self._listeners.append(listener)

    def has_hwspec(self) -> bool:
        return self.hwspec is not None

    def has_passed(self) -> bool:
        return self.provisional_status == Provisioner.Status.PASSED

    def set_status_passed(self):
        self.provisional_status = Provisioner.Status.PASSED

    def set_status_failed(self):
        self.provisional_status = Provisioner.Status.FAILED

    def set_status_retry(self):
        self.provisional_status = Provisioner.Status.RETRY

    def set_status_fail(self):
        self.provisional_status = Provisioner.Status.FAILED

    def set_status_inprogress(self):
        self.status = Provisioner.Status.INPROGRESS

    def set_status_waiting(self):
        self.status = Provisioner.Status.WAITING

    def promote_provision_status(self):
        self.status = self.provisional_status

    def reset(self):
        self.hwspec: Optional[HWSpec] = None
        self.logs: str = ""
        self.status: Provisioner.Status = Provisioner.Status.UNKNOWN