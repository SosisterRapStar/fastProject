import asyncio
from src.domain.events import (
    ErrorEvent,
    DeleteFilesFromLocalStorage,
)
import aiofiles.os
from src.config import logger, settings

directory_path = settings.base_dir


class DeleteFilesHandler:
    async def __call__(
        self,
        command: DeleteFilesFromLocalStorage,
        queue: asyncio.Queue,
    ):
        try:
            files = command.files
            for filename in files:
                file_path = directory_path + filename
                await aiofiles.os.remove(file_path)
                logger.debug(f"{file_path} deleted successfully.")

        except FileNotFoundError:
            logger.error(f"{file_path} not found.")
            await queue.put(ErrorEvent(err=e))

        except Exception as e:
            logger.error(f"An error occurred while deleting {file_path}: {e}")
            await queue.put(ErrorEvent(err=e))
