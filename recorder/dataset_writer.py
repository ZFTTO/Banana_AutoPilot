'''
-d = DatasetWriter()
-d.start()
-d.write()
-d.stop()
'''
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Optional

from recorder.utils import timestamp_iso, monotonic_time

logger = logging.getLogger(__name__)


class DatasetWriter:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._session_dir: Optional[Path] = None

        self._images_dir: Optional[Path] = None
        self._csv_file: Optional[object] = None
        self._csv_writer: Optional[csv.writer] = None

        self._start_mono: float = 0.0
        self._received_frame_count: int = 0
        self._recorded_frame_count: int = 0


    def start(self):
        self._received_frame_count = 0
        self._recorded_frame_count = 0
        self._start_mono = monotonic_time()

        self._root.mkdir(parents = True, exist_ok = True)

        session_num = 1
        while (self._root / f"session_{session_num:03d}").exists():
            session_num += 1
        self._session_dir = self._root / f"session_{session_num:03d}"
        self._session_dir.mkdir(parents = True, exist_ok = True)

        self._images_dir = self._session_dir / "images"
        self._images_dir.mkdir(parents = True, exist_ok = True)

        csv_path = self._session_dir / "labels.csv"
        self._csv_file = open(csv_path, "w", newline="")
        self._csv_writer = csv.writer(self._csv_file)
        self._csv_writer.writerow(["frame", "image", "timestamp", "throttle", "steering"])

        logger.info("Dataset session_%03d created at %s", session_num, self._session_dir)

    def stop(self):
        if self._session_dir is None:
            return

        if self._csv_file is not None:
            self._csv_file.close()
            self._csv_file = None
            self._csv_writer = None

        metadata = {
            "resolution": "QVGA (320x240)",
            "fps": "variable (every received frame)",
            "camera": "ESP32-S3 OV3660",
            "driver": "DRV8833 (H-Bridge) + MG90S Servo",
            "date": timestamp_iso(),
            "session_path": str(self._session_dir),
            "total_frames": self._recorded_frame_count,
        }
        metadata_path = self._session_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent = 2))

        logger.info("Dataset closed - %d frames", self._recorded_frame_count)
        self._session_dir = None

    def write(self, jpeg_bytes: bytes, throttle: float, steering: float, t: float | None = None) -> None:
        if self._session_dir is None or self._csv_writer is None:
            return

        if t is None:
            t = monotonic_time()

        self._received_frame_count += 1
        fname = f"{self._received_frame_count:06d}.jpg"
        img_path = self._images_dir / fname
        try:
            img_path.write_bytes(jpeg_bytes)
        except OSError as exc:
            logger.error("Failed to write image %s: %s", fname, exc)

        self._csv_writer.writerow([
            self._received_frame_count,
            fname,
            f"{t:.06f}",
            f"{throttle}",
            f"{steering}",
        ])

        self._recorded_frame_count += 1

    @property
    def frame_count(self) -> int:
        return self._recorded_frame_count

    @property
    def is_active(self) -> bool:
        return self._session_dir is not None

    @property
    def current_session_name(self) -> str:
        if self._session_dir is None:
            return ""
        return self._session_dir.name