import time
from dataclasses import dataclass
from datetime import datetime

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
    assembly_version: str = ""
    assembly_timestamp: int = 0
    manufacturer_name: str = ""
    manufacturer_id: int = 0x00
    factory_test_firmware_version: str = ""

    def get(self, ftf: JigClient):
        self.serial = ftf.hwspec_get("serial")
        self.thing_type_name = ftf.hwspec_get("thing_type_name")
        self.thing_type_id = int(ftf.hwspec_get("thing_type_id"), 16)
        self.hw_revision = ftf.hwspec_get("hw_revision")
        self.assembly_id = int(ftf.hwspec_get("assembly_id"), 16)
        self.assembly_version = ftf.hwspec_get("assembly_version")
        self.assembly_timestamp = self._parse_assembly_timestamp(ftf.hwspec_get("assembly_timestamp"))
        self.manufacturer_name = ftf.hwspec_get("manufacturer_name")
        self.manufacturer_id = int(ftf.hwspec_get("manufacturer_id"), 16)
        self.factory_test_firmware_version = ftf.hwspec_get("factory_test_firmware_version")

    def set(self, ftf: JigClient):
        timestamp = int(time.time())
        self.serial = self._generate_serial(timestamp)
        self.thing_type_name = settings.device.thing_type_name
        self.thing_type_id = settings.device.thing_type_id
        self.hw_revision = settings.device.hw_revision
        self.assembly_id = settings.device.assembly_id
        self.assembly_version = settings.device.assembly_version
        self.assembly_timestamp = timestamp
        self.manufacturer_name = settings.device.manufacturer_name
        self.manufacturer_id = settings.device.manufacturer_id
        self.factory_test_firmware_version = ftf.firmware_version()

    def save(self, ftf: JigClient):
        ftf.hwspec_set("serial", self.serial)
        ftf.hwspec_set("thing_type_name", self.thing_type_name)
        ftf.hwspec_set("thing_type_id", str(self.thing_type_id))
        ftf.hwspec_set("hw_revision", self.hw_revision)
        ftf.hwspec_set("assembly_id", str(self.assembly_id))
        ftf.hwspec_set("assembly_version", self.assembly_version)
        ftf.hwspec_set("assembly_timestamp", str(self.assembly_timestamp))
        ftf.hwspec_set("manufacturer_name", self.manufacturer_name)
        ftf.hwspec_set("manufacturer_id", str(self.manufacturer_id))
        ftf.hwspec_set("factory_test_firmware_version", self.factory_test_firmware_version)

    @staticmethod
    def _generate_serial(timestamp: int) -> str:
        minter_id = settings.device.minter_id
        device_type_id = settings.device.thing_type_id
        return f"W{minter_id}-{device_type_id}-{timestamp}"

    @staticmethod
    def _parse_assembly_timestamp(timestamp: str) -> int:
        try:
            return int(timestamp)
        except ValueError:
            dt = datetime.strptime(timestamp, "%Y-%m-%d")
            return int(datetime.timestamp(dt))
