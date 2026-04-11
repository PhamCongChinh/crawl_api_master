from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.core.config import settings
from src.core.logging import logger
from src.kafka.service import send_to_kafka
from src.utils.track_bot import track_bot

router = APIRouter(prefix="/api/v1/posts", tags=["Post"])


@router.post("/insert-posts")
async def insert_posts_classified(request: dict, background_tasks: BackgroundTasks):
    if not request.get("data"):
        raise HTTPException(status_code=400, detail="No data provided")

    try:
        topic = settings.KAFKA_TOPIC_CLASSIFIED  # fix: was KAFKA_TOPIC_UNCLASSIFIED
        data = request.get("data", [])
        background_tasks.add_task(send_to_kafka, topic, data)
        return {"status": "OK", "detail": f"Sent to topic '{topic}'"}
    except Exception as e:
        logger.exception("Error in insert_posts_classified")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insert-unclassified-org-posts")
async def insert_posts_unclassified(request: dict, background_tasks: BackgroundTasks):
    if not request.get("data"):
        raise HTTPException(status_code=400, detail="No data provided")

    try:
        topic = settings.KAFKA_TOPIC_UNCLASSIFIED
        data = request.get("data", [])

        if data:
            # background_tasks.add_task(track_bot, data)
            background_tasks.add_task(send_to_kafka, topic, data)

        return {"status": "OK", "detail": f"Sent to topic '{topic}'"}
    except Exception as e:
        logger.exception("Error in insert_posts_unclassified")
        raise HTTPException(status_code=500, detail=str(e))