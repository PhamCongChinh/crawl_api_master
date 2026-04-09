import time

from src.core.redis_client import redis_client

def track_bot(data: dict):
    platform = data.get("crawl_source_code")  # tt, yt, web
    bot_id = data.get("crawl_bot")            # tiktok-1

    now = int(time.time())

    # ===== PLATFORM =====
    redis_client.set(f"bot:{platform}:last_seen", now, ex=300)

    redis_client.incr(f"bot:{platform}:count:1m")
    redis_client.expire(f"bot:{platform}:count:1m", 60)

    redis_client.incr(f"bot:{platform}:count:5m")
    redis_client.expire(f"bot:{platform}:count:5m", 300)

    # ===== BOT =====
    redis_client.set(f"bot:{platform}:{bot_id}:last_seen", now, ex=300)

    redis_client.incr(f"bot:{platform}:{bot_id}:count:1m")
    redis_client.expire(f"bot:{platform}:{bot_id}:count:1m", 60)

    redis_client.incr(f"bot:{platform}:{bot_id}:count:5m")
    redis_client.expire(f"bot:{platform}:{bot_id}:count:5m", 300)