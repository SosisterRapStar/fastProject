from dataclasses import dataclass, field
from .entities import VideoEntity, ImageEntity
from abc import ABC
import uuid
from src.adapters.s3client import S3ABC
from src.adapters.cache import AbstractCache
import json
from typing import List


def _create_uuid():
    return str(uuid.uuid4())


@dataclass
class Command(ABC):
    id: set = field(default_factory=_create_uuid)


@dataclass(kw_only=True)
class DeleteFilesFromLocalStorage(Command):
    files: List[str]


@dataclass(kw_only=True)
class CheckDuplicates(Command):
    attachment: VideoEntity | ImageEntity
    # s3: S3ABC
    # cache: AbstractCache


@dataclass
class Event(ABC):
    id: str = field(default_factory=_create_uuid)


@dataclass(kw_only=True)
class AttachmentUploaded(Event):
    attachment: VideoEntity | ImageEntity


@dataclass(kw_only=True)
class ProcessVideoFileFromClient(Command):
    attachment: VideoEntity | ImageEntity


@dataclass(kw_only=True)
class ProcessImageFileFromClient(Command):
    image_bytes: bytes
    attachment: ImageEntity


@dataclass(kw_only=True)
class AttachmentProcessed(Event):
    attachment: VideoEntity | ImageEntity


# class LoadFilesToS3(Command):
#     files:


@dataclass(kw_only=True)
class AttachmentUploadedToS3(Event):
    attachment: VideoEntity | ImageEntity


@dataclass(kw_only=True)
class ErrorEvent(Event):
    err: str
