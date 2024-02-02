from sqlalchemy import String
from sqlalchemy.orm import Mapped
from .base import Base
from .annotated_types import *


class Convesation(Base):
    __tablename__ = "conversation"

    status: Mapped[str] = mapped_column(nullable=False)
    is_group: Mapped[bool] = mapped_column(nullable=False)
    name: Mapped[str | None]
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]



class Message(Base):
    __tablename__ = "messages"

    content: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]




class User(Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str]
    is_online: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[created_at_timestamp]
