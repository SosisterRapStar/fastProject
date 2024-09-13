import asyncio
from src.domain.events import AtachmentUploadedToS3
from dataclasses import dataclass
from src.adapters.messagequeues import BaseProducer


@dataclass
class KafkaHandler:
    producer: BaseProducer

    async def __call__(self, event: AtachmentUploadedToS3, queue: asyncio.Queue):
        atachment = event.attachment
        await self.producer.send(
            topic=atachment.messageId, value=atachment.to_json_in_utf()
        )
