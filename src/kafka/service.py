import json
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
from src.core.config import settings
from src.core.logging import logger

# Config Kafka
KAFKA_BOOTSTRAP_SERVERS = f"{settings.KAFKA_BROKER_HOST}:{settings.KAFKA_BROKER_PORT}"

# --- Kafka clients -------------------------------------------------
admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

def create_topic_if_not_exists(topic_name: str):
    """Tạo Kafka topic nếu chưa có."""
    try:
        metadata = admin.list_topics(timeout=5)

        if topic_name in metadata.topics:
            return  # đã có → bỏ qua

        topic = NewTopic(
            topic=topic_name,
            num_partitions=settings.KAFKA_DEFAULT_PARTITIONS,
            replication_factor=settings.KAFKA_DEFAULT_REPLICATION
        )
        fs = admin.create_topics([topic])
        fs[topic_name].result()  # chờ topic tạo xong

        logger.info(f"Đã tạo topic: {topic_name}")

    except Exception as e:
        if "TopicAlreadyExistsError" in str(e):
            pass  # nếu vừa có thằng khác tạo thì bỏ qua lỗi này
        else:
            raise Exception(f"Lỗi khi tạo topic '{topic_name}': {e}")
        

def send_to_kafka(topic: str, data: list, batch_poll: int = 1000):
    """
    Gửi dữ liệu vào Kafka theo batch an toàn:
    - produce + poll(0) để callback chạy ngay
    - flush cuối batch để đảm bảo không mất message
    Args:
        topic (str): Tên topic Kafka
        data (list): danh sách dict message
        batch_poll (int): số record mỗi lần poll (default=1000)
    """
    create_topic_if_not_exists(topic)

    for i, item in enumerate(data, start=1):
        producer.produce(
            topic=topic,
            key=item.get("url", ""),
            value=json.dumps(item).encode("utf-8"),
            callback=delivery_report
        )

        # poll theo từng batch để trigger callback
        if i % batch_poll == 0:
            producer.poll(0)

    producer.flush()
    logger.info(f"Sent {len(data)} messages to topic '{topic}'")

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Failed to send message: {err} - {msg.key().decode()}")
    else:
        logger.info(f'Offset {msg.offset()} - {msg.key().decode()}')
