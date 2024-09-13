import asyncio
from src.domain.events import AttachmentUploadedToS3
from dataclasses import dataclass
from src.adapters.messagequeues import BaseProducer


@dataclass
class KafkaHandler:
    producer: BaseProducer

    async def __call__(self, event: AttachmentUploadedToS3, queue: asyncio.Queue):
        attachment = event.attachment
        await self.producer.send(topic=attachment.messageId, value=attachment.to_json_in_utf())




