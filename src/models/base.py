from sqlalchemy import URL
from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
    AsyncAttrs,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Mapped, DeclarativeBase
from src.config import settings
from .annotated_types import UUIDpk


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    id: Mapped[UUIDpk]

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.id}"

    def __str__(self):
        return self.__repr__()


class DatabaseHandler:
    def __init__(self, url: str | URL, echo: bool = settings.db_settings.echo_mode):
        self.engine = create_async_engine(url=url)
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
        session = self.get_scoped_session()
        async with session() as session:
            yield session


db_handler = DatabaseHandler(
    url=settings.db_settings.db_url, echo=settings.db_settings.echo_mode
)
