import asyncio
from src.domain.events import (
    Event,
    DeleteAlreadyExistedFile,
    DeleteProcessedFilesFromLocalStorage,
)
import aiofiles.os
from src.config import logger

directory_path = "/home/vanya/test_ruff/uploads"


async def delete_files(
    command: DeleteAlreadyExistedFile | DeleteProcessedFilesFromLocalStorage,
    queue: asyncio.Queue,
):
    atachment = command.attachment
    file_path = directory_path + atachment.originalName
    try:
        await aiofiles.os.remove(file_path)
        logger.debug(f"{file_path} deleted successfully.")
    except FileNotFoundError:
        logger.debug(f"{file_path} not found.")
    except Exception as e:
        logger.debug(f"An error occurred while deleting {file_path}: {e}")