from pathlib import Path

import cv2
import numpy as np

from recorder.display import Overlay
from recorder.utils import FpsCounter

from configs import RecorderConfig


def main():
    f = FpsCounter()
    print(type(f))

    overlay = Overlay()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame = overlay.draw(frame, session = "001", fps=30.0, recording=True, throttle=0.75, steering=-0.2)

    output_path = Path("output/display_test.png")
    output_path.parent.mkdir(exist_ok=True)
    saved = cv2.imwrite(str(output_path), frame)
    print(f"Overlay test saved to {output_path} ({saved})")

    config = RecorderConfig()
    print(config.esp32.stream_url)
    print(config.controller.key_toggle_record)


if __name__ == "__main__":
    main()
