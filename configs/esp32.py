from __future__ import annotations

from dataclasses import dataclass 

@dataclass
class ESP32Config:

    host: str = "192.168.4.1"

    mjpeg_port: int = 81
    mjpeg_path: str = "/stream"

    ws_port: int = 80
    ws_path: str = "/ws"


    @property
    def stream_url(self):

        return (
            f"http://{self.host}:{self.mjpeg_port}{self.mjpeg_path}"
        )


    @property
    def ws_url(self):

        return (
            f"ws://{self.host}:{self.ws_port}{self.ws_path}"
        )
    