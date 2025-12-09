from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_HOST: str = "localhost"
    APP_PORT: int = 8000
    DEBUG: bool = False

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "mydb"
    MONGO_COLLECTION_CLASSIFIED: str = "data-classified"
    MONGO_COLLECTION_UNCLASSIFIED: str = "data-unclassified"

    # TEST
    KAFKA_BROKER_HOST_TEST: str = "localhost"
    KAFKA_BROKER_PORT_TEST: int = 9092

    KAFKA_TOPIC_CLASSIFIED_TEST: str = "data-classified"
    KAFKA_TOPIC_UNCLASSIFIED_TEST: str = "data-unclassified"

    KAFKA_DEFAULT_PARTITIONS: int = 1
    KAFKA_DEFAULT_REPLICATION: int = 1

    # LIVE
    KAFKA_BROKER_HOST_LIVE: str = "localhost"
    KAFKA_BROKER_PORT_LIVE: int = 9092

    KAFKA_TOPIC_CLASSIFIED_LIVE: str = "data-classified"
    KAFKA_TOPIC_UNCLASSIFIED_LIVE: str = "data-unclassified"

    model_config = {
        "env_file": ".env"
    }

settings = Settings()