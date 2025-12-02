import asyncio
from typing import List, Optional

class KeyManager:
    def __init__(self, keys: List[str]):
        self.keys = [{"key": k, "status": "ok"} for k in keys]
        self.index = 0
        self.lock = asyncio.Lock()

    async def get_current(self) -> Optional[str]:
        async with self.lock:
            if not self.keys:
                return None
            n = len(self.keys)
            for i in range(n):
                idx = (self.index + i) % n
                if self.keys[idx]["status"] == "ok":
                    self.index = idx
                    return self.keys[idx]["key"]
            return None

    async def rotate_to_next(self):
        async with self.lock:
            n = len(self.keys)
            for i in range(1, n + 1):
                idx = (self.index + i) % n
                if self.keys[idx]["status"] == "ok":
                    self.index = idx
                    return self.keys[idx]["key"]
            return None

    async def mark_blocked(self, key: str):
        async with self.lock:
            for k in self.keys:
                if k["key"] == key:
                    k["status"] = "blocked"
                    break