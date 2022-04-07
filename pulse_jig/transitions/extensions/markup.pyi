from ..core import Enum as Enum, Machine as Machine
from typing import Any

class MarkupMachine(Machine):
    state_attributes: Any
    transition_attributes: Any
    def __init__(self, *args, **kwargs) -> None: ...
    @property
    def auto_transitions_markup(self): ...
    @auto_transitions_markup.setter
    def auto_transitions_markup(self, value) -> None: ...
    @property
    def markup(self): ...
    def get_markup_config(self): ...
    def add_transition(
        self,
        trigger,
        source,
        dest,
        conditions: Any | None = ...,
        unless: Any | None = ...,
        before: Any | None = ...,
        after: Any | None = ...,
        prepare: Any | None = ...,
        **kwargs
    ) -> None: ...
    def add_states(
        self,
        states,
        on_enter: Any | None = ...,
        on_exit: Any | None = ...,
        ignore_invalid_triggers: Any | None = ...,
        **kwargs
    ) -> None: ...
    @staticmethod
    def format_references(func): ...

def rep(func, format_references: Any | None = ...): ...
