from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict, BaseSettings
import logging
import os
from dotenv import load_dotenv
from dataclasses import dataclass


ENV_FILE = ".env"


class BSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="",
        extra="ignore",  # здесь можно менять окружение на тестовое
    )


class DebugSettings(BaseSettings):
    PROFILING_ENABLE: bool = True

# class StorageSettings(BaseSettings):
#     BASE_DOWNLOADING_DIR = ''

class DBSettings(BSettings):
    pass


class KafkaSettings(BSettings):
    bootstrap_server: str = Field(default="", alias="BOOTSTRAP_SERVER")


class S3settings(BSettings):
    access_key: str = Field(default="", alias="ACCESS_KEY")
    secret_key: str = Field(default="", alias="SECRET_KEY")
    endpoint_url: str = Field(default="", alias="ENDPOINT_URL")
    bucket_name: str = Field(default="", alias="BUCKET_NAME")


@dataclass
class Settings:
    db: DBSettings = DBSettings()
    kafka: KafkaSettings = KafkaSettings()
    s3: S3settings = S3settings()
    debug: DebugSettings = DebugSettings()


settings = Settings()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# вырубили логи кафки
logging.getLogger("aiokafka").setLevel(logging.WARNING)
logging.getLogger("kafka").setLevel(logging.WARNING)
logging.getLogger("kafka.conn").setLevel(logging.WARNING)
logging.getLogger("kafka.producer.sender").setLevel(logging.WARNING)
logging.getLogger("kafka.client").setLevel(logging.WARNING)
