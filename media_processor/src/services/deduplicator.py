import asyncio
from src.domain.events import (
    Event,
    ErrorEvent,
    CheckDuplicates,
    # ProcessNewFileFromClient,
    DeleteFilesFromLocalStorage,
)
from dataclasses import dataclass
from adapters.s3client import S3ABC
from src.config import settings, logger
from src.domain.entities import VideoEntity, ImageEntity


@dataclass
class DeduplicateHandler:
    s3: S3ABC

    async def __call__(self, command: CheckDuplicates, queue: asyncio.Queue):
        try:
            
            name = command.attachment.originalName
            logger.debug(f"Checking if {name} already in S3 bucket")

            file_exists = await self.s3.file_exists(
                bucket_name=settings.s3.bucket_name, file_name=name
            )
            if file_exists:
                await queue.put(
                    DeleteFilesFromLocalStorage(files=[command.attachment.originalName])
                )
            # else:
            #     await queue.put(ProcessNewFileFromClient(attachment=command.attachment))
        except Exception as e:
            logger.error(f"Error occured during deduplication: {e}")
            await queue.put(ErrorEvent(err=e))
