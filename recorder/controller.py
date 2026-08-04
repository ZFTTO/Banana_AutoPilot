'''
-c.start()
-c.read()
-c.stop()
-create_controller(config: ControllerConfig) -> Controller
'''
from __future__ import annotations

import logging 
import pygame

from typing import Optional, Sequence
from dataclasses import dataclass
from abc import ABC, abstractmethod

from configs.controller import ControllerConfig

logger = logging.getLogger(__name__)

@dataclass
class ControllerState:
    throttle: float = 0.0
    steering: float = 0.0
    action: Optional[str] = None

class Controller(ABC):
    @abstractmethod
    def start(self):
        """Start the controller's input loop."""
        ...

    @abstractmethod
    def stop(self):
        """Stop the controller's input loop."""
        ...

    @abstractmethod
    def read(self) -> ControllerState:
        """read the current state of the controller."""
        ...
    
class KeyboardController(Controller):
    def __init__(self, config: ControllerConfig):
        self._config = config
        self._initialized = False

        self._prev_keycodes: Optional[Sequence[bool]] = None
        self._kcode_up: int = 0
        self._kcode_down: int = 0
        self._kcode_left: int = 0
        self._kcode_right: int = 0
        self._kcode_record: int = 0
        self._kcode_exit: int = 0

    def start(self) -> None:
        if not pygame.get_init():
            pygame.init()

        # macOS:
        # pygame.key.get_pressed() may not work unless SDL has an active display.
        # Create a minimal hidden window when no display exists.
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))

        try:
            self._kcode_up = pygame.key.key_code(self._config.keyboard.key_throttle_up)
            self._kcode_down = pygame.key.key_code(self._config.keyboard.key_throttle_down)
            self._kcode_left = pygame.key.key_code(self._config.keyboard.key_steer_left)
            self._kcode_right = pygame.key.key_code(self._config.keyboard.key_steer_right)
            self._kcode_record = pygame.key.key_code(self._config.keyboard.key_toggle_record)
            self._kcode_exit = pygame.key.key_code(self._config.keyboard.key_exit)
        except ValueError as ecx:
            logger.error(f"Invalid key configuration: {ecx}")
        
        self._initialized = True
        logger.info("Keyboard controller initialized.")

    def stop(self) -> None:
        if self._initialized:
            pygame.quit()
            self._initialized = False
            logger.info("Keyboard controller stopped.")

    def read(self) -> ControllerState:
        if not self._initialized:
            return ControllerState()
        
        pygame.event.pump()
        curr_keycodes = pygame.key.get_pressed()

        if self._prev_keycodes is None:
            self._prev_keycodes = curr_keycodes

        state = ControllerState()

        if curr_keycodes[self._kcode_up]:
            state.throttle = 1.0
        elif curr_keycodes[self._kcode_down]:
            state.throttle = -1.0
        if curr_keycodes[self._kcode_left]:
            state.steering = -1.0
        elif curr_keycodes[self._kcode_right]:
            state.steering = 1.0

        if curr_keycodes[self._kcode_record] and not self._prev_keycodes[self._kcode_record]:
            state.action = "toggle_record"
        elif curr_keycodes[self._kcode_exit] and not self._prev_keycodes[self._kcode_exit]:
            state.action = "toggle_exit"

        self._prev_keycodes = curr_keycodes
        return state

class SwitchController(Controller):
    def __init__(self, config: ControllerConfig):
        self._config = config
        self._initialized = False

        self._joystick: Optional[pygame.joystick.Joystick] = None
        self._prev_btn_rec: bool = False
        self._prev_btn_ext: bool = False

    def start(self) -> None:
        if self._initialized:
            return
        if not pygame.get_init():
            pygame.init()
        if not pygame.joystick.get_init():
            pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            return
        
        try:
            self._joystick = pygame.joystick.Joystick(0)
            self._joystick.init()
            self._initialized = True
            logger.info("Switch controller initialized.")

        except Exception as exc:
            logger.error("Switch controller initialization fail: %s", exc)

    def stop(self) -> None:
        if self._joystick is not None:
            self._joystick.quit()

        self._initialized = False
        logger.info("Switch controller stopped.")
    
    def read(self) -> ControllerState:
        if not self._initialized or self._joystick is None:
            return ControllerState()
        
        pygame.event.pump()
        state = ControllerState()

        try:
            raw_t = -self._joystick.get_axis(self._config.switch.switch_axis_throttle)
            raw_s = self._joystick.get_axis(self._config.switch.switch_axis_steering)

            state.throttle = 0.0 if abs(raw_t) < self._config.switch.switch_deadzone else raw_t
            state.steering = 0.0 if abs(raw_s) < self._config.switch.switch_deadzone else raw_s

            curr_btn_rec = self._joystick.get_button(self._config.switch.switch_btn_toggle_record)
            curr_btn_ext = self._joystick.get_button(self._config.switch.switch_btn_toggle_exit)

            if curr_btn_rec and not self._prev_btn_rec:
                state.action = "toggle_record"
            if curr_btn_ext and not self._prev_btn_ext:
                state.action = "toggle_exit"
            
            self._prev_btn_rec = curr_btn_rec
            self._prev_btn_ext = curr_btn_ext

        except Exception as exc:
            logger.error("joystick reading error: %s", exc)
            self._initialized = False #
        
        return state
    
    @property
    def available(self) -> bool:
        return self._initialized
    
def create_controller(config: ControllerConfig) -> Controller:
    if config.control_mode == "switch":
        return SwitchController(config)
    return KeyboardController(config)
            