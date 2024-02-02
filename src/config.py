from pydantic_settings import BaseSettings
from sqlalchemy import URL
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DebugSettings(BaseSettings):
    is_on = True


class DBSettings(BaseSettings):
    db_url: URL = URL.create(
        "postgresql+asyncpg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
    )
    echo_mode: bool = DebugSettings.is_on
