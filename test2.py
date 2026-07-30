from pathlib import Path

import cv2
import numpy as np
import pygame

from configs import RecorderConfig
from configs import ControllerConfig

from recorder.overlay import Overlay
from recorder.utils import FpsCounter
from recorder.controller import Controller, create_controller


import logging

logger = logger = logging.getLogger(__name__)



def main():




    overlay = Overlay()

    pygame.init()

    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("Banana AutoPilot")



    ctrlconfig = ControllerConfig(control_mode="switch")
    ctrl = create_controller(ctrlconfig)

    try:
        ctrl.start()
        running = True

        while running:


            
            state = ctrl.poll()

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
        logger.info("kill controller source")




if __name__ == "__main__":
    main()
