import ImageDraw as ImageDraw
import abc
import qrcode.image.base
from qrcode.image.styles.colormasks import SolidFillColorMask as SolidFillColorMask
from qrcode.image.styles.moduledrawers import SquareModuleDrawer as SquareModuleDrawer
from typing import Any

class StyledPilImage(qrcode.image.base.BaseImage, metaclass=abc.ABCMeta):
    kind: str
    needs_context: bool
    needs_processing: bool
    color_mask: Any
    module_drawer: Any
    eye_drawer: Any
    embeded_image: Any
    embeded_image_resample: Any
    mode: Any
    back_color: Any
    paint_color: Any
    def new_image(self, **kwargs): ...
    def drawrect_context(self, row, col, is_active, context) -> None: ...
    def process(self) -> None: ...
    def draw_embeded_image(self) -> None: ...
    def is_eye(self, row, col): ...
    def save(self, stream, format: Any | None = ..., **kwargs) -> None: ...
    def __getattr__(self, name): ...
