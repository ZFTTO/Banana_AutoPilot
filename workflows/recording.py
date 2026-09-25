from __future__ import annotations

import numpy as np
import pygame

from configs.recorder import RecorderConfig
from configs.controller import ControllerConfig
from configs.esp32 import ESP32Config

from core.controller import create_controller
from core.camera_stream import CameraStream, jpeg_to_cv_mat
from core.websocket_client import WebsocketClient 
from core.dataset_writer import DatasetWriter
from core.display import Display

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

    ctrl_config = ControllerConfig(control_mode = "keyboard")
    ctrl = create_controller(ctrl_config)

    esp32_config = ESP32Config()
    camera = CameraStream(stream_url = esp32_config.stream_url, queue_maxsize = 8)
    vehicle = WebsocketClient(ws_url = esp32_config.ws_url, send_interval = 0.025)

    recd_config = RecorderConfig()
    dataset_writer = DatasetWriter(root = recd_config.dataset_root)

    display = Display()

    recording = False

    try:
        display.start()
        ctrl.start()
        camera.start()
        vehicle.start()
        logger.info("start ctrl, camera, vehicle")

        while True:
            state = ctrl.read()
            command = state.command

            if state.action == "toggle_exit":
                break

            if state.action == "toggle_record":
                if recording:
                    dataset_writer.stop()
                    recording = False
                    logger.info("stop recording")
                else:
                    dataset_writer.start()
                    recording = True
                    logger.info("start recording")

            # Send the driving command before waiting for a camera frame.
            vehicle.send_control(
                throttle=command.throttle,
                steering=command.steering,
            )

            jpeg_bytes = camera.get_frame(timeout=0.2)
            frame = jpeg_to_cv_mat(jpeg_bytes) if jpeg_bytes else None

            # Record only successfully decoded frames.
            if recording and frame is not None:
                dataset_writer.write(
                    jpeg_bytes=jpeg_bytes,
                    throttle=command.throttle,
                    steering=command.steering,
                )

            # Use a blank frame for display when no valid image is available.
            if frame is None:
                frame = np.zeros((240, 320, 3), dtype=np.uint8)

            frame = display.draw(frame, session = dataset_writer.current_session_name, fps = 30.0,
                                 recording = recording, throttle = command.throttle, steering = command.steering,)
            display.show(frame)

    finally:
        dataset_writer.stop()
        ctrl.stop()
        camera.stop()
        vehicle.stop()
        pygame.quit()
        
        logger.info("stop ctrl, camera, vehicle")


if __name__ == "__main__":
    main()
