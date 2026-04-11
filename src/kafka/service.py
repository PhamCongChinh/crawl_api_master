import hashlib
import json
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
from src.core.config import settings
from src.core.logging import logger

KAFKA_BOOTSTRAP_SERVERS = f"{settings.KAFKA_BROKER_HOST}:{settings.KAFKA_BROKER_PORT}"

admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})


def create_topic_if_not_exists(topic_name: str):
    try:
        metadata = admin.list_topics(timeout=5)
        if topic_name in metadata.topics:
            return

        topic = NewTopic(
            topic=topic_name,
            num_partitions=settings.KAFKA_DEFAULT_PARTITIONS,
            replication_factor=settings.KAFKA_DEFAULT_REPLICATION,
        )
        fs = admin.create_topics([topic])
        fs[topic_name].result()
        logger.info(f"[KAFKA] Created topic: {topic_name}")

    except Exception as e:
        if "TopicAlreadyExistsError" not in str(e):
            raise RuntimeError(f"Failed to create topic '{topic_name}': {e}")


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"[KAFKA] Delivery failed: {err}")


def send_to_kafka(topic: str, data: list, batch_poll: int = 1000):
    create_topic_if_not_exists(topic)

    for i, item in enumerate(data, start=1):
        key_raw = item.get("url", "")
        hash_key = hashlib.md5(key_raw.encode()).hexdigest() if key_raw else None
        value = json.dumps(item).encode("utf-8")

        try:
            producer.produce(topic=topic, key=hash_key, value=value, callback=delivery_report)
            platform = item.get("crawl_source_code", "?")
            bot = item.get("crawl_bot", "?")
            logger.info(f"[KAFKA] Queued | platform={platform} bot={bot} url={key_raw}")
        except BufferError:
            producer.poll(1)
            producer.produce(topic=topic, key=hash_key, value=value, callback=delivery_report)
            logger.warning(f"[KAFKA] BufferError retry | url={key_raw}")

        if i % batch_poll == 0:
            producer.poll(0.5)

    producer.flush(5)
