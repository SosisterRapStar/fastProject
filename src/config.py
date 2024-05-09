import datetime
from pydantic_settings import BaseSettings
from sqlalchemy import URL
from datetime import timedelta
import os
from dotenv import load_dotenv


# if os.environ.get("TEST_ENV", None):
#     load_dotenv(os.environ["TEST_ENV"])
# else:
#     load_dotenv()

load_dotenv()

DEBUG_MODE = bool(os.getenv("DEBUG_MODE"))


class SchemasValidationSettings(BaseSettings):
    extra: str = "forbid"


class RouterSettings(BaseSettings):
    api_v1_prefix: str = "/api/v1"


class DB(BaseSettings):
    pass

class DBSettings(DB):
    db_string_url: str = os.getenv("DB_STRING")
    db_url: URL = URL.create(
        "postgresql+asyncpg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        port = int(os.getenv("DB_PORT"))
    )
    echo_mode: bool = DEBUG_MODE
    sync_url: str = os.getenv("DB_SYNC_URL")
    

class SecuritySettings(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCES_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 120

class Broker(BaseSettings):
    url: str = os.getenv("BROKER_URL")

class RedisSettings(BaseSettings):
    host: str = os.getenv("REDIS_HOST")
    port: int = int(os.getenv("REDIS_PORT"))
    db: int = int(os.getenv("REDIS_DB"))
    max_pool_size: int = 5
    
class Settings(BaseSettings):
    schemas_settings: SchemasValidationSettings = SchemasValidationSettings()
    router_settings: RouterSettings = RouterSettings()
    db_settings: DB = DBSettings()
    security_settings: SecuritySettings = SecuritySettings()
    broker: Broker = Broker()
    redis: RedisSettings = RedisSettings()


settings = Settings()
