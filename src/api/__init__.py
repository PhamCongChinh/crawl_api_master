from fastapi import APIRouter
from .post import router as router_post

router = APIRouter()

router.include_router(router_post)