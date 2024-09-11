from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import uuid

# class ImageEntity(BaseModel):
#     id: str
#     bucket_name: str = Field(alias="bucketName")
#     high_quality: str = Field(alias="highQuality")
#     medium_quality: str = Field(alias="mediumQuality")
#     thumbnail: str


def _create_id() -> str:
    return str(uuid.uuid4())


@dataclass
class Entity:
    id: str = field(default_factory=_create_id)


@dataclass(kw_only=True)
class AttachmentEntity(Entity):
    mimeType: str  # image/jpeg, #video/mp4
    originalName: str
    imageThumbnail: str | None = None
    imageHighQuality: str | None = None
    imageMediumQuality: str | None = None
    imageLowQuality: str | None = None
    videoThumbnail: str | None = None
    videoHighQuality: str | None = None
    videoMediumQuality: str | None = None
    videoLowQuality: str | None = None


# class VideoEntity(BaseModel):
#     id: str
#     bucket_name: str = Field(alias="bucketName")
#     medium_quality_thumb: str = Field(alias="mediumQuality")
#     thumbnail: str
#     video_low_quality: str = Field(alias="videoLow")
#     video_medium_quality: str = Field(alias="videoMedium")
#     video_original: str = Field(alias="videoOriginal")


class PutPolicies(BaseModel):
    high_url: str = Field(default="")
    medium_url: str = Field(default="")
    thumbnail_url: str = Field(default="")


class GetPolicies(BaseModel):
    high_url: str = Field(default="")
    medium_url: str = Field(default="")
    thumbnail_url: str = Field(default="")
