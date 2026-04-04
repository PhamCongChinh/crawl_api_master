from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.core.config import settings
from src.core.logging import logger

router = APIRouter(prefix="/api/v1/check", tags=["Check"])

@router.get("/health")
async def check_health():
    return {
        "status" : "OK"
    }