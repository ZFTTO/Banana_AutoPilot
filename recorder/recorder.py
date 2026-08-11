'''
MAYBE DONT NEED RECOREDER CLASS NOW >.<
'''

from __future__ import annotations

import cv2
import numpy as np
import pygame
from torch.mtia import snapshot

from configs import RecorderConfig
from configs import ControllerConfig
from configs import ESP32Config

from recorder import Controller, create_controller
from recorder import CameraStream, jpeg_to_cv_mat
from recorder import WebsocketClient 
from recorder import DatasetWriter
from recorder import Overlay
from recorder import FpsCounter, timestamp_iso, monotonic_time

import logging

logger = logging.getLogger(__name__)

class Recorder:
    def __init__(self, controller: Controller, camera_stream: CameraStream, websocket_client: WebsocketClient
                 , dataset_writer: DatasetWriter):
        self._running = False


        self._controller = controller
        self._camera_stream = camera_stream
        self._websocket_client = websocket_client
        self._dataset_writer = dataset_writer

    def run(self) -> None:
        self._running = True

        pygame.init()
        pygame.display.set_mode((320, 240))
        pygame.display.set_caption("Banana AutoPilot")

        try:
            self._controller.start()
            self._camera_stream.start()
            self._websocket_client.start()
            logger.info("Recoder started")

            while self._running:
                self._step()

        finally:
            self._controller.stop()
            self._camera_stream.stop()
            self._websocket_client.stop()

            pygame.quit()
            logger.info("Recorder stopped")

    def _step(self):
        state = self._controller.read()

        if state.action == "toggle_exit":
            self._running = False
            return

        if state.action == "toggle_record":
            pass

        self._websocket_client.send_control(throttle = state.throttle, steering = state.steering)

        jpeg_bytes = self._camera_stream.get_frame()
        if jpeg_bytes:
            frame = jpeg_to_cv_mat(jpeg_bytes)
        else:
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
        #frame = overlay.draw(frame, )




        self._dataset_writer.start()
        self._dataset_writer.stop()
        

