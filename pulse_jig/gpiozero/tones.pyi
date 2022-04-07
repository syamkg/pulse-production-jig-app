from .compat import log2 as log2
from .exc import AmbiguousTone as AmbiguousTone
from collections import namedtuple as namedtuple
from typing import Any

str: Any

class Tone(float):
    tones: str
    semitones: Any
    regex: Any
    def __new__(cls, value: Any | None = ..., **kwargs): ...
    @classmethod
    def from_midi(cls, midi_note): ...
    @classmethod
    def from_note(cls, note): ...
    @classmethod
    def from_frequency(cls, freq): ...
    @property
    def frequency(self): ...
    @property
    def midi(self): ...
    @property
    def note(self): ...
    def up(self, n: int = ...): ...
    def down(self, n: int = ...): ...
