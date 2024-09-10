import uuid
import enum
import datetime
from datetime import timedelta
from sqlalchemy.orm.attributes import get_history
from src.config import settings
from sqlalchemy import event
from sqlalchemy import String, UniqueConstraint, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .annotated_types import created_at_timestamp, UUIDpk, updated_at_timestamp
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User


class StatusEnum(enum.Enum):
    PENDING = "pendind"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Invite(Base):
    __tablename__ = "invite"
    __table_args__ = (
        UniqueConstraint(
            "inviter_id",
            "invitee_id",
            name="unique_invite_pair",
        ),
    )

    # type was changed from enum to str because of alembic issues with enums
    status: Mapped[str] = mapped_column(default=StatusEnum.PENDING.value, server_default=StatusEnum.PENDING.value, nullable=False)

    inviter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")   
    )
    invitee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    inviter: Mapped["User"] = relationship(back_populates="sended_invites", foreign_keys=[inviter_id])
    invitee: Mapped["User"] = relationship(back_populates="received_invites", foreign_keys=[invitee_id])

    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]
    expire_at: Mapped[datetime.datetime | None] 
    
    
def update_expiration_timestamp(mapper, connection, target):
    # Check if status changed from PENDING to ACCEPTED or REJECTED  
    
    history = get_history(target, "status")
    if history and history.deleted[0] == StatusEnum.PENDING.value and target.status in (StatusEnum.ACCEPTED.value, StatusEnum.REJECTED.value):
        target.expire_at = datetime.datetime.utcnow() + timedelta(seconds=10)
       


event.listen(Invite, 'before_update', update_expiration_timestamp)


class Friends(Base):
    __tablename__ = "friendship"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "friend_id",
            name="unique_friendship",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    friend_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    def __repr__(self):
        return f"{self.user_id} | {self.friend_id}"
