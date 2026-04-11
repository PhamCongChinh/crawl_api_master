import logging
from pydantic import ValidationError
from pymongo import UpdateOne

from src.model.post_classified import PostClassifiedModel
from src.model.post_unclassified import PostUnclassifiedModel
from src.core.mongo import collection_classified, collection_unclassified


class PostService:
    @staticmethod
    async def insert_posts(items: dict):
        operations = []
        for item in items.get("data", []):
            try:
                post = PostClassifiedModel(**item)
                operations.append(
                    UpdateOne({"url": post.url}, {"$set": post.model_dump()}, upsert=True)
                )
            except ValidationError:
                logging.warning(f"Invalid classified post: {item.get('url')}")

        if operations:
            result = await collection_classified.bulk_write(operations, ordered=False)
            return {
                "matched": result.matched_count,
                "modified": result.modified_count,
                "upserted": len(result.upserted_ids),
            }

    @staticmethod
    async def insert_unclassified_org_posts(items: dict):
        operations = []
        for item in items.get("data", []):
            try:
                post = PostUnclassifiedModel(**item)
                operations.append(
                    UpdateOne({"url": post.url}, {"$set": post.model_dump()}, upsert=True)
                )
            except ValidationError:
                logging.warning(f"Invalid unclassified post: {item.get('url')}")

        if operations:
            result = await collection_unclassified.bulk_write(operations, ordered=False)
            return {
                "matched": result.matched_count,
                "modified": result.modified_count,
                "upserted": len(result.upserted_ids),
            }
