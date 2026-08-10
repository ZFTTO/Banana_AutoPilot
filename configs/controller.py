from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

@dataclass 
class KeyboardConfig:
    key_throttle_up: str = "w"
    key_throttle_down: str = "s"

    key_steer_left: str = "a"
    key_steer_right: str = "d"

    key_toggle_record: str = "r"
    key_exit: str = "q"

@dataclass 
class SwitchConfig:
    switch_deadzone: float = 0.05

    switch_axis_throttle: int = 1
    switch_axis_steering: int = 0

    switch_btn_toggle_record: int = 1
    switch_btn_toggle_exit: int = 0

@dataclass
class ControllerConfig:
    control_mode: Literal["keyboard", "switch"] = "keyboard"

    keyboard: KeyboardConfig = field(default_factory = KeyboardConfig)
    switch: SwitchConfig = field(default_factory = SwitchConfig)
