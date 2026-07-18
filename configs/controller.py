from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

@dataclass
class controllerConfig:
    control_mode: Literal["keyboard", "switchJoyCon"] = "keyboard"

    # keyboard
    key_toggle_record: str = "r"
    key_exit: str = "esc"

    key_throttle_up: str = "w"
    key_throttle_down: str = "s"

    key_steer_left: str = "a"
    key_steer_right: str = "d"


    # switch
    switch_deadzone: float = 0.05

    switch_axis_throttle: int = 1
    switch_axis_steering: int = 0

    switch_btn_toggle_record: int = 0
    switch_btn_exit: int = 1