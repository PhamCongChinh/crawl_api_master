import time
import psutil
from datetime import datetime, timedelta, timezone

import asyncio
from fastapi import APIRouter
from src.core.config import settings
from src.core.logging import logger
from src.core.mongo import db
from src.kafka.service import admin

router = APIRouter(prefix="/api/v1/check", tags=["Check"])


@router.post("/heartbeat")
async def check_heartbeat(data: dict):
    bot_id = data.get("bot_id")
    if not bot_id:
        return {"error": "bot_id is required"}

    now_unix = int(time.time())
    records = data.get("records", 0)
    collection = db["bots_health"]
    bot = await collection.find_one({"bot_id": bot_id})

    if not bot:
        await collection.insert_one({
            "bot_id": bot_id,
            "bot_name": data.get("bot_name"),
            "bot_type": data.get("bot_type"),
            "last_ping": now_unix,
            "last_data_time": now_unix if records > 0 else None,
            "status": "alive",
        })
    else:
        update = {"last_ping": now_unix, "status": "alive"}
        if records > 0:
            update["last_data_time"] = now_unix
        await collection.update_one({"bot_id": bot_id}, {"$set": update})

    return {"status": "ok"}


@router.get("/bot-health")
async def check_bot_health():
    collection = db["bots_health"]
    bots = await collection.find().to_list(length=200)
    now_unix = int(time.time())

    result = []
    for b in bots:
        last_ping = b.get("last_ping", 0)
        status = "dead" if (now_unix - last_ping) > 90 else "alive"
        result.append({
            "bot_id": b.get("bot_id"),
            "bot_name": b.get("bot_name"),
            "bot_type": b.get("bot_type"),
            "status": status,
        })

    return result  # fix: moved outside the for loop


@router.get("/server")
async def system_health():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "cpu": {"percent": cpu_percent, "cores": psutil.cpu_count()},
        "memory": {
            "total": round(memory.total / (1024 ** 3), 2),
            "used": round(memory.used / (1024 ** 3), 2),
            "free": round(memory.available / (1024 ** 3), 2),
            "percent": memory.percent,
        },
        "disk": {
            "total": round(disk.total / (1024 ** 3), 2),
            "used": round(disk.used / (1024 ** 3), 2),
            "free": round(disk.free / (1024 ** 3), 2),
            "percent": disk.percent,
        },
    }


@router.get("/health")
async def check_health():
    return {"status": "OK"}


@router.get("/kafka")
async def check_kafka():
    try:
        metadata = admin.list_topics(timeout=3)
        brokers = metadata.brokers
        if not brokers:
            return {"status": "DOWN", "detail": "No brokers found"}
        return {"status": "UP", "brokers": len(brokers), "topics": len(metadata.topics)}
    except Exception as e:
        return {"status": "DOWN", "error": str(e)}


@router.get("/data-volume")
async def data_volume():
    try:
        now = datetime.now(timezone.utc)
        t_10m = now - timedelta(minutes=10)
        t_60m = now - timedelta(minutes=60)

        records_10m, records_60m = await asyncio.gather(
            db.sls_not_spam_posts.count_documents({"createdAt": {"$gte": t_10m}}),
            db.sls_not_spam_posts.count_documents({"createdAt": {"$gte": t_60m}}),
        )

        if records_10m == 0:
            status = "down"
        elif records_10m < 50:
            status = "low"
        else:
            status = "healthy"

        return {"records_10m": records_10m, "records_60m": records_60m, "status": status}
    except Exception as e:
        return {"status": "error", "error": str(e)}
