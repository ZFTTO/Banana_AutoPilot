'''
-ws.start()
-ws.send_control()
-ws.get_telemetry()
-ws.stop()
'''
from __future__ import annotations

import json
import logging
import threading
import time
from queue import Empty, Full, Queue
from typing import Any, Optional

import websocket

logger = logging.getLogger(__name__)

class WebsocketClient:
    def __init__(self, ws_url: str, send_interval: float = 0.025) -> None:
        self._url = ws_url
        self._send_interval = send_interval

        self._queue: Queue[str] = Queue(maxsize = 1)

        self._telemetry: Optional[dict[str, Any]] = None
        self._telemetry_lock = threading.Lock()

        self._ws: Optional[websocket.WebSocket] = None

        self._thread: Optional[threading.Thread] = None

        self._running = threading.Event()
        self._connected = False

    def start(self) -> None:
        if self._running.is_set():
            return

        self._running.set()
        self._thread = threading.Thread(target = self._poll, daemon = True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()

        if self._ws is not None:
            self._ws.close()

        if self._thread is not None:
            self._thread.join(timeout = 2.0)

    def send_control(self, throttle: float, steering: float) -> None:
        control_data = f"{throttle:.2f} {steering:.2f}"

        try:
            self._queue.put_nowait(control_data)

        except Full:
            try: 
                self._queue.get_nowait()
            except Empty:
                pass
            self._queue.put_nowait(control_data)

    def get_telemetry(self) -> dict[str, Any] | None:
        with self._telemetry_lock:
            if self._telemetry is None:
                return None

            return self._telemetry.copy()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _poll(self) -> None: 
        while self._running.is_set():
            try:
                logger.info("Connecting to WebSocket server: %s", self._url)
                self._ws = websocket.create_connection(self._url, timeout = 5.0)

                self._connected = True
                logger.info("WebSocket connected.")

                self._ws.settimeout(0.01)

                while self._running.is_set():
                    try:
                        msg = self._queue.get_nowait()
                        self._ws.send(msg)

                    except Empty:
                        pass

                    try:
                        response = self._ws.recv()

                        if response:
                            response_data = json.loads(response)

                            with self._telemetry_lock:
                                self._telemetry = response_data

                    except websocket.WebSocketTimeoutException:
                        pass

                    time.sleep(self._send_interval)
                        
            except Exception as e:
                logger.error("WebSocket connection error: %s", e)

            finally:
                self._connected = False

                if self._ws is not None:
                    self._ws.close()
                    self._ws = None


            if self._running.is_set():
                logger.info("Reconnecting to WebSocket server in 2 seconds...")
                time.sleep(2.0)
