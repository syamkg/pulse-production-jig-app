import logging
from dataclasses import dataclass
from datetime import datetime

import json
import serial

from pulse_jig.config import settings
from .provisioner import Provisioner
from ..jig_client import JigClient

logger = logging.getLogger("provisioner")


class PulseProvisioner(Provisioner):
    @dataclass
    class QRCode(Provisioner.QRCode):
        deveui: str
        ass_id: str
        ass_ver: str

        def __str__(self):
            """
            DO NOT CHANGE THIS STRUCTURE OR ORDER!!!
            Laser engraver relies on this exact order
            """

            # the purpose of this is to provide the exact json string that we want the engraver to use for the QR code.
            # the other rows are for the other markings on the device.
            # the reason for having the same data repeated in a different way is that we wish to make it as easy as possible for the company/ies doing this work for us.
            qr_data = {
                "devEUI": self.deveui,
                "sn": self.sn,
                "dom": self.dom,
                "fab_ver": self.rev,
                "cert": self.cert,
            }

            return (
                f"{self.sn}\n"
                f"{self.rev}\n"
                f"{datetime.fromtimestamp(self.dom).strftime('%m/%y')}\n"
                f"{self.cert}\n"
                f"{self.deveui}\n"
                f"{self.ass_id}\n"
                f"{self.ass_ver}\n"
                f"{json.dumps(qr_data, separators=(',', ':'))}"
            )

    @dataclass
    class Mode(Provisioner.Mode):
        region_ch_plan: str = ""

    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar)
        self._init_state_machine()
        self._pulse_manager = pulse_manager
        self._port = serial.Serial(baudrate=115200)
        self._port.port = dev
        self._test_firmware_path = settings.app.test_firmware_path
        self._prod_firmware_au915_path = settings.app.prod_firmware_au915_path
        self._prod_firmware_as923_path = settings.app.prod_firmware_as923_path
        self.mode = self.Mode()

    def run(self):
        while self.is_running():
            try:
                self._inner_loop()
            except Exception as e:
                logger.error(str(e))
                self.device_lost()

        logger.info("pulse_provisioner provisioning thread terminated")

    def reset_device(self):
        self._pulse_manager.reset_device()

    def loading_prod_firmware(self):
        prod_firmware_path = None
        if self.mode.region_ch_plan == "AU915":
            prod_firmware_path = self._prod_firmware_au915_path
        elif self.mode.region_ch_plan == "AS923":
            prod_firmware_path = self._prod_firmware_as923_path
        else:
            logger.error("Invalid region selected, failed to load Production firmware")
            self.retry()
            return

        if not settings.app.skip_firmware_load:
            self._pulse_manager.load_firmware(prod_firmware_path)

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
                deveui=self.dev_eui,
                ass_id="{:#04x}".format(self.hwspec.assembly_id),
                ass_ver="{:#04x}".format(self.hwspec.assembly_version),
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
