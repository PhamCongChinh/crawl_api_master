from enum import IntEnum
from typing import Annotated, Optional
from pydantic import BaseModel, Field

class DocTypeEnum(IntEnum):
    POST = 1
    COMMENT = 2
class CrawlSourceEnum(IntEnum):
    FACEBOOK = 1
class PostUnclassifiedModel(BaseModel):
    # id: Optional[str] = None
    doc_type: int = Field(default=DocTypeEnum.POST)
    source_type: int
    crawl_source: int # crawl_source: int = Field(default=CrawlSourceEnum.FACEBOOK)
    crawl_source_code: Optional[str] = None #crawl_source: int = Field(default=1)
    pub_time: int = Field(..., gt=0)
    crawl_time: int = Field(..., gt=0)
    subject_id: Optional[str] = Field(default="", max_length=255)
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = Field(default="")
    url: str = Field(..., max_length=3000)
    media_urls: Optional[str] = Field(default="[]")
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    reactions: int = Field(default=0, ge=0)
    favors: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)
    web_tags: Optional[str] = Field(default="[]")
    web_keywords: Optional[str] = Field(default="[]")
    auth_id: str = Field(..., max_length=3000)
    auth_name: str = Field(..., max_length=3000)
    auth_type: int
    auth_url: str = Field(..., max_length=3000)
    source_id: str = Field(..., max_length=3000)
    source_name: str = Field(..., max_length=3000)
    source_url: str = Field(..., max_length=3000)
    reply_to: Optional[str] = None
    level: Optional[int] = None
    org_id: Optional[int] = None
    sentiment: int = Field(default=0)
    isPriority: Optional[bool] = None
    crawl_bot: str