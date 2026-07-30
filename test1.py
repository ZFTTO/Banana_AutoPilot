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
    f = FpsCounter()
    print(type(f))

    overlay = Overlay()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame = overlay.draw(frame, session = "001", fps=30.0, recording=False, throttle=0.75, steering=-0.2)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    pygame.init()

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Banana AutoPilot")
    surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))

    screen.blit(surface,(0,0))

    output_path = Path("output/display_test.png")
    output_path.parent.mkdir(exist_ok=True)
    saved = cv2.imwrite(str(output_path), frame)
    print(f"Overlay test saved to {output_path} ({saved})")

    config = RecorderConfig()
    print(config.esp32.stream_url)
    print(config.controller.keyboard.key_toggle_record)

    ctrlconfig = ControllerConfig(control_mode="keyboard")
    ctrl = create_controller(ctrlconfig)

    try:
        ctrl.start()
        running = True

        while running:
            state = ctrl.poll()
            print(state)

            if state.action == "toggle_exit" or state.action == "toggle_record":
                running = False

            

    finally:
        ctrl.stop()
        logger.info("kill controller source")




if __name__ == "__main__":
    main()
