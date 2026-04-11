import time

from src.core.redis_client import redis_client

async def check_platform(platform):
    now = int(time.time())

    last_seen = await redis_client.get(f"bot:{platform}:last_seen")
    count_raw = await redis_client.get(f"bot:{platform}:count:time")
    count_time = int(count_raw or 0)

    if not last_seen:
        return "dead"
    if now - int(last_seen) > 7200:
        return "dead"
    if count_time == 0:
        return "stuck"
    return "healthy"


async def check_bot(platform, bot_id):
    now = int(time.time())

    last_seen = await redis_client.get(f"bot:{platform}:{bot_id}:last_seen")
    count_raw = await redis_client.get(f"bot:{platform}:{bot_id}:count:time")
    count_time = int(count_raw or 0)

    if not last_seen:
        return "dead"
    if now - int(last_seen) > 7200:
        return "dead"
    if count_time == 0:
        return "stuck"
    return "healthy"