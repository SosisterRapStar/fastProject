from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import DirectoryTarget
from src.domain.entities import AttachmentEntity
from src.services.stream_handlers import VideoProcessingTargetWithSHA256
import asyncio
from starlette.concurrency import run_in_threadpool
import aiofiles
from dataclasses import dataclass
from pathlib import Path
import hashlib

# test_multipart = """
import uuid

# """
CHUNK_SIZE = 1024


@dataclass
class TestPresets:
    headers: dict[str, str]
    file: str


small_test_preset = TestPresets(
    headers={
        "user-agent": "PostmanRuntime/7.41.2",
        "accept": "*/*",
        "postman-token": "e880b118-0ea3-4074-8a5c-7d48b607bdbf",
        "host": "127.0.0.1:5000",
        "accept-encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "content-type": "multipart/form-data; boundary=--------------------------689625782190013645834302",
        "content-length": "12115",
    },
    file="/home/vanya/test_ruff/small_multipart_file_test",
)

# Medium test preset
medium_test_preset = TestPresets(
    headers={
        "user-agent": "PostmanRuntime/7.41.2",
        "accept": "*/*",
        "postman-token": "748b1549-1934-4c7d-8bab-96d8af52cfa5",
        "host": "127.0.0.1:5000",
        "accept-encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "content-type": "multipart/form-data; boundary=--------------------------092466239646792037285037",
        "content-length": "15764468",
    },
    file="/home/vanya/test_ruff/medium_multipart_file_test",
)

# Big test preset
big_test_preset = TestPresets(
    headers={
        "user-agent": "PostmanRuntime/7.41.2",
        "accept": "*/*",
        "postman-token": "fd950584-1757-4201-89c3-1935d0d5c929",
        "host": "127.0.0.1:5000",
        "accept-encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "content-type": "multipart/form-data; boundary=--------------------------433465365647585314260668",
        "content-length": "35849137",
    },
    file="/home/vanya/test_ruff/big_multipart_file_test",
)

# Two files in one multipart with one key preset
two_files_in_one_multipart_with_one_key = TestPresets(
    headers={
        "user-agent": "PostmanRuntime/7.41.2",
        "accept": "*/*",
        "postman-token": "54257b69-407a-4ba4-a4db-785449d4fe2a",
        "host": "127.0.0.1:5000",
        "accept-encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "content-type": "multipart/form-data; boundary=--------------------------563485192429315734968550",
        "content-length": "51613549",
    },
    file="/home/vanya/test_ruff/complex_multipart_file_test",
)


# async def another_routine(msg: str):
#     while True:
#         await asyncio.sleep(1)
#         print(msg)


async def Consumer(queue: asyncio.Queue):
    counter = 0
    while True:
        event = await queue.get()
        print(event)


# async def test_streaming_file_to_stream_handler():


async def test_async_events_and_parser():
    queue = asyncio.Queue()
    future = asyncio.create_task(Consumer(queue))
    preset = small_test_preset

    parser = StreamingFormDataParser(headers=preset.headers)
    # parser.register('file', VideoProcessingTargetWithSHA256(loop=asyncio.get_running_loop(), queue=queue, directory_path='/home/vanya/test_ruff/uploads'))
    t = VideoProcessingTargetWithSHA256(directory_path="/home/vanya/test_ruff/uploads")

    parser.register("file", t)
    async with aiofiles.open(preset.file, "rb") as f:
        chunk_size = CHUNK_SIZE
        chunk = await f.read(chunk_size)
        while chunk:
            await run_in_threadpool(parser.data_received, chunk)
            while loaded_files := t.multipart_filenames:
                await queue.put(loaded_files.pop())
            chunk = await f.read(chunk_size)

    # event = await future
    # print(event)


if __name__ == "__main__":
    asyncio.run(test_async_events_and_parser())
