from src.services.video_compressor import (
    VideoStreamInfoSchema,
    AudioStreamInfoSchema,
    Quality,
    create_compressing_config,
    video_compressing_pipeline,
    get_video_info,
)
from src.domain.entities import AttachmentEntity
from src.domain.events import (
    AtachmentProcessed,
    AtachmentUploadedFromClient,
    ErrorEvent,
)
import asyncio
import uuid
from src.config import settings
import time


async def test_compression_config_generator_with_all_params():
    file_info = VideoStreamInfoSchema(
        codec_name="fake_codec",
        format_name="fake_format",
        width=1337,
        height=1080,
        bit_rate=100000,
        audio=AudioStreamInfoSchema(codec_name="fake_codec", bit_rate=1000),
    )

    presets = {
        "high": Quality(height=1080),
        "medium": Quality(height=720),
        "low": Quality(height=360),
    }

    base_videos_name = "_test.mp4"

    original_name = "example.mp4 "

    for preset, quality in presets.items():
        output_name = preset + "_" + base_videos_name
        config = await create_compressing_config(
            video_info=file_info,
            quality=quality,
            file_name=original_name,
            output_name=preset + "_" + base_videos_name,
        )
        print(config)
        assert "libx264 -pix_fmt yuv420p" in config
        assert "-c:a aac" in config
        assert f"scale=-1:{quality.height}" in config


async def test_compression_config_generator_with_some_params():
    file_info = VideoStreamInfoSchema(
        codec_name="h264",
        format_name="ew",
        width=1337,
        height=1080,
        bit_rate=100000,
        audio=AudioStreamInfoSchema(codec_name="aac", bit_rate=1000),
    )

    presets = {
        "high": Quality(height=1080),
        "medium": Quality(height=720),
        "low": Quality(height=360),
    }

    base_videos_name = "_test.mp4"

    original_name = "example.mp4 "

    for preset, quality in presets.items():
        output_name = preset + "_" + base_videos_name
        config = await create_compressing_config(
            video_info=file_info,
            quality=quality,
            file_name=original_name,
            output_name=preset + "_" + base_videos_name,
        )
        print(config)
        assert "libx264 -pix_fmt yuv420p" not in config
        assert "-c:a aac" not in config
        assert f"scale=-1:{quality.height}" in config


async def test_get_video_info():
    file_name = settings.base_dir + "example.mp4"
    video_info = await get_video_info(file_name=file_name)
    print(video_info)


async def Consumer(queue: asyncio.Queue):
    while True:
        event = await queue.get()
        return event


# slow test here can be used level up IO approach
async def test_integration_compressing_ffmpeg():
    queue = asyncio.Queue(maxsize=10)
    future = asyncio.create_task(Consumer(queue=queue))
    realfile = "example.mp4"
    attachment = AttachmentEntity(
        id=str(uuid.uuid4()),
        mimeType="video/mp4",
        originalName=realfile,
    )
    event = AtachmentUploadedFromClient(attachment=attachment)
    await video_compressing_pipeline(event=event, queue=queue)
    event: AtachmentProcessed = await future

    assert isinstance(event, AtachmentProcessed)
    assert event.attachment.id == attachment.id
    assert event.attachment.videoHighQuality is not None
    assert event.attachment.videoLowQuality is not None
    assert event.attachment.videoMediumQuality is not None
    assert event.attachment.videoThumbnail is not None


# slow test here can be used level up IO approach
async def test_integration_compressing_ffmpeg_negative_with_error_event():
    queue = asyncio.Queue(maxsize=10)
    future = asyncio.create_task(Consumer(queue=queue))
    realfile = "non-existent.mp4"
    attachment = AttachmentEntity(
        id=str(uuid.uuid4()),
        mimeType="video/mp4",
        originalName=realfile,
    )
    event = AtachmentUploadedFromClient(attachment=attachment)
    await video_compressing_pipeline(event=event, queue=queue)
    event: ErrorEvent = await future
    assert event.__class__ == ErrorEvent


asyncio.run(test_compression_config_generator_with_all_params())
