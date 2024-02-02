from sqlalchemy import create_engine, URL
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from src.config import db_settings
from .annotated_types import UUIDpk


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[UUIDpk]




class DatabaseHandler:
    def __init__(self, url: str | URL, echo: bool = db_settings.echo_mode):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )


db_handler = DatabaseHandler(url=db_settings.db_url, echo=db_settings.echo_mode)
