from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings

MONGO_URI = settings.MONGO_URI  # hoặc từ .env
client = AsyncIOMotorClient(MONGO_URI)
db = client[settings.MONGO_DB]  # Tên DB