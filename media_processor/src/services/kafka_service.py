import asyncio
from src.domain.events import (
    AttachmentUploadedToS3,
    ErrorEvent,
    DeleteFilesFromLocalStorage,
)
from dataclasses import dataclass
from src.adapters.messagequeues import BaseProducer
from src.config import logger


@dataclass
class KafkaHandler:
    producer: BaseProducer

    async def __call__(self, event: AttachmentUploadedToS3, queue: asyncio.Queue):
        try:
            attachment = event.attachment
            await self.producer.send(
                topic=attachment.messageId, value=attachment.to_json_in_utf()
            )
            if attachment.mimeType.split()[0] == "image":
                await queue.put(
                    DeleteFilesFromLocalStorage(
                        files=[
                            attachment.originalName,
                            attachment.imageHighQuality,
                            attachment.imageLowQuality,
                            attachment.imageMediumQuality,
                            attachment.imageThumbnail,
                        ]
                    )
                )
            else:
                await queue.put(
                    DeleteFilesFromLocalStorage(
                        files=[
                            attachment.originalName,
                            attachment.videoHighQuality,
                            attachment.videoLowQuality,
                            attachment.videoMediumQuality,
                            attachment.videoThumbnail,
                        ]
                    )
                )
        except Exception as e:
            logger.error(f"Erorr occured duting kafka working: {e}")
            await queue.put(ErrorEvent(err=e))
