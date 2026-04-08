from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.model.botheart import BotHealth
from src.core.config import settings
from src.core.logging import logger
from confluent_kafka.admin import AdminClient
from confluent_kafka import Producer
from src.core.mongo import db
import psutil

KAFKA_BOOTSTRAP_SERVERS = f"{settings.KAFKA_BROKER_HOST}:{settings.KAFKA_BROKER_PORT}"
# --- Kafka clients -------------------------------------------------
admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

router = APIRouter(prefix="/api/v1/check", tags=["Check"])

# Heartbeat
@router.post("/heartbeat")
async def check_heartbeat(data: dict):
    now = datetime.now(timezone.utc)
    bot_id = data.get("bot_id")
    bot_name = data.get("bot_name")
    bot_type = data.get("bot_type")
    records = data.get("records", 0)

    collection = db["tiktok_bot_configs"]

    if not bot_id:
        return {"error": "bot_id is required"}

    bot = await collection.find_one({"bot_id": bot_id})

    print(bot)

    if not bot:
        # insert mới
        doc = {
            "bot_id": bot_id,
            "bot_type": bot_type,
            "last_ping": now,
            "last_data_time": now if records > 0 else None,
            "status": "alive"
        }
        await collection.insert_one(doc)

    else:
        # update
        update_data = {
            "last_ping": now,
            "status": "alive"
        }

        if records > 0:
            update_data["last_data_time"] = now

        await collection.update_one(
            {"bot_id": bot_id},
            {"$set": update_data}
        )

    return {"status": "ok"}

@router.get("/server")
async def system_health():
    # %CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    # RAM
    memory = psutil.virtual_memory()
    # Disk
    disk = psutil.disk_usage('/')

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),

        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count()
        },

        "memory": {
            "total": round(memory.total / (1024**3), 2),   # GB
            "used": round(memory.used / (1024**3), 2),
            "free": round(memory.available / (1024**3), 2),
            "percent": memory.percent
        },

        "disk": {
            "total": round(disk.total / (1024**3), 2),
            "used": round(disk.used / (1024**3), 2),
            "free": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }
    }

@router.get("/health")
async def check_health():
    return {
        "status" : "OK"
    }

@router.get("/kafka")
async def check_kafka():
    try:
        # gọi metadata từ Kafka
        metadata = admin.list_topics(timeout=3)

        # nếu có broker là OK
        brokers = metadata.brokers

        if not brokers:
            return {
                "status": "DOWN",
                "detail": "No brokers found"
            }

        return {
            "status": "UP",
            "brokers": len(brokers),
            "topics": len(metadata.topics)
        }

    except Exception as e:
        return {
            "status": "DOWN",
            "error": str(e)
        }
    
@router.get("/data-volume")
async def data_volume():
    try:
        now = datetime.now(timezone.utc)

        t_1m = now - timedelta(minutes=10)
        t_5m = now - timedelta(minutes=60)

        records_1m = await db.sls_not_spam_posts.count_documents({
            "createdAt": {"$gte": t_1m}
        })

        records_5m = await db.sls_not_spam_posts.count_documents({
            "createdAt": {"$gte": t_5m}
        })

        # logic health
        status = "healthy"
        if records_1m < 50:
            status = "low"
        if records_1m == 0:
            status = "down"

        return {
            "records_1m": records_1m,
            "records_5m": records_5m,
            "status": status
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }