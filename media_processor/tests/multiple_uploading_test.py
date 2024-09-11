import aiohttp
import asyncio
import aiofiles
import os
import time
from src.config import settings

ENDPOINT = "http://localhost:5000/videos/"
TEST_FILE = settings.base_dir + 'download.html'
REQUESTS_NUMBER = 1000


async def get_form_data(file_name: str, content_type: str):
    form_data = aiohttp.FormData()

    # Open file and add it to form data
    form_data.add_field(
        "file",
        open(file_name, "rb"),
        filename=os.path.basename(file_name),
        content_type=content_type,
    )

    return form_data


async def send_multipart():
    # Generate form data for each request
    form_data = await get_form_data(file_name=TEST_FILE, content_type="text/html")

    # Send request
    async with aiohttp.ClientSession() as session:
        async with session.post(ENDPOINT, data=form_data) as response:
            pass


async def send_multiple_multipart(number: int):
    for i in range(number):
        await send_multipart()


async def main():
    time_start = time.perf_counter()

    # Send multiple requests
    await send_multiple_multipart(REQUESTS_NUMBER)

    time_end = time.perf_counter()
    print(f"Total time: {time_end - time_start} seconds")


if __name__ == "__main__":
    asyncio.run(main())
