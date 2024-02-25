from pydantic_settings import BaseSettings
from sqlalchemy import URL
import os
from dotenv import load_dotenv
from src.config_file import global_config

# Load environment variables from .env file
load_dotenv()


class SchemasValidationSettings(BaseSettings):
    extra: str = 'forbid'


class RouterSettings(BaseSettings):
    api_v1_prefix: str = "/api/v1"


class DBSettings(BaseSettings):
    db_string_url: str = os.getenv("DB_STRING")
    db_url: URL = URL.create(
        "postgresql+asyncpg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
    )
    echo_mode: bool = global_config.DEBUG_MODE


class SecuritySettings(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCES_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCES_TOKEN_EXPIRE_MINUTES"))


security_settings = SecuritySettings()
db_settings = DBSettings()
schemas_settings = SchemasValidationSettings()
router_settings = RouterSettings()
