# from ffmpeg import FFmpeg
# from asynccpu import ProcessTaskPoolExecutor
# from asyncffmpeg import FFmpegCoroutineFactory, StreamSpec
import asyncio
from dataclasses import dataclass
import json
from src.domain.events import (
    AtachmentProcessed,
    AtachmentUploadedFromClient,
    ErrorEvent,
)
import uuid
from config import logger



@dataclass
class VideoCompressor:
    async def __call__(
        event: AtachmentUploadedFromClient, queue: asyncio.Queue
    ):
        """
        Function that handling all process of compressing, using ffmpeg

        Args:
            event (AtachmentUploadedFromClient): Event entity that activates this func
            queue (asyncio.Queue): Async queue  for putting messages about processed videos
        """

        try:
            video = event.attachment
            original_name = base_dir + video.originalName + " "

            logger.debug(f"Starting to compress the video video_path {original_name}")

            # There should be three presets for high, medium and low quality
            presets = {
                "high": Quality(height=1080),
                "medium": Quality(height=720),
                "low": Quality(height=360),
            }

            output = {}  # maps the name of the preset and the filename for this preset

            video_info = await get_video_info(file_name=original_name)

            base_videos_name = create_attachment_id()

            for preset, quality in presets.items():
                output_name = preset + "_" + base_videos_name + ".mp4"
                logger.debug(f"starting compression of {original_name} to {preset} preset")

                config = await create_compressing_config(
                    video_info=video_info,
                    quality=quality,
                    file_name=original_name,
                    output_name=base_dir + output_name,
                )

                await start_compressing_the_video(config=config)
                output[preset] = output_name

            thumbnail_name = "tumbnail_" + base_videos_name + ".jpg"

            logger.debug(f"starting thumbnail generation for {original_name}")

            video_thumbnail = await generate_thumbnail(
                file_name=original_name, output_image_name=base_dir + "/" + thumbnail_name
            )

            video.videoMediumQuality = output["medium"]
            video.videoLowQuality = output["low"]
            video.videoHighQuality = output["high"]
            video.videoThumbnail = thumbnail_name

            event = AtachmentProcessed(attachment=video)
            await queue.put(event)

        except SubprocessErorr as e:
            logger.error("Error in compressing")
            await queue.put(ErrorEvent())

        except Exception as e:
            logger.error(f"Error in something else {e}")
            await queue.put(ErrorEvent())


@dataclass
class SubprocessErorr(Exception):
    message: str = ""


@dataclass
class ErrorDuringProbe(SubprocessErorr):
    def __str__(self) -> str:
        return f"Error occured during ffprobe function: {self.message}"


@dataclass
class ErrorDuringThumbnailGeneration(SubprocessErorr):
    def __str__(self) -> str:
        return f"Error occured during generating thumbnail in ffmpeg: {self.message}"


@dataclass
class ErorrDuringCompression(SubprocessErorr):
    def __str__(self) -> str:
        return f"Error occured during compressing the video in ffmpeg: {self.message}"


# TODO: оптимизировать сжатие, сейчас меньшие пресеты сжимают оригинал, нужно чтобы меньшие пресеты работали с данными, которые выдали более качественные пресеты
base_dir = "/home/vanya/test_ruff/uploads/"


@dataclass(frozen=True)
class Quality:
    """
    Object-Value that describes quality of the video
    """

    height: str | None
    crf: str = "28"
    video_codec: str = "h264"
    audio_codec: str = "aac"
    compress_preset: str = "veryfast"  # default preset
    tune: str = "zerolatency"
    file_format: str = "mp4"
    pix_fmt: str = "yuv420p"


@dataclass(frozen=True)
class AudioStreamInfoSchema:
    codec_name: str
    bit_rate: int


@dataclass(frozen=True)
class VideoStreamInfoSchema:
    codec_name: str
    format_name: str
    width: int
    height: int
    bit_rate: int
    audio: AudioStreamInfoSchema


async def get_video_info(file_name: str) -> VideoStreamInfoSchema:
    # ffmpeg config for getting info about file
    # TODO: add errors handling

    try:
        ffprobe_query = f"ffprobe -show_entries format=format_name,bit_rate,filename:stream=index,codec_name,width,height,bit_rate -of json -v quiet -i {file_name}"
        process = await asyncio.create_subprocess_shell(
            ffprobe_query, stdout=asyncio.subprocess.PIPE
        )
        data, _ = await process.communicate()
        return await parse_file_info_to_objects(json.loads(data.decode("utf-8")))

    except KeyError:
        logger.error("ffprobe erorr")
        raise ErrorDuringProbe()


async def parse_file_info_to_objects(file_info: dict) -> VideoStreamInfoSchema:
    stream_info = file_info["streams"]
    format_info = file_info["format"]
    video_info = VideoStreamInfoSchema(
        codec_name=stream_info[0]["codec_name"],
        format_name=format_info["format_name"],
        width=stream_info[0]["width"],
        height=stream_info[0]["height"],
        bit_rate=stream_info[0]["bit_rate"],
        audio=AudioStreamInfoSchema(
            codec_name=stream_info[1]["codec_name"],
            bit_rate=stream_info[1]["bit_rate"],
        ),
    )

    return video_info


def add_transcode_video_to_h264() -> str:
    return "-profile:v main -c:v libx264 -pix_fmt yuv420p "


def add_transcode_audio_to_aac() -> str:
    return "-c:a aac "


def add_resolution_resizing(new_height: str) -> str:
    return f"-vf scale=-1:{new_height} "


def create_attachment_id():
    """
    Generate uuid for video objects (low, quality video, high quality)

    Returns:
        _type_: _description_
    """
    name = str(uuid.uuid4())
    return name


async def generate_thumbnail(
    file_name: str, output_image_name: str, timestamp="00:00:01"
):
    config = f"ffmpeg -loglevel error -ss {timestamp} -i {file_name} -frames:v 1 -q:v 2 {output_image_name}"
    process = await asyncio.create_subprocess_shell(
        config, stderr=asyncio.subprocess.PIPE
    )
    _, err = await process.communicate()

    if err:
        logger.error(f"Error occured during thumbnail generating {err.decode('utf-8')}")
        raise ErorrDuringCompression()


async def create_compressing_config(
    video_info: VideoStreamInfoSchema,
    quality: Quality,
    file_name: str,
    output_name: str,
):
    config = f"ffmpeg -loglevel error -i {file_name} "
    if video_info.codec_name != "h264":
        config += add_transcode_video_to_h264()

    if video_info.audio.codec_name != "aac":
        config += add_transcode_audio_to_aac()

    if video_info.height >= quality.height:
        config += add_resolution_resizing(quality.height)

    config += f"-crf {quality.crf} -preset {quality.compress_preset} -tune {quality.tune} {output_name}"

    return config


async def start_compressing_the_video(config: str):
    process = await asyncio.create_subprocess_shell(
        config, stderr=asyncio.subprocess.PIPE
    )
    _, err = await process.communicate()

    if err:
        logger.error(f"Error occured during compression {err}")
        raise ErorrDuringCompression()


