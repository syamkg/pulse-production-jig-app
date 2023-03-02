import time
from dataclasses import dataclass

from pulse_jig.config import settings
from .jig_client import JigClient


@dataclass
class HWSpec:
    """
    HWSpec definition from the pulse firmware. The HWSpec is a standardised
    set of fields and format intended to be used by pulse devices and probes
    to make identification and tracing easy.
    """

    serial: str = ""
    thing_type_name: str = ""
    thing_type_id: int = 0x00
    hw_revision: str = ""
    assembly_id: int = 0x00
    assembly_version: int = 0x00
    assembly_timestamp: int = 0
    manufacturer_name: str = ""
    manufacturer_id: int = 0x00
    iecex_cert: str = ""

    def get(self, ftf: JigClient):
        self.serial = ftf.hwspec_get("serial")
        self.thing_type_name = ftf.hwspec_get("thing_type_name")
        self.thing_type_id = int(ftf.hwspec_get("thing_type_id"), 16)
        self.hw_revision = str(ftf.hwspec_get("hw_revision"))
        self.assembly_id = int(ftf.hwspec_get("assembly_id"), 16)
        self.assembly_version = int(ftf.hwspec_get("assembly_version"), 16)
        self.assembly_timestamp = int(ftf.hwspec_get("assembly_timestamp"))
        self.manufacturer_name = ftf.hwspec_get("manufacturer_name")
        self.manufacturer_id = int(ftf.hwspec_get("manufacturer_id"), 16)
        self.iecex_cert = ftf.hwspec_get("iecex_cert")

    def set(self, iecex_cert):
        # the serial and properties that it's composed of should never be overwritten
        if not self.serial:
            timestamp = int(time.time())
            self.serial = self._generate_serial(timestamp)
            self.assembly_timestamp = timestamp
            self.thing_type_name = settings.device.thing_type_name
            self.thing_type_id = settings.device.thing_type_id
        # other properties are allowed to be changed
        self.hw_revision = str(settings.device.hw_revision)
        self.assembly_id = settings.device.assembly_id
        self.assembly_version = settings.device.assembly_version
        self.manufacturer_name = settings.device.manufacturer_name
        self.manufacturer_id = settings.device.manufacturer_id
        self.iecex_cert = iecex_cert

    def save(self, ftf: JigClient):
        ftf.hwspec_set("serial", self.serial)
        ftf.hwspec_set("thing_type_name", self.thing_type_name)
        ftf.hwspec_set("thing_type_id", str(self.thing_type_id))
        ftf.hwspec_set("hw_revision", self.hw_revision)
        ftf.hwspec_set("assembly_id", str(self.assembly_id))
        ftf.hwspec_set("assembly_version", str(self.assembly_version))
        ftf.hwspec_set("assembly_timestamp", str(self.assembly_timestamp))
        ftf.hwspec_set("manufacturer_name", self.manufacturer_name)
        ftf.hwspec_set("manufacturer_id", str(self.manufacturer_id))
        ftf.hwspec_set("iecex_cert", self.iecex_cert)

    @staticmethod
    def _generate_serial(timestamp: int) -> str:
        minter_id = settings.device.minter_id
        device_type_id = settings.device.thing_type_id
        return f"W{minter_id}-{device_type_id}-{timestamp}"
