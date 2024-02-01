import datetime
from typing import Annotated

from sqlalchemy import text, UUID
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

UUIDpk = Annotated[UUID, mapped_column(primary_key=True)]
