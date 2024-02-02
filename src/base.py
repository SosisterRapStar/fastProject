from sqlalchemy import create_engine, URL
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import DBSettings


class Base(DeclarativeBase):
    pass


class DatabaseHandler:
    def __init__(self, url: str | URL, echo: bool = DBSettings.echo_mode):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session = async_sessionmaker(
            self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )


db_handler = DatabaseHandler(url=DBSettings.db_url)
