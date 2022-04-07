from ..core import (
    Enum as Enum,
    EnumMeta as EnumMeta,
    Event as Event,
    EventData as EventData,
    Machine as Machine,
    MachineError as MachineError,
    State as State,
    Transition as Transition,
    listify as listify,
)
from collections import defaultdict as defaultdict
from typing import Any

class FunctionWrapper:
    def __init__(self, func, path) -> None: ...
    def add(self, func, path) -> None: ...
    def __call__(self, *args, **kwargs): ...

class NestedEvent(Event):
    def trigger(self, _model, _machine, *args, **kwargs): ...

class NestedState(State):
    separator: str
    initial: Any
    events: Any
    states: Any
    def __init__(
        self,
        name,
        on_enter: Any | None = ...,
        on_exit: Any | None = ...,
        ignore_invalid_triggers: Any | None = ...,
        initial: Any | None = ...,
    ) -> None: ...
    def add_substate(self, state) -> None: ...
    def add_substates(self, states) -> None: ...
    def scoped_enter(self, event_data, scope=...) -> None: ...
    def scoped_exit(self, event_data, scope=...) -> None: ...
    @property
    def name(self): ...

class NestedTransition(Transition):
    def __deepcopy__(self, memo): ...

class HierarchicalMachine(Machine):
    state_cls: Any
    transition_cls: Any
    event_cls: Any
    prefix_path: Any
    scoped: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def __call__(self, to_scope: Any | None = ...): ...
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def add_model(self, model, initial: Any | None = ...) -> None: ...
    @property
    def initial(self): ...
    @initial.setter
    def initial(self, value) -> None: ...
    def add_ordered_transitions(
        self,
        states: Any | None = ...,
        trigger: str = ...,
        loop: bool = ...,
        loop_includes_initial: bool = ...,
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
    def get_global_name(self, state: Any | None = ..., join: bool = ...): ...
    def get_nested_state_names(self): ...
    def get_nested_transitions(self, trigger: str = ..., src_path: Any | None = ..., dest_path: Any | None = ...): ...
    def get_nested_triggers(self, src_path: Any | None = ...): ...
    def get_state(self, state, hint: Any | None = ...): ...
    def get_states(self, states): ...
    def get_transitions(self, trigger: str = ..., source: str = ..., dest: str = ..., delegate: bool = ...): ...
    def get_triggers(self, *args): ...
    def has_trigger(self, trigger, state: Any | None = ...): ...
    def is_state(self, state_name, model, allow_substates: bool = ...): ...
    def on_enter(self, state_name, callback) -> None: ...
    def on_exit(self, state_name, callback) -> None: ...
    def set_state(self, states, model: Any | None = ...) -> None: ...
    def to_state(self, model, state_name, *args, **kwargs) -> None: ...
    def trigger_event(self, _model, _trigger, *args, **kwargs): ...
