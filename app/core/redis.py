import redis.asyncio as redis
from app.config import settings


redis_client = redis.from_url(settings.REDIS_URL)



async def set_refresh_token(email: str, token: str) -> None:
    await redis_client.set(f"refresh:{email}", token, ex=60*60*24*7)


async def get_refresh_token(email: str) -> str | None:
    value = await redis_client.get(f"refresh:{email}")
    if value:
        return value.decode("utf-8")
    return None


async def delete_refresh_token(email: str) -> None:
    await redis_client.delete(f"refresh:{email}")

#ttl = 5 min (5*60=300)
#key:   "cache:posts:page:1:page_size:20:sort_by:most_liked"
#value: '{"items": [{"id": 1, "body": "hi", "created_at": "2026-03-08T22:13:50", ...}], "total": 10, "page": 1, ...}'
async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    await redis_client.set(key, value, ex=ttl)

#Redis: b'{"items": [...]}'  ← bytes
#after decode: '{"items": [...]}'   ← str
#after json.loads: {"items": [...]} ← Python vocabulary
async def cache_get(key: str) -> str | None:
    value = await redis_client.get(key)
    if value:
        return value.decode("utf-8")
    return None


async def cache_pattern_delete(pattern: str) -> None:
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)

"""
async def cache_delete(key: str) -> None:
    await redis_client.delete(key)
"""