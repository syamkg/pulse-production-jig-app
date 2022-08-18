import logging

import serial

from pulse_jig.config import settings
from .provisioner import Provisioner
from ..jig_client import JigClient

logger = logging.getLogger("provisioner")


class PulseProvisioner(Provisioner):
    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar)
        self._init_state_machine()
        self._pulse_manager = pulse_manager
        self._port = serial.Serial(baudrate=115200)
        self._port.port = dev
        self._test_firmware_path = settings.app.test_firmware_path
        self._prod_firmware_path = settings.app.prod_firmware_path
        self.mode = self.Mode()

    def run(self):
        while True:
            try:
                self._inner_loop()
            except Exception as e:
                logger.error(str(e))
                self.device_lost()

    def loading_prod_firmware(self):
        if not settings.app.skip_firmware_load:
            self._pulse_manager.load_firmware(self._prod_firmware_path)

        self._pf = JigClient(self._port)
        self._pulse_manager.reset_device()  # this has no effect for Phase 2 tests
        header = self._pf.read_boot_header()

        if not settings.app.skip_firmware_load and not validate_prod_firmware_load(header):
            logger.error("Failed to load the Production firmware")
            self.retry()
            return

        self.prod_firmware_version = get_prod_firmware_version(header)
        self.proceed()

    def waiting_for_pcb_removal(self):
        self._pulse_manager.await_removal()
        self.proceed()

    def update_qrcode(self):
        if self.has_passed():
            self.qrcode = self.QRCode(
                sn=self.hwspec.serial,
                rev=self.hwspec.hw_revision,
                dom=self.hwspec.assembly_timestamp,
                cert=self.hwspec.iecex_cert,
            )

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


def validate_prod_firmware_load(header: str) -> bool:
    return "Starting Production Firmware" in header


def get_prod_firmware_version(header: str) -> str:
    version = ""
    for ln in header.splitlines(True):
        if ln.startswith("Firmware Version:"):
            version = ln[17:].strip()  # Strip - "Firmware Version:"
    return version
