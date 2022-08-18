import enum
import logging
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from pulse_jig.config import settings
from ..hwspec import HWSpec
from ..registrar import Registrar, NetworkStatus

logger = logging.getLogger("provisioner")


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
    class QRCode:
        """
        Class containing common attributes for the QR code.
        Extend this in extended provisioner class to add
        target specific attributes.
        """

        sn: str
        rev: str
        dom: int
        cert: str

    @dataclass
    class Mode:
        """
        Class containing common attributes for the mode.
        In general these have are fixed values set via settings.

        Extend this in extended provisioner class to add
        target specific attributes.

        If any of the added attributes need to be set via UI,
        then add them to the settings under `mode_vars`
        with the exact attribute name.
        Options/values for dropdown can be added as an array.
        """

        manufacturer: str = settings.device.manufacturer_name
        target: str = settings.app.target

    @dataclass
    class EventData:
        hwspec: Optional[HWSpec]
        status: "Provisioner.Status"
        qrcode: Optional["Provisioner.QRCode"]
        reset_logs: bool
        mode: Optional["Provisioner.Mode"]
        test_firmware_version: Optional[str]
        prod_firmware_version: Optional[str]

    def __init__(self, registrar: Registrar):
        self.reset()
        self._registrar = registrar
        self._listeners: List[Callable] = []
        self.status = Provisioner.Status.UNKNOWN
        self.provisional_status = Provisioner.Status.UNKNOWN
        self.reset_gui_logs = False
        self.mode = self.Mode()
        self.test_firmware_version: str = "0.0.0"
        self.prod_firmware_version: str = "0.0.0"

    def _send_event(self, name: str):
        for listener in self._listeners:
            listener(
                name,
                Provisioner.EventData(
                    hwspec=self.hwspec,
                    status=self.status,
                    qrcode=self.qrcode,
                    reset_logs=self.reset_gui_logs,
                    mode=self.mode,
                    test_firmware_version=self.test_firmware_version,
                    prod_firmware_version=self.prod_firmware_version,
                ),
            )

    def run(self):
        while True:
            self._inner_loop()

    def _inner_loop(self):
        self._send_event(self.state.value)
        try:
            getattr(self, self.state.value)()
            logger.info(f"{self.state.value}()")
        except ValueError as e:
            logger.error(str(e))
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

    def has_network(self) -> bool:
        return self._registrar.network_status == NetworkStatus.CONNECTED

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
        self.status: Provisioner.Status = Provisioner.Status.UNKNOWN
        self.qrcode: Optional[Provisioner.QRCode] = None

    def reset_logs(self):
        # Clear firmware logs if exists.
        if hasattr(self, "_ftf"):
            self._ftf.reset_logs()

        # Clear GUI logs
        # 1. Set reset_gui_logs flag to True
        self.reset_gui_logs: bool = True
        # 2. Send an additional event to GUI
        self._send_event(self.state.value)
        # 3. Toggle back the reset_gui_logs flag
        self.reset_gui_logs: bool = False
