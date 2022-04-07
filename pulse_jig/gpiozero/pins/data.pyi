from ..devices import Device as Device
from ..exc import (
    PinInvalidPin as PinInvalidPin,
    PinMultiplePins as PinMultiplePins,
    PinNoPins as PinNoPins,
    PinUnknownPi as PinUnknownPi,
)
from typing import Any

str: Any
V1_8: str
V3_3: str
V5: str
GND: str
NC: str
GPIO0: str
GPIO1: str
GPIO2: str
GPIO3: str
GPIO4: str
GPIO5: str
GPIO6: str
GPIO7: str
GPIO8: str
GPIO9: str
GPIO10: str
GPIO11: str
GPIO12: str
GPIO13: str
GPIO14: str
GPIO15: str
GPIO16: str
GPIO17: str
GPIO18: str
GPIO19: str
GPIO20: str
GPIO21: str
GPIO22: str
GPIO23: str
GPIO24: str
GPIO25: str
GPIO26: str
GPIO27: str
GPIO28: str
GPIO29: str
GPIO30: str
GPIO31: str
GPIO32: str
GPIO33: str
GPIO34: str
GPIO35: str
GPIO36: str
GPIO37: str
GPIO38: str
GPIO39: str
GPIO40: str
GPIO41: str
GPIO42: str
GPIO43: str
GPIO44: str
GPIO45: str
REV1_BOARD: str
REV2_BOARD: str
A_BOARD: str
BPLUS_BOARD: str
B3PLUS_BOARD: str
B4_BOARD: str
APLUS_BOARD: str
A3PLUS_BOARD: str
ZERO12_BOARD: str
ZERO13_BOARD: str
CM_BOARD: str
CM3PLUS_BOARD: str
CM4_BOARD: str
P400_BOARD: str
REV1_P1: Any
REV2_P1: Any
REV2_P5: Any
PLUS_J8: Any
PLUS_POE: Any
CM_SODIMM: Any
CM3_SODIMM: Any
CM4_J6: Any
CM4_J2: Any
PI_REVISIONS: Any

class Style:
    color: Any
    effects: Any
    colors: Any
    def __init__(self, color: Any | None = ...) -> None: ...
    @classmethod
    def from_style_content(cls, format_spec): ...
    def __call__(self, format_spec): ...
    def __format__(self, format_spec): ...

class PinInfo: ...

class HeaderInfo:
    def __format__(self, format_spec): ...
    def pprint(self, color: Any | None = ...) -> None: ...

class PiBoardInfo:
    @classmethod
    def from_revision(cls, revision): ...
    def physical_pins(self, function): ...
    def physical_pin(self, function): ...
    def pulled_up(self, function): ...
    def to_gpio(self, spec): ...
    def __format__(self, format_spec): ...
    def pprint(self, color: Any | None = ...) -> None: ...

def pi_info(revision: Any | None = ...): ...
