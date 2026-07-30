from __future__ import annotations

import json
import logging
import threading
import time
from queue import Empty, Full, Queue
from typing import Optional

import websocket

logger = logging.getLogger(__name__)

class WebsocketClient:
    def __init__(self, ws_url: str, send_interval: float = 0.025) -> None:
        self._url = ws_url
        self._send_interval = send_interval
        self._queue: Queue[str] = Queue(maxsize = 1)
        self._telemetry: list[Optional[float]] = None
        self._lock = 


    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def send_control(self) -> None:
        pass

    def get_telemetry(self) -> None:
        pass

    @property
    def is_connnected(self) -> bool:
        pass

    def _poll(self) -> None: 
        pass

