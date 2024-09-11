import asyncio
from src.domain.events import AtachmentUploadedToS3
from dataclasses import dataclass
from src.adapters.messagequeues import BaseProducer



@dataclass
class KafkaHandler:
    kafka: BaseProducer
    
    async def __call__(event: AtachmentUploadedToS3, queue: asyncio.Queue):  
        pass
