from adapters.s3client import S3ABC
from dataclasses import dataclass
from src.domain.events import AtachmentProcessed

# from domain.entities import ImageEntity
import asyncio

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

    async def __call__(event: AtachmentProcessed, queue: asyncio.Queue):
        pass
