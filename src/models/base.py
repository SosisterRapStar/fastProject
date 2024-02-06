from typing import Generator

from sqlalchemy import URL
from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, as_declarative
from src.config import db_settings
from .annotated_types import UUIDpk


@as_declarative()  # pont zheskiy commited
class Base:
    __abstract__ = True
    id: Mapped[UUIDpk]

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.name}, {self.id}"

    def __str__(self):
        return self.__repr__()


class DatabaseHandler:
    def __init__(self, url: str | URL, echo: bool = db_settings.echo_mode):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session,
            scopefunc=current_task,
        )
        return session

# TODO: сделать scoped_session
    async def session_dependency(self) -> AsyncSession:  # Generator[AsyncSession]:
        async with self.session() as session:
            yield session


db_handler = DatabaseHandler(url=db_settings.db_url, echo=db_settings.echo_mode)
