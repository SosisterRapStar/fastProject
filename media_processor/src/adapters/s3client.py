from dataclasses import dataclass, field
from aiobotocore.session import get_session, AioSession, AioBaseClient
from botocore.exceptions import ClientError
from contextlib import asynccontextmanager
import asyncio
from config import settings
from abc import ABC, abstractmethod
from enum import Enum
from config import logger
from typing import AsyncGenerator


@dataclass
class S3Exception(Exception):
    message: str = ""

    def __str__(self) -> str:
        return f"Something went wrong with S3: {self.message}"


@dataclass
class S3ABC(ABC):
    @abstractmethod
    async def upload_file(
        self, file_path: str, bucket_name: str, object_name: str = None
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_presigned_url(
        self, object_name: str, method: str, expiration_time: int, bucket_name: str
    ):
        raise NotImplementedError

    @abstractmethod
    async def file_exists(self, bucket_name: str, file_name: str) -> bool:
        raise NotImplementedError


@dataclass
class FakeS3(S3ABC):
    storage: list[str] = field(default_factory=list)

    async def upload_file(self, file_path: str, object_name: str = None):
        self.storage.append(file_path)

    async def get_presigned_url(
        self, object_name: str, method: str, expiration_time: int, bucket_name: str
    ):
        return "Соси балумбу"


@dataclass
class S3CLient(S3ABC):
    """_summary_

    Args:
        S3ABC (_type_): _description_

    Raises:
        S3Exception: raised if S3 responsed by error without 404
    """

    config = {
        "aws_access_key_id": settings.s3.access_key,
        "aws_secret_access_key": settings.s3.secret_key,
        "endpoint_url": settings.s3.endpoint_url,
    }

    session: AioSession = get_session()

    @asynccontextmanager
    async def __get_client(self) -> AsyncGenerator[AioBaseClient, None]:
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        object_name: str = None,
    ) -> None:
        if file_path:
            if not object_name:
                object_name: str = file_path.split("/")[
                    -1
                ]  # using the filename for object name
            async with self.__get_client() as client:
                with open(file_path, "rb") as file:
                    await client.put_object(
                        Bucket=bucket_name, Key=object_name, Body=file
                    )

    async def get_presigned_url(
        self, object_name: str, method: str, expiration_time: int, bucket_name: str
    ):
        async with self.__get_client() as client:
            url = await client.generate_presigned_url(
                ClientMethod=method,
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=expiration_time,
            )
            logger.debug("Created presigned URL %s, with method %s", url, method)
            return url

    async def file_exists(self, bucket_name: str, file_name: str) -> bool:
        async with self.__get_client() as client:
            try:
                await client.head_object(Bucket=bucket_name, Key=file_name)
                return True
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":  # значит что файл не найден
                    return False
                raise S3Exception(
                    message=e.response["Error"]
                )  # TODO: не забыть обработать
