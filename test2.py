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



import logging

import socket



logger = logger = logging.getLogger(__name__)



def main():
    print("-----------------------------")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("192.168.4.1", 81))
        print("success")
    except Exception as e:
        print("fail", e)
    finally:
        s.close()
    
    print("-----------------------------")


    overlay = Overlay()

    pygame.init()

    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("Banana AutoPilot")



    ctrlconfig = ControllerConfig(control_mode = "keyboard")
    ctrl = create_controller(ctrlconfig)

    esp32config = ESP32Config()
    
    stream = CameraStream(stream_url = "http://192.168.4.1:81/stream", queue_maxsize = 8)



    try:
        ctrl.start()
        running = True

        stream.start()

        while running:


            
            state = ctrl.poll()
            v = stream.get_frame(timeout=1)
            try:
                frame = jpeg_to_cv_mat(v)
            except:
                frame = np.zeros((240, 320, 3), dtype=np.uint8)
            ''''''
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
        logger.info("kill controller source")




if __name__ == "__main__":
    main()
