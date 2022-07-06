from dataclasses import dataclass

from .jig_client import JigClient


@dataclass
class ProbeSpec:
    """
    Definition for the `probe` chunk in the probes EEPROM.
    """

    cable_length: int = 0

    def get(self, ftf: JigClient):
        self.cable_length = self._parse_cable_length(ftf.hwchunk_get_probe())

    def set(self, cable_length: float):
        self.cable_length = int(cable_length * 1000)

    def save(self, ftf: JigClient):
        ftf.hwchunk_write_probe(self.cable_length)

    @staticmethod
    def _parse_cable_length(data: str):
        return int(data.split("cable length: ")[1].split("mm")[0])
