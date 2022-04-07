from .devices import Device as Device
from .exc import DeviceClosed as DeviceClosed, ThresholdOutOfRange as ThresholdOutOfRange
from .mixins import EventsMixin as EventsMixin, event as event
from .threads import GPIOThread as GPIOThread
from typing import Any

str: Any

class InternalDevice(EventsMixin, Device):
    def __init__(self, pin_factory: Any | None = ...) -> None: ...
    def close(self) -> None: ...
    @property
    def closed(self): ...

class PolledInternalDevice(InternalDevice):
    def __init__(self, event_delay: float = ..., pin_factory: Any | None = ...) -> None: ...
    def close(self) -> None: ...
    @property
    def event_delay(self): ...
    @event_delay.setter
    def event_delay(self, value) -> None: ...
    def wait_for_active(self, timeout: Any | None = ...): ...
    def wait_for_inactive(self, timeout: Any | None = ...): ...

class PingServer(PolledInternalDevice):
    def __init__(self, host, event_delay: float = ..., pin_factory: Any | None = ...) -> None: ...
    @property
    def host(self): ...
    @property
    def value(self): ...
    when_activated: Any
    when_deactivated: Any

class CPUTemperature(PolledInternalDevice):
    sensor_file: Any
    min_temp: Any
    max_temp: Any
    threshold: Any
    def __init__(
        self,
        sensor_file: str = ...,
        min_temp: float = ...,
        max_temp: float = ...,
        threshold: float = ...,
        event_delay: float = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def temperature(self): ...
    @property
    def value(self): ...
    @property
    def is_active(self): ...
    when_activated: Any
    when_deactivated: Any

class LoadAverage(PolledInternalDevice):
    load_average_file: Any
    min_load_average: Any
    max_load_average: Any
    threshold: Any
    def __init__(
        self,
        load_average_file: str = ...,
        min_load_average: float = ...,
        max_load_average: float = ...,
        threshold: float = ...,
        minutes: int = ...,
        event_delay: float = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def load_average(self): ...
    @property
    def value(self): ...
    @property
    def is_active(self): ...
    when_activated: Any
    when_deactivated: Any

class TimeOfDay(PolledInternalDevice):
    def __init__(
        self, start_time, end_time, utc: bool = ..., event_delay: float = ..., pin_factory: Any | None = ...
    ) -> None: ...
    @property
    def start_time(self): ...
    @property
    def end_time(self): ...
    @property
    def utc(self): ...
    @property
    def value(self): ...
    when_activated: Any
    when_deactivated: Any

class DiskUsage(PolledInternalDevice):
    filesystem: Any
    threshold: Any
    def __init__(
        self, filesystem: str = ..., threshold: float = ..., event_delay: float = ..., pin_factory: Any | None = ...
    ) -> None: ...
    @property
    def usage(self): ...
    @property
    def value(self): ...
    @property
    def is_active(self): ...
    when_activated: Any
    when_deactivated: Any
