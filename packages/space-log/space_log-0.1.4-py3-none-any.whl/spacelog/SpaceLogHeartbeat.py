from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from spacelog.SpaceLogClient import SpaceLogClient


class SpaceLogHeartbeat:
    def __init__(self, client: SpaceLogClient, interval: float):
        self.client = client
        self.interval = interval

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread is not None:
            self._stop_event.set()

    def _loop(self):
        self.client.send_ping()
        while not self._stop_event.is_set():
            time.sleep(self.interval)
            self.client.send_ping()
