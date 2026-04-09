from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_HOST: str = "localhost"
    APP_PORT: int = 8000
    DEBUG: bool = False

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "mydb"
    MONGO_COLLECTION_CLASSIFIED: str = "data-classified"
    MONGO_COLLECTION_UNCLASSIFIED: str = "data-unclassified"

    KAFKA_BROKER_HOST: str = "localhost"
    KAFKA_BROKER_PORT: int = 9092
    
    KAFKA_TOPIC_CLASSIFIED: str = "data-classified"
    KAFKA_TOPIC_UNCLASSIFIED: str = "data-unclassified"

    KAFKA_DEFAULT_PARTITIONS: int = 1
    KAFKA_DEFAULT_REPLICATION: int = 1

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    model_config = {
        "env_file": ".env"
    }

settings = Settings()