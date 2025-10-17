from typing import Any, Dict, List
from pydantic import BaseModel
class MessagePayload(BaseModel):
    topic: str
    message: List[Dict[str, Any]]