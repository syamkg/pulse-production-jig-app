import qrcode.image.base
from typing import Any

class PymagingImage(qrcode.image.base.BaseImage):
    kind: str
    allowed_kinds: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def new_image(self, **kwargs): ...
    def drawrect(self, row, col) -> None: ...
    def save(self, stream, kind: Any | None = ...) -> None: ...
    def check_kind(self, kind, transform: Any | None = ..., **kwargs): ...
