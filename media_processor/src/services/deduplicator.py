import asyncio
from src.domain.events import (
    Event,
    ErrorEvent,
    AtachmentUploaded,
    CheckDuplicates,
    ProcessNewFileFromClient,
    DeleteAlreadyExistedFile,
)
from adapters.s3client import S3CLient


# should be able to return: AlreadyExists event and then get fileinfo from S3 or should return UploadedNewFile
async def deduplicate_files(command: CheckDuplicates, queue: asyncio.Queue):
    s3 = command.s3  # ой бля уже хз мне похйу на депендеси инжекшин
    try:
        file_exists = await s3.file_exists
        if file_exists:
            await queue.put(DeleteAlreadyExistedFile)
        else:
            await queue.put(ProcessNewFileFromClient)
    except:
        await queue.put(ErrorEvent)
