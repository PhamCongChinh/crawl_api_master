from fastapi import APIRouter, BackgroundTasks, HTTPException
from confluent_kafka import Producer
from src.core.config import settings
from src.core.logging import logger
from src.kafka.service import send_to_kafka

producer = Producer({
    'bootstrap.servers': f"{settings.KAFKA_BROKER_HOST}:{settings.KAFKA_BROKER_PORT}"
})

router = APIRouter(prefix="/api/v1/posts", tags=["Post"])

@router.post("/insert-posts")
async def insert_posts_classified(request: dict, background_tasks: BackgroundTasks): # data là 1 list dict
    
    if not request.get("data"):
        raise HTTPException(status_code=400, detail="No data provided")

    try:
        # result = await PostService.insert_posts(items=request)
        # logging.info(f"Inserted classified posts: {result}")

        topic = settings.KAFKA_TOPIC_CLASSIFIED
        data = request.get("data", [])

        cleaned_data = []
        for item in data:
            if isinstance(item, dict):
                item.pop("server", None)  # xóa nếu có
                cleaned_data.append(item)

        background_tasks.add_task(send_to_kafka, topic, cleaned_data)

        return {"status": "OK", "detail": f"Sent to topic '{topic}'"}
    except Exception as e:
        logger.exception("Error in insert_posts_classified")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insert-unclassified-org-posts")
async def insert_posts_unclassified(request: dict, background_tasks: BackgroundTasks):

    if not request.get("data"):
        raise HTTPException(status_code=400, detail="No data provided")
    
    try:
        # result = await PostService.insert_unclassified_org_posts(items=request)
        # logging.info(f"Inserted unclassified org posts: {result}")

        topic = settings.KAFKA_TOPIC_UNCLASSIFIED
        data = request.get("data", [])

        items_with_server = [item for item in data if isinstance(item, dict) and "server" in item]
        if items_with_server:
            logger.warning(f"Found {len(items_with_server)} items containing 'server' field:")
            for i, item in enumerate(items_with_server, start=1):
                logger.warning(f"[{i}] server={item.get('server')} | auth_id={item.get('auth_id')} | url={item.get('url')}")

        cleaned_data = []
        for item in data:
            if isinstance(item, dict):
                item.pop("server", None)  # xóa nếu có
                cleaned_data.append(item)

        background_tasks.add_task(send_to_kafka, topic, cleaned_data)

        return {"status": "OK", "detail": f"Sent to topic '{topic}'"}
    except Exception as e:
        logger.exception("Error in insert_posts_unclassified")
        raise HTTPException(status_code=500, detail=str(e))