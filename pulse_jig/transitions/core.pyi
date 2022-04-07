from typing import Any

class Enum: ...
class EnumMeta: ...

def listify(obj): ...

class State:
    dynamic_methods: Any
    ignore_invalid_triggers: Any
    on_enter: Any
    on_exit: Any
    def __init__(
        self, name, on_enter: Any | None = ..., on_exit: Any | None = ..., ignore_invalid_triggers: Any | None = ...
    ) -> None: ...
    @property
    def name(self): ...
    @property
    def value(self): ...
    def enter(self, event_data) -> None: ...
    def exit(self, event_data) -> None: ...
    def add_callback(self, trigger, func) -> None: ...

class Condition:
    func: Any
    target: Any
    def __init__(self, func, target: bool = ...) -> None: ...
    def check(self, event_data): ...

class Transition:
    dynamic_methods: Any
    condition_cls: Any
    source: Any
    dest: Any
    prepare: Any
    before: Any
    after: Any
    conditions: Any
    def __init__(
        self,
        source,
        dest,
        conditions: Any | None = ...,
        unless: Any | None = ...,
        before: Any | None = ...,
        after: Any | None = ...,
        prepare: Any | None = ...,
    ) -> None: ...
    def execute(self, event_data): ...
    def add_callback(self, trigger, func) -> None: ...

class EventData:
    state: Any
    event: Any
    machine: Any
    model: Any
    args: Any
    kwargs: Any
    transition: Any
    error: Any
    result: bool
    def __init__(self, state, event, machine, model, args, kwargs) -> None: ...
    def update(self, state) -> None: ...

class Event:
    name: Any
    machine: Any
    transitions: Any
    def __init__(self, name, machine) -> None: ...
    def add_transition(self, transition) -> None: ...
    def trigger(self, model, *args, **kwargs): ...
    def add_callback(self, trigger, func) -> None: ...

class Machine:
    separator: str
    wildcard_all: str
    wildcard_same: str
    state_cls: Any
    transition_cls: Any
    event_cls: Any
    self_literal: str
    states: Any
    events: Any
    send_event: Any
    auto_transitions: Any
    ignore_invalid_triggers: Any
    name: Any
    model_attribute: Any
    models: Any
    def __init__(
        self,
        model=...,
        states: Any | None = ...,
        initial: str = ...,
        transitions: Any | None = ...,
        send_event: bool = ...,
        auto_transitions: bool = ...,
        ordered_transitions: bool = ...,
        ignore_invalid_triggers: Any | None = ...,
        before_state_change: Any | None = ...,
        after_state_change: Any | None = ...,
        name: Any | None = ...,
        queued: bool = ...,
        prepare_event: Any | None = ...,
        finalize_event: Any | None = ...,
        model_attribute: str = ...,
        on_exception: Any | None = ...,
        **kwargs
    ) -> None: ...
    def add_model(self, model, initial: Any | None = ...) -> None: ...
    def remove_model(self, model) -> None: ...
    @property
    def initial(self): ...
    @initial.setter
    def initial(self, value) -> None: ...
    @property
    def has_queue(self): ...
    @property
    def model(self): ...
    @property
    def before_state_change(self): ...
    @before_state_change.setter
    def before_state_change(self, value) -> None: ...
    @property
    def after_state_change(self): ...
    @after_state_change.setter
    def after_state_change(self, value) -> None: ...
    @property
    def prepare_event(self): ...
    @prepare_event.setter
    def prepare_event(self, value) -> None: ...
    @property
    def finalize_event(self): ...
    @finalize_event.setter
    def finalize_event(self, value) -> None: ...
    @property
    def on_exception(self): ...
    @on_exception.setter
    def on_exception(self, value) -> None: ...
    def get_state(self, state): ...
    def is_state(self, state, model): ...
    def get_model_state(self, model): ...
    def set_state(self, state, model: Any | None = ...) -> None: ...
    def add_state(self, *args, **kwargs) -> None: ...
    def add_states(
        self,
        states,
        on_enter: Any | None = ...,
        on_exit: Any | None = ...,
        ignore_invalid_triggers: Any | None = ...,
        **kwargs
    ) -> None: ...
    def get_triggers(self, *args): ...
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
    def add_transitions(self, transitions) -> None: ...
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
    def get_transitions(self, trigger: str = ..., source: str = ..., dest: str = ...): ...
    def remove_transition(self, trigger, source: str = ..., dest: str = ...) -> None: ...
    def dispatch(self, trigger, *args, **kwargs): ...
    def callbacks(self, funcs, event_data) -> None: ...
    def callback(self, func, event_data) -> None: ...
    @staticmethod
    def resolve_callable(func, event_data): ...
    def __getattr__(self, name): ...

class MachineError(Exception):
    value: Any
    def __init__(self, value) -> None: ...
