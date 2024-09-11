import pytest
import os
import uvicorn
from src.entrypoints.app import app
import multiprocessing
import time
from src.config import logger, settings
import aiohttp

PORT = 5005
ENDPOINT = f"http://localhost:{PORT}/videos/"
TEST_FILE = settings.base_dir + "download.html"
REQUESTS_NUMBER = 100

# async def get_form_data(file_name: str, content_type: str):
#     form_data = aiohttp.FormData()

#     async with aiofiles.open(file_name, 'rb') as f:
#         form_data.add_field("file", f, filename=file_name, content_type=content_type)

#     return form_data

# fixture only for testing with a lot of requests
# async def start_server():
#     uvicorn.run(app, port=PORT)

# @pytest.fixture(scope="function")
# async def start_testing_with_uvicorn_in_another_process():
#     server_process = multiprocessing.Process(target=start_server, daemon=True)
#     server_process.start()
#     logger.debug("Pause")
#     time.sleep(2)

#     yield

#     server_process.terminate()
#     server_process.join()
