from fastapi import APIRouter, BackgroundTasks, HTTPException
# from src.service.post import PostService
from src.core.config import settings
from src.core.logging import logger
from src.kafka.service import send_to_kafka
from src.utils import track_bot

router = APIRouter(prefix="/api/v1/posts", tags=["Post"])

@router.post("/insert-posts")
async def insert_posts_classified(request: dict, background_tasks: BackgroundTasks): # data là 1 list dict
    
    if not request.get("data"):
        raise HTTPException(status_code=400, detail="No data provided")

    try:
        # result = await PostService.insert_posts(items=request)
        # logger.info(f"Inserted classified posts: {result}")

        topic = settings.KAFKA_TOPIC_UNCLASSIFIED
        data = request.get("data", [])

        # cleaned_data = []
        # for item in data:
        #     if isinstance(item, dict):
        #         item.pop("server", None)  # xóa nếu có
        #         cleaned_data.append(item)

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
        # result = await PostService.insert_unclassified_org_posts(items=request)
        # logger.info(f"Inserted unclassified org posts: {result}")

        topic = settings.KAFKA_TOPIC_UNCLASSIFIED
        data = request.get("data", []) # return list<dict>

        await track_bot.track_bot(data)

        # cleaned_data = []
        # for item in data:
        #     if isinstance(item, dict):
        #         item.pop("server", None)  # xóa nếu có
        #         cleaned_data.append(item)

        # background_tasks.add_task(send_to_kafka, topic, cleaned_data)

        if len(data) > 0:
            background_tasks.add_task(send_to_kafka, topic, data)

        return {"status": "OK", "detail": f"Sent to topic '{topic}'"}

    except Exception as e:
        logger.exception("Error in insert_posts_unclassified")
        raise HTTPException(status_code=500, detail=str(e))