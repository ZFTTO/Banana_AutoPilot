from __future__ import annotations

import logging 
import threading

import pygame
from pynput import keyboard

from typing import Optional
from abc import ABC, abstractmethod

from configs.controller import controllerConfig

class Controller(ABC):
    @abstractmethod
    def get_control(self) -> tuple[float, float]:
        """Return (throttle, steering), both in [-1.0, 1.0]."""
        ...
    
    @abstractmethod
    def get_status(self) -> Optional[str]:
        """Return an action string, or None if no action. (record, exit, etc.)"""
        ...

    @abstractmethod
    def start(self):
        """Start the controller's input loop."""
        ...

    @abstractmethod
    def stop(self):
        """Stop the controller's input loop."""
        ...
    
class KeyboardController(Controller):
    def __init__(self, config: controllerConfig) -> None:
        self._throttle: float = 0.0
        self._steering: float = 0.0
        self._status: Optional[str] = None
        self._pressed_keys: set[str] = set()
        self._lock = threading.Lock()
        self._listener: Optional[keyboard.Listener] = None

    def get_control(self) -> tuple[float, float]:
        with self._lock:
            return self._thr
