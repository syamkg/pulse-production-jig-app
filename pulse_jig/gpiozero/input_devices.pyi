from .compat import mean as mean, median as median
from .devices import CompositeDevice as CompositeDevice, GPIODevice as GPIODevice
from .exc import (
    DeviceClosed as DeviceClosed,
    DistanceSensorNoEcho as DistanceSensorNoEcho,
    InputDeviceError as InputDeviceError,
    PWMSoftwareFallback as PWMSoftwareFallback,
    PinInvalidState as PinInvalidState,
)
from .mixins import EventsMixin as EventsMixin, GPIOQueue as GPIOQueue, HoldMixin as HoldMixin, event as event
from .pins.pigpio import PiGPIOFactory as PiGPIOFactory
from itertools import tee as tee
from time import time as time
from typing import Any

class InputDevice(GPIODevice):
    def __init__(
        self, pin: Any | None = ..., pull_up: bool = ..., active_state: Any | None = ..., pin_factory: Any | None = ...
    ) -> None: ...
    @property
    def pull_up(self): ...

class DigitalInputDevice(EventsMixin, InputDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        pull_up: bool = ...,
        active_state: Any | None = ...,
        bounce_time: Any | None = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...

class SmoothedInputDevice(EventsMixin, InputDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        pull_up: bool = ...,
        active_state: Any | None = ...,
        threshold: float = ...,
        queue_len: int = ...,
        sample_wait: float = ...,
        partial: bool = ...,
        average=...,
        ignore: Any | None = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    def close(self) -> None: ...
    @property
    def queue_len(self): ...
    @property
    def partial(self): ...
    @property
    def value(self): ...
    @property
    def threshold(self): ...
    @threshold.setter
    def threshold(self, value) -> None: ...
    @property
    def is_active(self): ...

class Button(HoldMixin, DigitalInputDevice):
    hold_time: Any
    hold_repeat: Any
    def __init__(
        self,
        pin: Any | None = ...,
        pull_up: bool = ...,
        active_state: Any | None = ...,
        bounce_time: Any | None = ...,
        hold_time: int = ...,
        hold_repeat: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def value(self): ...

class LineSensor(SmoothedInputDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        pull_up: bool = ...,
        active_state: Any | None = ...,
        queue_len: int = ...,
        sample_rate: int = ...,
        threshold: float = ...,
        partial: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def value(self): ...
    @property
    def line_detected(self): ...

class MotionSensor(SmoothedInputDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        pull_up: bool = ...,
        active_state: Any | None = ...,
        queue_len: int = ...,
        sample_rate: int = ...,
        threshold: float = ...,
        partial: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def value(self): ...

class LightSensor(SmoothedInputDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        queue_len: int = ...,
        charge_time_limit: float = ...,
        threshold: float = ...,
        partial: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def charge_time_limit(self): ...
    @property
    def value(self): ...

class DistanceSensor(SmoothedInputDevice):
    ECHO_LOCK: Any
    threshold: Any
    speed_of_sound: float
    def __init__(
        self,
        echo: Any | None = ...,
        trigger: Any | None = ...,
        queue_len: int = ...,
        max_distance: int = ...,
        threshold_distance: float = ...,
        partial: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    def close(self) -> None: ...
    @property
    def max_distance(self): ...
    @max_distance.setter
    def max_distance(self, value) -> None: ...
    @property
    def threshold_distance(self): ...
    @threshold_distance.setter
    def threshold_distance(self, value) -> None: ...
    @property
    def distance(self): ...
    @property
    def value(self): ...
    @property
    def trigger(self): ...
    @property
    def echo(self): ...
    @property
    def in_range(self): ...

class RotaryEncoder(EventsMixin, CompositeDevice):
    TRANSITIONS: Any
    def __init__(
        self,
        a,
        b,
        bounce_time: Any | None = ...,
        max_steps: int = ...,
        threshold_steps=...,
        wrap: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    def wait_for_rotate(self, timeout: Any | None = ...): ...
    def wait_for_rotate_clockwise(self, timeout: Any | None = ...): ...
    def wait_for_rotate_counter_clockwise(self, timeout: Any | None = ...): ...
    when_rotated: Any
    when_rotated_clockwise: Any
    when_rotated_counter_clockwise: Any
    @property
    def steps(self): ...
    @steps.setter
    def steps(self, value) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    @property
    def is_active(self): ...
    @property
    def max_steps(self): ...
    @property
    def threshold_steps(self): ...
    @property
    def wrap(self): ...
