'''
-s = CameraStream
-s.start()
-s.get_frame()
-s.stop()
-jpeg_to_cv_mat(jpeg_bytes: bytes) -> np.ndarray | None
'''
from __future__ import annotations

import logging
import threading
import urllib.request
from queue import Full, Empty, Queue
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

class CameraStream:
    def __init__(self, stream_url: str, queue_maxsize: int = 8) -> None:
        self._url = stream_url
        self._queue: Queue[Optional[bytes]] = Queue(maxsize = queue_maxsize)

        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()

        self._stream = None

    def start(self) -> None:
        if self._running.is_set():
            return
        self._running.set()
        self._thread = threading.Thread(target = self._poll, daemon = True)
        self._thread.start()
        logger.info("CameraStream started: %s", self._url)

    def stop(self) -> None:
        self._running.clear()

        if self._stream is not None:
            self._stream.close()

        if self._thread is not None:
            self._thread.join(timeout = 2.0)
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except Exception:
                    break

        logger.info("CameraStream stopped")

    def get_frame(self, timeout: float | None = 0.5) -> bytes | None:
        try: 
            return self._queue.get(timeout = timeout)
        except Empty:
            return None

        

    def flush(self) -> None:
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Empty:
                break
        

    @property
    def is_running(self) -> bool:
        return self._running.is_set()

    def _poll(self) -> None:
        try:
            self._stream = urllib.request.urlopen(self._url, timeout = 5.0)
        except (urllib.error.URLError, OSError) as exc:
            logger.error("Cannot open stream url: %s", exc)
            self._running.clear()
            return
        
        boundary = b"--frame"
        buf = b""

        while self._running.is_set():
            try:
                chunk = self._stream.read(8192)
            except Exception as exc:
                logger.warning("Stream read error: %s", exc)
                break

            if not chunk:
                break

            buf += chunk

            while True:
                '''
                --frame\r\n
                Content-Type: image/jpeg\r\n
                Content-Length: 45678\r\n
                \r\n          ← header end
                [JPG bin bytes]
                \r\n
                --frame\r\n
                next frame ……
                '''

                b = buf.find(boundary)
                if b < 0:
                    break

                header_end = buf.find(b"\r\n\r\n", b)
                if header_end < 0:
                    break

                payload_start = header_end + 4

                next_b = buf.find(boundary, payload_start)
                if next_b < 0:
                    break

                jpeg_bytes = buf[payload_start: next_b].rstrip(b"\r\n")
                buf = buf[next_b: ]

                if jpeg_bytes:
                    try:
                        self._queue.put_nowait(jpeg_bytes)
                    
                    except Full:
                        self._queue.get_nowait()
                        self._queue.put_nowait(jpeg_bytes)

        # leave while loop, close stream and clear running flag      
        self._stream.close()
        self._running.clear()

def jpeg_to_cv_mat(jpeg_bytes: bytes) -> np.ndarray | None:
    if jpeg_bytes is None or len(jpeg_bytes) == 0:
        return None
    arr = np.frombuffer(jpeg_bytes, dtype = np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)
