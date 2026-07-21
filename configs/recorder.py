from __future__ import annotations

from .esp32 import ESP32Config
from .controller import ControllerConfig
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class RecorderConfig:
    esp32: ESP32Config = field(default_factory = ESP32Config)

    controller: ControllerConfig = field(default_factory = ControllerConfig)

    # ── Controller ──────────────────────────────────────────────────
    control_mode: Literal["keyboard", "switch"] = "keyboard"
    ws_send_interval_ms: float = 25.0

    # ── Dataset / Recording ─────────────────────────────────────────
    dataset_root: str = "datasets"
    frame_extension: str = ".jpg"
    frame_quality: int = 95

    # ── Display ─────────────────────────────────────────────────────
    window_name: str = "LuluLab Recorder"
    display_fps_alpha: float = 0.1

    # ── Recording control ───────────────────────────────────────────
    idle_throttle_on_stop: bool = True