from .compat import log2 as log2
from .devices import CompositeDevice as CompositeDevice, Device as Device, GPIODevice as GPIODevice
from .exc import (
    DeviceClosed as DeviceClosed,
    GPIOPinMissing as GPIOPinMissing,
    OutputDeviceBadValue as OutputDeviceBadValue,
    PWMSoftwareFallback as PWMSoftwareFallback,
)
from .mixins import SourceMixin as SourceMixin
from .pins.pigpio import PiGPIOFactory as PiGPIOFactory
from .threads import GPIOThread as GPIOThread
from .tones import Tone as Tone
from typing import Any

str: Any

class OutputDevice(SourceMixin, GPIODevice):
    def __init__(
        self, pin: Any | None = ..., active_high: bool = ..., initial_value: bool = ..., pin_factory: Any | None = ...
    ) -> None: ...
    def on(self) -> None: ...
    def off(self) -> None: ...
    def toggle(self) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    @property
    def active_high(self): ...
    @active_high.setter
    def active_high(self, value) -> None: ...

class DigitalOutputDevice(OutputDevice):
    def __init__(
        self, pin: Any | None = ..., active_high: bool = ..., initial_value: bool = ..., pin_factory: Any | None = ...
    ) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    def close(self) -> None: ...
    def on(self) -> None: ...
    def off(self) -> None: ...
    def blink(self, on_time: int = ..., off_time: int = ..., n: Any | None = ..., background: bool = ...) -> None: ...

class LED(DigitalOutputDevice): ...
class Buzzer(DigitalOutputDevice): ...

class PWMOutputDevice(OutputDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        active_high: bool = ...,
        initial_value: int = ...,
        frequency: int = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    def close(self) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    def on(self) -> None: ...
    def off(self) -> None: ...
    def toggle(self) -> None: ...
    @property
    def is_active(self): ...
    @property
    def frequency(self): ...
    @frequency.setter
    def frequency(self, value) -> None: ...
    def blink(
        self,
        on_time: int = ...,
        off_time: int = ...,
        fade_in_time: int = ...,
        fade_out_time: int = ...,
        n: Any | None = ...,
        background: bool = ...,
    ) -> None: ...
    def pulse(
        self, fade_in_time: int = ..., fade_out_time: int = ..., n: Any | None = ..., background: bool = ...
    ) -> None: ...

class TonalBuzzer(SourceMixin, CompositeDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        initial_value: Any | None = ...,
        mid_tone=...,
        octaves: int = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    def play(self, tone) -> None: ...
    def stop(self) -> None: ...
    @property
    def tone(self): ...
    @tone.setter
    def tone(self, value) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    @property
    def is_active(self): ...
    @property
    def octaves(self): ...
    @property
    def min_tone(self): ...
    @property
    def mid_tone(self): ...
    @property
    def max_tone(self): ...

class PWMLED(PWMOutputDevice): ...

class RGBLED(SourceMixin, Device):
    def __init__(
        self,
        red: Any | None = ...,
        green: Any | None = ...,
        blue: Any | None = ...,
        active_high: bool = ...,
        initial_value=...,
        pwm: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    def close(self) -> None: ...
    @property
    def closed(self): ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    @property
    def is_active(self): ...
    is_lit: Any
    @property
    def color(self): ...
    @color.setter
    def color(self, value) -> None: ...
    @property
    def red(self): ...
    @red.setter
    def red(self, value) -> None: ...
    @property
    def green(self): ...
    @green.setter
    def green(self, value) -> None: ...
    @property
    def blue(self): ...
    @blue.setter
    def blue(self, value) -> None: ...
    def on(self) -> None: ...
    def off(self) -> None: ...
    def toggle(self) -> None: ...
    def blink(
        self,
        on_time: int = ...,
        off_time: int = ...,
        fade_in_time: int = ...,
        fade_out_time: int = ...,
        on_color=...,
        off_color=...,
        n: Any | None = ...,
        background: bool = ...,
    ) -> None: ...
    def pulse(
        self,
        fade_in_time: int = ...,
        fade_out_time: int = ...,
        on_color=...,
        off_color=...,
        n: Any | None = ...,
        background: bool = ...,
    ) -> None: ...

class Motor(SourceMixin, CompositeDevice):
    def __init__(
        self,
        forward: Any | None = ...,
        backward: Any | None = ...,
        enable: Any | None = ...,
        pwm: bool = ...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    @property
    def is_active(self): ...
    def forward(self, speed: int = ...) -> None: ...
    def backward(self, speed: int = ...) -> None: ...
    def reverse(self) -> None: ...
    def stop(self) -> None: ...

class PhaseEnableMotor(SourceMixin, CompositeDevice):
    def __init__(
        self, phase: Any | None = ..., enable: Any | None = ..., pwm: bool = ..., pin_factory: Any | None = ...
    ) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    @property
    def is_active(self): ...
    def forward(self, speed: int = ...) -> None: ...
    def backward(self, speed: int = ...) -> None: ...
    def reverse(self) -> None: ...
    def stop(self) -> None: ...

class Servo(SourceMixin, CompositeDevice):
    def __init__(
        self,
        pin: Any | None = ...,
        initial_value: float = ...,
        min_pulse_width=...,
        max_pulse_width=...,
        frame_width=...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def frame_width(self): ...
    @property
    def min_pulse_width(self): ...
    @property
    def max_pulse_width(self): ...
    @property
    def pulse_width(self): ...
    @pulse_width.setter
    def pulse_width(self, value) -> None: ...
    def min(self) -> None: ...
    def mid(self) -> None: ...
    def max(self) -> None: ...
    def detach(self) -> None: ...
    @property
    def value(self): ...
    @value.setter
    def value(self, value) -> None: ...
    @property
    def is_active(self): ...

class AngularServo(Servo):
    def __init__(
        self,
        pin: Any | None = ...,
        initial_angle: float = ...,
        min_angle: int = ...,
        max_angle: int = ...,
        min_pulse_width=...,
        max_pulse_width=...,
        frame_width=...,
        pin_factory: Any | None = ...,
    ) -> None: ...
    @property
    def min_angle(self): ...
    @property
    def max_angle(self): ...
    @property
    def angle(self): ...
    value: Any
