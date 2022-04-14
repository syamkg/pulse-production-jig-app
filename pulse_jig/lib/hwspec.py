from dataclasses import dataclass


@dataclass
class HWSpec:
    """
    HWSpec definition from the pulse firmware. The HWSpec is a standardised
    set of fields and format intended to be used by pulse devices and probes
    to make identification and tracing easy.
    """

    serial: str
