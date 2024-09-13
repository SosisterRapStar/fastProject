from adapters.s3client import S3ABC
from dataclasses import dataclass
from src.domain.events import AttachmentProcessed, AttachmentUploadedToS3, ErrorEvent

# from domain.entities import ImageEntity
import asyncio
from src.config import settings, logger

methods = {"get": "get_object", "put": "put_object"}

DEFAULT_TIME_EXPIRATION: int = 3600
DEFAULT_METHOD: str = methods["get"]


@dataclass
class SendToS3Handler:
    s3: S3ABC

    async def __call__(self, event: AttachmentProcessed, queue: asyncio.Queue):
        try:
            attachment = event.attachment
            if attachment.mimeType == "video/mp4":
                tasks = [
                    self.s3.upload_file(
                        attachment.videoHighQuality, bucket_name=settings.s3.bucket_name
                    ),
                    self.s3.upload_file(
                        attachment.videoMediumQuality,
                        bucket_name=settings.s3.bucket_name,
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
                        attachment.imageMediumQuality,
                        bucket_name=settings.s3.bucket_name,
                    ),
                ]

            await asyncio.gather(*tasks)

            await queue.put(AttachmentUploadedToS3(attachment=attachment))
        except Exception as e:
            logger.error(f"Error occured during uploading to S3 {e}")
            await queue.put(ErrorEvent(err=e))
