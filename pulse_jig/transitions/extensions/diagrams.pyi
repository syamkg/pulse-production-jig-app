from transitions import Transition as Transition
from transitions.core import listify as listify
from transitions.extensions.markup import MarkupMachine as MarkupMachine
from typing import Any

class TransitionGraphSupport(Transition):
    label: Any
    def __init__(self, *args, **kwargs) -> None: ...

class GraphMachine(MarkupMachine):
    transition_cls: Any
    machine_attributes: Any
    hierarchical_machine_attributes: Any
    style_attributes: Any
    title: Any
    show_conditions: Any
    show_state_attributes: Any
    model_graphs: Any
    graph_cls: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def get_combined_graph(self, title: Any | None = ..., force_new: bool = ..., show_roi: bool = ...): ...
    def add_model(self, model, initial: Any | None = ...) -> None: ...
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

class BaseGraph:
    machine: Any
    fsm_graph: Any
    roi_state: Any
    def __init__(self, machine, title: Any | None = ...) -> None: ...
