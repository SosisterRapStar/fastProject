from starlette.concurrency import run_in_threadpool
from fastapi import FastAPI, Request
from src.adapters.s3client import S3CLient
from src.adapters.messagequeues import KafkaProducer, FakeProducer
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import Request
from streaming_form_data import StreamingFormDataParser
from src.domain.events import CheckDuplicates
from src.services.stream_handlers import VideoProcessingTargetWithSHA256
from config import settings, logger
from typing import Callable
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from pyinstrument.renderers.speedscope import SpeedscopeRenderer
import aiofiles
from src.bootstrap import bootstrap
from contextlib import asynccontextmanager
import asyncio


origins = [
    "http://localhost:5173/",
]


message_bus = bootstrap(S3CLient, FakeProducer)


@asynccontextmanager
async def lifespan(app: FastAPI):
    message_bus_task = await message_bus.start()
    yield
    if message_bus_task:
        # Cancel the task if it exists
        message_bus_task.cancel()
        try:
            await message_bus_task
        except asyncio.CancelledError:
            print("Message bus task was canceled.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/videos/", status_code=201)
async def upload_video(request: Request):
    parser = StreamingFormDataParser(headers=request.headers)
    target = VideoProcessingTargetWithSHA256(directory_path=settings.base_dir)

    parser.register("video", target=target)

    async for chunk in request.stream():
        await run_in_threadpool(parser.data_received, chunk)
        while loaded_files := target.multipart_filenames:
            command = CheckDuplicates(attachment=loaded_files.pop())
            await message_bus.queue.put(command)

    return {"sosi": "pisos"}


@app.post("/test_upload/", status_code=201)
async def upload_video(request: Request):
    print(dict(request.headers))
    async with aiofiles.open("multipart_file", "wb") as f:
        await f.seek(0)
        async for chunk in request.stream():
            await f.write(chunk)

    return {"sosi": "pisos"}


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000)
