from fastapi import APIRouter
from .post import router as router_post
from .checkheath import router as router_checkhealth

router = APIRouter()

router.include_router(router_post)
router.include_router(router_checkhealth)