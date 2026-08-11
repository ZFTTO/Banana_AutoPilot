from __future__ import annotations

import cv2
import numpy as np
import pygame
from torch.mtia import snapshot

from configs.recorder import RecorderConfig
from configs.controller import ControllerConfig
from configs.esp32 import ESP32Config

from recorder.controller import Controller, create_controller
from recorder.camera_stream import CameraStream, jpeg_to_cv_mat
from recorder.websocket_client import WebsocketClient 
from recorder.dataset_writer import DatasetWriter
from recorder.overlay import Overlay
from recorder.utils import FpsCounter, timestamp_iso, monotonic_time

import logging

logger = logging.getLogger(__name__)

banner = r"""
  _______   ________   ___   __    ________   ___   __    ________
/_______/\ /_______/\ /__/\ /__/\ /_______/\ /__/\ /__/\ /_______/\
\::: _  \ \\::: _  \ \\::`_\\  \ \\::: _  \ \\::`_\\  \ \\::: _  \ \
 \::\_\  \/_\::\_\  \ \\:. `-\  \ \\::\_\  \ \\:. `-\  \ \\::\_\  \ \
  \::  _  \ \\:: __  \ \\:. _    \ \\:: __  \ \\:. _    \ \\:: __  \ \
   \::\_\  \ \\:.\ \  \ \\. \`-\  \ \\:.\ \  \ \\. \`-\  \ \\:.\ \  \ \
 ___\_______\/ \__\/\__\/_\__\/ `__\/_\__\/\__\/ \__\/_`__\/_\__\/\__\/____   _________
/_______/\ /_/\/_/\ /________/\/_____/\ /_____/\ /_______/\/_/\     /_____/\ /________/\
\::: _  \ \\:\ \:\ \\__.::.__\/\:::_ \ \\:::_ \ \\__.::._\/\:\ \    \:::_ \ \\__.::.__\/
 \::\_\  \ \\:\ \:\ \  \::\ \   \:\ \ \ \\:\_\ \ \  \::\ \  \:\ \    \:\ \ \ \  \::\ \
  \:: __  \ \\:\ \:\ \  \::\ \   \:\ \ \ \\: ___\/  _\::\ \__\:\ \____\:\ \ \ \  \::\ \
   \:.\ \  \ \\:\_\:\ \  \::\ \   \:\_\ \ \\ \ \   /__\::\__/\\:\/___/\\:\_\ \ \  \::\ \
    \__\/\__\/ \_____\/   \__\/    \_____\/ \_\/   \________\/ \_____\/ \_____\/   \__\/
"""

def main():
    print(banner)

    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("Banana AutoPilot")

    ctrl_config = ControllerConfig(control_mode = "switch")
    ctrl = create_controller(ctrl_config)

    esp32_config = ESP32Config()
    stream = CameraStream(stream_url = esp32_config.stream_url, queue_maxsize = 8)
    ws = WebsocketClient(ws_url = esp32_config.ws_url, send_interval = 0.025)

    recd_config = RecorderConfig()
    dswtr = DatasetWriter(root = recd_config.dataset_root)

    overlay = Overlay()

    running = False
    recording = False

    try:
        ctrl.start()
        stream.start()
        ws.start()
        logger.info("start ctrl, stream, ws")

        running = True
        while running:
            state = ctrl.read()
            print(recording)

            if state.action == "toggle_exit":
                running = False
                break

            if state.action == "toggle_record":
                recording = not recording
                if recording:
                    dswtr.start()
                    logger.info("start recording")
                else:
                    dswtr.stop()
                    logger.info("stop recording")

            jpeg_bytes = stream.get_frame(timeout = 0.2)
            if jpeg_bytes:
                frame = jpeg_to_cv_mat(jpeg_bytes)
            else:
                frame = np.zeros((240, 320, 3), dtype = np.uint8)

            ws.send_control(throttle = state.throttle,steering = state.steering)
            telemetry = ws.get_telemetry()

            if recording:
                dswtr.write(jpeg_bytes = jpeg_bytes, 
                            throttle = state.throttle, steering = state.steering, t = None)

            frame = overlay.draw(frame, session = dswtr.current_session_name, fps = 30.0,
                                 recording = recording, throttle = state.throttle, steering = state.steering,)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(surface, (0, 0))
            pygame.display.flip()

    finally:
        ctrl.stop()
        stream.stop()
        ws.stop()
        logger.info("stop ctrl, stream, ws")


if __name__ == "__main__":
    main()
