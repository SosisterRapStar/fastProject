from dataclasses import dataclass, field
from .entities import AttachmentEntity
from abc import ABC
import uuid
from src.adapters.s3client import S3ABC
from src.adapters.cache import AbstractCache
import json


def _create_uuid():
    return str(uuid.uuid4())


@dataclass
class Command(ABC):
    id: set = field(default_factory=_create_uuid)


@dataclass
class DeleteProcessedFilesFromLocalStorage(Command):
    attachment: AttachmentEntity


@dataclass
class DeleteAlreadyExistedFile(Command):
    attachment: AttachmentEntity


@dataclass
class CheckDuplicates(Command):
    attachment: AttachmentEntity
    # s3: S3ABC
    # cache: AbstractCache


@dataclass
class Event(ABC):
    id: str = field(default_factory=_create_uuid)

    def to_json_in_utf(self) -> bytes:
        return json.dumps(self.__dict__).encode("utf-8")


@dataclass
class AtachmentUploaded(Event):
    attachment: AttachmentEntity


@dataclass(kw_only=True)
class ProcessNewFileFromClient(Command):
    attachment: AttachmentEntity


@dataclass(kw_only=True)
class AtachmentProcessed(Event):
    attachment: AttachmentEntity


@dataclass(kw_only=True)
class AtachmentUploadedToS3(Event):
    attachment: AttachmentEntity


@dataclass(kw_only=True)
class ErrorEvent(Event):
    pass
