from fastapi import APIRouter, BackgroundTasks, HTTPException
# from confluent_kafka import Producer
from src.service.post import PostService
from src.core.config import settings
from src.core.logging import logger
from src.kafka.service import send_to_kafka_test, send_to_kafka_live

# producer = Producer({
#     'bootstrap.servers': f"{settings.KAFKA_BROKER_HOST}:{settings.KAFKA_BROKER_PORT}"
# })

router = APIRouter(prefix="/api/v1/posts", tags=["Post"])

@router.post("/insert-posts")
async def insert_posts_classified(request: dict, background_tasks: BackgroundTasks): # data là 1 list dict
    
    if not request.get("data"):
        raise HTTPException(status_code=400, detail="No data provided")

    try:
        result = await PostService.insert_posts(items=request)
        logger.info(f"Inserted classified posts: {result}")

        topic_test = settings.KAFKA_TOPIC_UNCLASSIFIED_TEST
        topic_live = settings.KAFKA_TOPIC_UNCLASSIFIED_LIVE
        data = request.get("data", [])

        cleaned_data = []
        for item in data:
            if isinstance(item, dict):
                item.pop("server", None)  # xóa nếu có
                cleaned_data.append(item)

        background_tasks.add_task(send_to_kafka_test, topic_test, cleaned_data)

        return {"status": "OK", "detail": f"Sent to topic '{topic_test}'"}
    except Exception as e:
        logger.exception("Error in insert_posts_classified")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insert-unclassified-org-posts")
async def insert_posts_unclassified(request: dict, background_tasks: BackgroundTasks):

    if not request.get("data"):
        raise HTTPException(status_code=400, detail="No data provided")
    
    try:
        result = await PostService.insert_unclassified_org_posts(items=request)
        logger.info(f"Inserted unclassified org posts: {result}")

        topic_test = settings.KAFKA_TOPIC_UNCLASSIFIED_TEST
        topic_live = settings.KAFKA_TOPIC_UNCLASSIFIED_LIVE

        data = request.get("data", []) # return list<dict>

        items_with_server = [item for item in data if isinstance(item, dict) and "server" in item]
        if items_with_server:
            logger.warning(f"Found {len(items_with_server)} items containing 'server' field:")
            for i, item in enumerate(items_with_server, start=1):
                logger.warning(f"[{i}] [{item.get('server')}] | {item.get('url')}")

        # cleaned_data = []
        # for item in data:
        #     if isinstance(item, dict):
        #         item.pop("server", None)  # xóa nếu có
        #         cleaned_data.append(item)

        # background_tasks.add_task(send_to_kafka, topic, cleaned_data)

        data_test = []
        data_live = []
        for item in data:
            if not isinstance(item, dict):
                continue

            server = item.get("server")
            item.pop("server", None)

            if server == "server_test":
                data_test.append(item)
            elif server == "server_live":
                data_live.append(item)
        
        if len(data_test) > 0:
            background_tasks.add_task(send_to_kafka_test, topic_test, data_test)
            return {"status": "OK", "detail": f"Sent to topic '{topic_test}'"}

        if len(data_live) > 0:
            background_tasks.add_task(send_to_kafka_live, topic_live, data_live)
            return {"status": "OK", "detail": f"Sent to topic '{topic_live}'"}

    except Exception as e:
        logger.exception("Error in insert_posts_unclassified")
        raise HTTPException(status_code=500, detail=str(e))