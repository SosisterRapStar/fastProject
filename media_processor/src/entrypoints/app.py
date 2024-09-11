from starlette.concurrency import run_in_threadpool
from fastapi import FastAPI, Request
from services.S3service import S3service
from adapters.s3client import S3CLient
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import Request
from streaming_form_data import StreamingFormDataParser

from src.services.stream_handlers import VideoProcessingTargetWithSHA256
from src.domain.events import AtachmentUploadedFromClient
from config import settings, logger
from typing import Callable
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from pyinstrument.renderers.speedscope import SpeedscopeRenderer
import asyncio
import aiofiles
from dependencies.queue import asyncio_consumer


origins = [
    "http://localhost:5173/",
]


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

queue = asyncio.Queue()

# profiler
if settings.debug.PROFILING_ENABLE:

    @app.middleware("http")
    async def profile_request(request: Request, call_next: Callable):
        profile_type_to_ext = {"html": "html", "speedscope": "speedscope.json"}
        profile_type_to_renderer = {
            "html": HTMLRenderer,
            "speedscope": SpeedscopeRenderer,
        }

        profile_type = request.query_params.get("profile_format", "speedscope")

        with Profiler(interval=0.001, async_mode="enabled") as profiler:
            response = await call_next(request)

        extension = profile_type_to_ext[profile_type]
        renderer = profile_type_to_renderer[profile_type]()
        with open(f"profile.{extension}", "w") as out:
            out.write(profiler.output(renderer=renderer))
        return response


# @app.post(
#     "/images/",
# )
# async def give_presigned_for_put(image: ImageEntity) -> GetPolicies:
#     s3 = S3service(client=S3CLient())
#     urls = await s3.get_image_presigned_url(image=image, method="put_object")
#     return GetPolicies(high_url=urls[0], medium_url=urls[1], thumbnail_url=urls[2])


@app.post("/videos/", status_code=201)
async def upload_video(consumer: asyncio_consumer, request: Request):
    parser = StreamingFormDataParser(headers=request.headers)
    target = VideoProcessingTargetWithSHA256(
        directory_path=settings.base_dir
    )
    parser.register("file", target=target)

    async for chunk in request.stream():
        await run_in_threadpool(parser.data_received, chunk)
        while loaded_files := target.loaded_files:
            event = AtachmentUploadedFromClient(attachment=loaded_files.pop())
            await consumer.queue.put(event)

    # async for chunk in request.stream():
    #     logger.debug("Got chunk from client")
    #     await run_in_threadpool(parser.data_received, chunk)

    return {"sosi": "pisos"}


@app.post("/test_upload/", status_code=201)
async def upload_video(request: Request):
    # parser = StreamingFormDataParser(headers=request.headers)

    print(dict(request.headers))
    async with aiofiles.open("multipart_file", "wb") as f:
        await f.seek(0)
        async for chunk in request.stream():
            await f.write(chunk)

        # logger.debug("Got chunk from client")
        # await run_in_threadpool(parser.data_received, chunk)

    return {"sosi": "pisos"}


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000)
