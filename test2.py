from pathlib import Path

import cv2
import numpy as np
import pygame

from configs import RecorderConfig
from configs import ControllerConfig
from configs import ESP32Config

from recorder.overlay import Overlay
from recorder.utils import FpsCounter
from recorder.controller import Controller, create_controller
from recorder.camera_stream import CameraStream, jpeg_to_cv_mat
from recorder.websocket_client import WebsocketClient



import logging

import socket



logger = logger = logging.getLogger(__name__)


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
    print("-----------------------------")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect(("192.168.4.1", 81))
        print("connection success")
    except Exception as e:
        print("connection fail:", e)
    finally:
        s.close()
        print("finally close")
    
    print("-----------------------------")

    print(banner)

    overlay = Overlay()

    pygame.init()

    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("Banana AutoPilot")

    ctrlconfig = ControllerConfig(control_mode = "keyboard")
    ctrl = create_controller(ctrlconfig)

    esp32config = ESP32Config()
    stream = CameraStream(stream_url = esp32config.stream_url, queue_maxsize = 8)
    ws = WebsocketClient(ws_url = esp32config.ws_url, send_interval = 0.025)



    try:
        ctrl.start()
        running = True

        stream.start()
        ws.start()

        while running:

            state = ctrl.read()
            v = stream.get_frame(timeout=1)
            ws.send_control(throttle = state.throttle, steering = state.steering)

            if v is not None:
                frame = jpeg_to_cv_mat(v)
            else:
                frame = np.zeros((240, 320, 3), dtype=np.uint8)
            
            frame = overlay.draw(frame, session = "001", fps=30.0, recording=False, throttle=state.throttle, steering=state.steering)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))
            screen.blit(surface,(0,0))

            pygame.display.flip()

            if state.action == "toggle_exit" or state.action == "toggle_record":
                running = False

            

    finally:
        ctrl.stop()

        stream.stop()
        ws.stop()

        logger.info("kill controller source")




if __name__ == "__main__":
    main()
