from fastapi import FastAPI
import uvicorn
from src.core.redis_client import ping_redis, redis_client
from src.core.config import settings
from src.api import router_post, router_checkhealth

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
        last_seen = redis_client.get(f"bot:tt:last_seen")
        count_5m = int(redis_client.get(f"bot:tt:count:5m") or 0)
        print(last_seen)
        print(count_5m)
        return {
            "status": "healthy" if res else "unhealthy"
        }
    except Exception as e:
        return {
            "status": "dead",
            "error": str(e)
        }