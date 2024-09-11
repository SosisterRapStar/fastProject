import asyncio
from src.domain.events import AtachmentUploadedToS3


async def send_event_to_kafka(event: AtachmentUploadedToS3, queue: asyncio.Queue):
    attachment = event.attachment
    pass
