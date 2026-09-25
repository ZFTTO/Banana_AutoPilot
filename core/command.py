"""Driving values shared by manual input and model inference."""

from dataclasses import dataclass


@dataclass
class DriveCommand:
    throttle: float = 0.0
    steering: float = 0.0
