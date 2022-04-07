from qrcode import constants as constants, exceptions as exceptions, util as util
from qrcode.image.base import BaseImage as BaseImage
from typing import Any

precomputed_qr_blanks: Any

def make(data: Any | None = ..., **kwargs): ...
def copy_2d_array(x): ...

class QRCode:
    version: Any
    error_correction: Any
    box_size: Any
    border: Any
    image_factory: Any
    def __init__(
        self,
        version: Any | None = ...,
        error_correction=...,
        box_size: int = ...,
        border: int = ...,
        image_factory: Any | None = ...,
        mask_pattern: Any | None = ...,
    ) -> None: ...
    @property
    def mask_pattern(self): ...
    @mask_pattern.setter
    def mask_pattern(self, pattern) -> None: ...
    modules: Any
    modules_count: int
    data_cache: Any
    data_list: Any
    def clear(self) -> None: ...
    def add_data(self, data, optimize: int = ...) -> None: ...
    def make(self, fit: bool = ...) -> None: ...
    def makeImpl(self, test, mask_pattern) -> None: ...
    def setup_position_probe_pattern(self, row, col) -> None: ...
    def best_fit(self, start: Any | None = ...): ...
    def best_mask_pattern(self): ...
    def print_tty(self, out: Any | None = ...) -> None: ...
    def print_ascii(self, out: Any | None = ..., tty: bool = ..., invert: bool = ...): ...
    def make_image(self, image_factory: Any | None = ..., **kwargs): ...
    def is_constrained(self, row, col): ...
    def get_module_context(self, row, col): ...
    def setup_timing_pattern(self) -> None: ...
    def setup_position_adjust_pattern(self) -> None: ...
    def setup_type_number(self, test) -> None: ...
    def setup_type_info(self, test, mask_pattern) -> None: ...
    def map_data(self, data, mask_pattern) -> None: ...
    def get_matrix(self): ...
