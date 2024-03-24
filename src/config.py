from pydantic_settings import BaseSettings
from sqlalchemy import URL
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
DEBUG_MODE = bool(os.getenv("DEBUG_MODE"))
TEST_MODE = bool(os.getenv("TEST_MODE"))


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

class Test_DBSettings(DB):
    db_string_url: str = os.getenv("TEST_DB_STRING")
    db_url: URL = URL.create(
        "postgresql+asyncpg",
        username=os.getenv("TEST_DB_USER"),
        password=os.getenv("TEST_DB_PASSWORD"),
        host=os.getenv("TEST_DB_HOST"),
        database=os.getenv("TEST_DB_NAME"),
        port = int(os.getenv("TEST_DB_PORT"))
    )
    echo_mode: bool = DEBUG_MODE


class SecuritySettings(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCES_TOKEN_EXPIRE_MINUTES: int = 60


class Settings(BaseSettings):
    schemas_settings: SchemasValidationSettings = SchemasValidationSettings()
    router_settings: RouterSettings = RouterSettings()
    db_settings: DB = DBSettings() if not TEST_MODE else Test_DBSettings()
    security_settings: SecuritySettings = SecuritySettings()


settings = Settings()
