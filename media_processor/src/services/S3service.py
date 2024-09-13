from adapters.s3client import S3ABC
from dataclasses import dataclass
from src.domain.events import AttachmentProcessed, AttachmentUploadedToS3

# from domain.entities import ImageEntity
import asyncio
from src.config import settings

methods = {"get": "get_object", "put": "put_object"}

DEFAULT_TIME_EXPIRATION: int = 3600
DEFAULT_METHOD: str = methods["get"]


# @dataclass
# class S3service:
#     client: S3ABC

#     async def get_image_presigned_url(self, image, method: str) -> list[str]:
#         urls: list[str] = []
#         object_prefix: str = image.id
#         high: str = f"{object_prefix}/{image.high_qualitiy}"
#         medium: str = f"{object_prefix}/{image.medium_quality}"
#         thumbnail: str = f"{object_prefix}/{image.thumbnail}"

#         urls = await asyncio.gather(
#             self.client.get_presigned_url(
#                 object_name=high,
#                 method=method,
#                 expiration_time=DEFAULT_TIME_EXPIRATION,
#                 bucket_name=image.bucket_name,
#             ),
#             self.client.get_presigned_url(
#                 object_name=medium,
#                 method=method,
#                 expiration_time=DEFAULT_TIME_EXPIRATION,
#                 bucket_name=image.bucket_name,
#             ),
#             self.client.get_presigned_url(
#                 object_name=thumbnail,
#                 method=method,
#                 expiration_time=DEFAULT_TIME_EXPIRATION,
#                 bucket_name=image.bucket_name,
#             ),
#         )

#         return urls


@dataclass
class SendToS3Handler:
    s3: S3ABC

    async def __call__(self, event: AttachmentProcessed, queue: asyncio.Queue):
        attachment = event.attachment
        if attachment.mimeType == "video/mp4":
            tasks = [
                self.s3.upload_file(
                    attachment.videoHighQuality, bucket_name=settings.s3.bucket_name
                ),
                self.s3.upload_file(
                    attachment.videoMediumQuality, bucket_name=settings.s3.bucket_name
                ),
                self.s3.upload_file(
                    attachment.videoLowQuality, bucket_name=settings.s3.bucket_name
                ),
            ]

        else:
            tasks = [
                self.s3.upload_file(
                    attachment.imageHighQuality, bucket_name=settings.s3.bucket_name
                ),
                self.s3.upload_file(
                    attachment.imageLowQuality, bucket_name=settings.s3.bucket_name
                ),
                self.s3.upload_file(
                    attachment.imageMediumQuality, bucket_name=settings.s3.bucket_name
                ),
            ]

        await asyncio.gather(*tasks)

        await queue.put(AttachmentUploadedToS3(attachment=attachment))
