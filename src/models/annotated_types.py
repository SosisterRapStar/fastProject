import datetime
from typing import Annotated
import uuid
from sqlalchemy import text
from sqlalchemy.orm import mapped_column


created_at_timestamp = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
updated_at_timestamp = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow
    ),
]

UUIDpk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
