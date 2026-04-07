from __future__ import annotations

from dataclasses import dataclass

import redis


@dataclass(frozen=True)
class RedisCache:
    redis: redis.Redis
    prefix: str = "summary:"

    def get_summary(self, content_hash: str) -> str | None:
        value = self.redis.get(self.prefix + content_hash)
        if value is None:
            return None
        return value.decode("utf-8")

    def set_summary(self, content_hash: str, summary: str) -> None:
        self.redis.set(self.prefix + content_hash, summary)


def get_cache(redis_url: str) -> RedisCache:
    r = redis.Redis.from_url(redis_url)
    return RedisCache(redis=r)

