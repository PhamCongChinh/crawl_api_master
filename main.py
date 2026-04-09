import asyncio
import time

from fastapi import FastAPI
import uvicorn
from src.core.redis_client import ping_redis, redis_client
from src.core.config import settings
from src.api import router_post, router_checkhealth
from src.utils.check_bot import check_bot, check_platform

app = FastAPI()

app.include_router(router_post)
app.include_router(router_checkhealth)

def main():
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=False, access_log=False)

if __name__ == "__main__":
    main()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health/redis")
async def check_redis():
    try:
        res = await ping_redis()
        last_seen = await redis_client.get(f"bot:tt:last_seen")
        count_time = await (redis_client.get(f"bot:tt:count:time") or 0)
        return {
            "status": "healthy" if res else "unhealthy",
            "tiktok_last_seen": last_seen,
            "tiktok_count": count_time
        }
    except Exception as e:
        return {
            "status": "dead",
            "error": str(e)
        }
    
@app.get("/bot-health")
async def bot_health():
    platforms = ["tt", "yt", "web", "fb"]

    async def get_platform_data(p):
        last_seen, count = await asyncio.gather(
            redis_client.get(f"bot:{p}:last_seen"),
            redis_client.get(f"bot:{p}:count:time")
        )

        if not last_seen:
            status = "die"
        else:
            delay = int(time.time()) - int(last_seen)
            status = "delay" if delay > 7200 else "ok"

        return {
            "platform": p,
            "status": status,
            "records": int(count or 0)
        }

    result = await asyncio.gather(
        *[get_platform_data(p) for p in platforms]
    )

    return result