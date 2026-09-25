from __future__ import annotations

import cv2
import pygame
from core.utils import FpsCounter


class Display:
    def __init__(self):
        self.screen = None

        self._rec_flash_until = 0.0
        self._rec_flash_text = "●REC"
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._font_scale = 0.6
        self._font_color = (255, 255, 255)
        self._shadow = (0, 0, 0)
        self._rec_color = (0, 0, 255)
        self._idle_color = (128, 128, 128)
        self._green_color = (0, 255, 0)

    def start(self):
        self.screen = pygame.display.set_mode((320, 240))
        pygame.display.set_caption("Banana AutoPilot")

    def draw(self, frame: cv2.Mat, session: str, fps: float, recording: bool, throttle: float, steering: float) -> cv2.Mat:
        h, w = frame.shape[:2]

        cv2.putText(frame, f"Session: {session}", (10, 30),
                    self._font, self._font_scale, self._font_color, 2)
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 50), 
                    self._font, self._font_scale, self._font_color, 2)
        
        status = "●REC" if recording else "IDLE"
        color = self._rec_color if recording else self._idle_color
        cv2.putText(frame, status, (w - 50, 30),
                    self._font, self._font_scale, color, 2)

        cv2.putText(frame, f"Throttle: {throttle:.2f}", (10, h - 40),
                    self._font, self._font_scale, self._font_color, 2)
        cv2.putText(frame, f"Steering: {steering:.2f}", (10, h - 20),
                    self._font, self._font_scale, self._font_color, 2)
        
        return frame

    def show(self, frame: cv2.Mat) -> None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()
