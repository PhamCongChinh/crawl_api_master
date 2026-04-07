from beanie import Document
from datetime import datetime

class BotHealth(Document):
    bot_id: str
    bot_type: str   # tiktok, news, tax...
    last_ping: datetime
    last_data_time: datetime | None
    status: str  # alive / dead / warning