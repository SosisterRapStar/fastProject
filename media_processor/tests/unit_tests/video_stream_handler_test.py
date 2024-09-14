from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import DirectoryTarget
from src.domain.entities import VideoEntity, ImageEntity
from src.services.stream_handlers import ProcessingTargetWithSHA256
import asyncio
from starlette.concurrency import run_in_threadpool
import aiofiles
from dataclasses import dataclass
from pathlib import Path
import hashlib
from src.config import settings



# test_multipart = """
import uuid

# """
CHUNK_SIZE = 1024


@dataclass
class TestPresets:
    headers: dict[str, str]
    file: str


image_test_preset = TestPresets(
    headers={'user-agent': 'PostmanRuntime/7.42.0', 
             'accept': '*/*', 
             'postman-token': '0462ba34-29e7-4533-8e7e-b7f9f4093fce', 
             'host': '127.0.0.1:5000', 
             'accept-encoding': 'gzip, deflate, br', 
             'connection': 'keep-alive', 
             'content-type': 'multipart/form-data; boundary=--------------------------990162002095409661778521',
             'content-length': '113082'},
    file=settings.base_dir + "image_file_test",
)

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
    file=settings.base_dir + "small_multipart_file_test",
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
    file=settings.base_dir + "medium_multipart_file_test",
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
    file=settings.base_dir + "big_multipart_file_test",
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
    file=settings.base_dir + "complex_multipart_file_test",
)


multiple_images_test = TestPresets(
    headers={'user-agent': 'PostmanRuntime/7.42.0', 
            'accept': '*/*', 
            'postman-token': '4038b80c-dc61-4bba-be4d-84a275c17b78',
            'host': '127.0.0.1:5000',
            'accept-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive',
            'content-type': 'multipart/form-data; boundary=--------------------------614221550133177709844202', 
            'content-length': '221149'},
    file=settings.base_dir + "multiple_images_file_test",
)

composed_video_and_file_test = TestPresets(
    headers={'user-agent': 'PostmanRuntime/7.42.0', 
              'accept': '*/*', 
              'postman-token': '626b5e8b-3c88-42d6-88c9-60d2d5b91c64', 
              'host': '127.0.0.1:5000', 
              'accept-encoding': 'gzip, deflate, br', 
              'connection': 'keep-alive', 
              'content-type': 'multipart/form-data; boundary=--------------------------961611119173016411091306', 
              'content-length': '36070230'},
    file=settings.base_dir + "composed_file_test",
)

very_big_composed_file = TestPresets(
    headers={'user-agent': 'PostmanRuntime/7.42.0',
            'accept': '*/*', 
            'postman-token': '8d1618d5-151f-45be-ae77-73905f94a9bb',
            'host': '127.0.0.1:5000', 
            'accept-encoding': 'gzip, deflate, br',
            'connection': 'keep-alive', 
            'content-type': 'multipart/form-data; boundary=--------------------------079254843882076502415992', 'content-length': '51938012'},
    file=settings.base_dir + "very_big_file_test",
)
# async def another_routine(msg: str):
#     while True:
#         await asyncio.sleep(1)
#         print(msg)


async def Consumer(queue: asyncio.Queue):
    counter = 0
    while True:
        event = await queue.get()
        if isinstance(event, list):
            async with aiofiles.open(settings.base_dir + event[1].originalName, mode="wb") as fi:
                await fi.write(event[0].getvalue())
            print(event[1])
        else:
            print(event)
                
        # print(event[1])
        
            


# async def test_streaming_file_to_stream_handler():


async def test_async_events_and_parser():
    queue = asyncio.Queue()
    future = asyncio.create_task(Consumer(queue))
    preset = very_big_composed_file

    parser = StreamingFormDataParser(headers=preset.headers)
    t = ProcessingTargetWithSHA256(directory_path=settings.base_dir)

    parser.register("file", t)
    async with aiofiles.open(preset.file, "rb") as f:
        chunk_size = CHUNK_SIZE
        chunk = await f.read(chunk_size)
        while chunk:
            await run_in_threadpool(parser.data_received, chunk)
            while loaded_videos := t.video_filenames:
                await queue.put(loaded_videos.pop())

            while loaded_images := t.image_files:
                image = loaded_images.pop()
                await queue.put(image)

            chunk = await f.read(chunk_size)
    
    await asyncio.sleep(2)

    # event = await future
    # print(event)


if __name__ == "__main__":
    asyncio.run(test_async_events_and_parser())
    
