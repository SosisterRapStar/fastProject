import asyncio
from src.domain.events import (
    Event,
    ErrorEvent,
    AtachmentUploaded,
    CheckDuplicates,
    ProcessNewFileFromClient,
    DeleteAlreadyExistedFile,
)
from dataclasses import dataclass
from adapters.s3client import S3ABC

@dataclass  
class DeduplicateHandler:
    s3: S3ABC

    async def deduplicate_files(self, command: CheckDuplicates, queue: asyncio.Queue):
        try:
            file_exists = await self.s3.file_exists
            if file_exists:
                await queue.put(DeleteAlreadyExistedFile)
            else:
                await queue.put(ProcessNewFileFromClient)
        except:
            await queue.put(ErrorEvent)

    async def __call__(self, *args: asyncio.Any, **kwds: asyncio.Any) -> asyncio.Any:
        pass
