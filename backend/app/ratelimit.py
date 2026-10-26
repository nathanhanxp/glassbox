"""Tiny async token bucket. Defaults are placeholders until the consoles are checked."""

import asyncio
import time


class RateLimiter:
    def __init__(self, rpm: int):
        self.interval = 60.0 / max(rpm, 1)
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            delay = self._next - now
            if delay > 0:
                await asyncio.sleep(delay)
                now = time.monotonic()
            self._next = max(self._next, now) + self.interval
