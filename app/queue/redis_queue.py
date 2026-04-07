from __future__ import annotations

from dataclasses import dataclass

import redis


@dataclass(frozen=True)
class RedisQueue:
    redis: redis.Redis
    key: str

    def push(self, item: str) -> None:
        self.redis.lpush(self.key, item)

    def pop_blocking(self, *, timeout_seconds: int = 5) -> str | None:
        result = self.redis.brpop(self.key, timeout=timeout_seconds)
        if result is None:
            return None
        _, item = result
        return item.decode("utf-8")


def get_queue(redis_url: str, *, key: str = "jobs:queue") -> RedisQueue:
    r = redis.Redis.from_url(redis_url)
    return RedisQueue(redis=r, key=key)

