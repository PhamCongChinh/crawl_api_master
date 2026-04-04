from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.core.config import settings
from src.core.logging import logger
from confluent_kafka.admin import AdminClient
from confluent_kafka import Producer

KAFKA_BOOTSTRAP_SERVERS = f"{settings.KAFKA_BROKER_HOST}:{settings.KAFKA_BROKER_PORT}"
# --- Kafka clients -------------------------------------------------
admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

router = APIRouter(prefix="/api/v1/check", tags=["Check"])

@router.get("/health")
async def check_health():
    return {
        "status" : "OK"
    }

@router.get("/health/kafka")
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