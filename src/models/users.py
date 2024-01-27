from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from src.base import Base


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[str]
    status: Mapped[str]




