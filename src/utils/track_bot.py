import time

from src.core.redis_client import redis_client

async def track_bot(data):
    if isinstance(data, list):
        for item in data:
            await _track_single(item)
    else:
        await _track_single(data)


async def _track_single(data: dict):
    platform = data.get("crawl_source_code")
    bot_id = data.get("crawl_bot", "default")

    if not platform:
        return  # tránh rác key

    now = int(time.time())

    pipe = redis_client.pipeline()

    # ===== PLATFORM =====
    pipe.set(f"bot:{platform}:last_seen", now, ex=300)

    pipe.incr(f"bot:{platform}:count:1m")
    pipe.expire(f"bot:{platform}:count:1m", 60, nx=True)

    pipe.incr(f"bot:{platform}:count:5m")
    pipe.expire(f"bot:{platform}:count:5m", 300, nx=True)

    # ===== BOT =====
    pipe.set(f"bot:{platform}:{bot_id}:last_seen", now, ex=300)

    pipe.incr(f"bot:{platform}:{bot_id}:count:1m")
    pipe.expire(f"bot:{platform}:{bot_id}:count:1m", 60, nx=True)

    pipe.incr(f"bot:{platform}:{bot_id}:count:5m")
    pipe.expire(f"bot:{platform}:{bot_id}:count:5m", 300, nx=True)

    await pipe.execute()