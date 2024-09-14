# from ffmpeg import FFmpeg
# from asynccpu import ProcessTaskPoolExecutor
# from asyncffmpeg import FFmpegCoroutineFactory, StreamSpec
import asyncio
from dataclasses import dataclass
import json
from src.domain.events import (
    AttachmentProcessed,
    ProcessVideoFileFromClient,
    ProcessImageFileFromClient,
    ErrorEvent,
)
from src.domain.entities import VideoEntity, ImageEntity
import uuid
from src.config import logger, settings
from io import BytesIO
from PIL import Image
import concurrent.futures

pool = concurrent.futures.ProcessPoolExecutor()

@dataclass
class FileProcessor:
    async def __call__(
        self,
        command: ProcessVideoFileFromClient | ProcessImageFileFromClient,
        queue: asyncio.Queue,
    ) -> None:
        if isinstance(command, ProcessVideoFileFromClient):
            await self.video_compressor(video=command.attachment, queue=queue)
        else:
            await self.image_compressor(image_event=command, queue=queue)

    async def image_compressor(
        self, image_command: ProcessImageFileFromClient, queue: asyncio.Queue
    ):
        new_extention = "jpg"
        file_name_without_extention = image_command.attachment.originalName.split('.')[0]
        qualities = {
            "high": ImageQuality(width=1920, height=1080, coefficient=95),
            "medium": ImageQuality(width=576, height=1024, coefficient=80),
            "low": ImageQuality(width=160, height=160, coefficient=70),
            "thumbnail": ImageQuality(width=160, height=160, coefficient=70),
        }
        original_image_bytes = BytesIO(image_command.attachment.originalBytes)
        image = Image.open(original_image_bytes)
        original_width, original_height = image.size
        image_info = ImageInfo(width=original_width, height=original_height)

        output = {}
        for preset, quality in qualities.items():
            loop = asyncio.get_running_loop()
            logger.debug("Started process of image compression")
            output_name = preset+'_'+file_name_without_extention+'.'+new_extention
            task = loop.run_in_executor(pool, compress_image, image_info, quality, output_name)
            await task
            output[preset] = output_name
        
        image_command.attachment.imageHighQuality = output["high"]
        image_command.attachment.imageMediumQuality = output["medium"]
        image_command.attachment.imageLowQuality = output["low"]
        image_command.attachment.imageThumbnail = output["thumbnail"]
        
        await queue.put(image_command)

        

        
        

    async def video_compressor(self, video: VideoEntity, queue: asyncio.Queue):
        """
        Function that handling all process of compressing, using ffmpeg

        Args:
            event (AttachmentUploadedFromClient): Event entity that activates this func
            queue (asyncio.Queue): Async queue  for putting messages about processed videos
        """

        try:
            original_name = video.originalName

            logger.debug(f"Starting to compress the video video_path {original_name}")

            # There should be three presets for high, medium and low quality
            logger.debug("...")
            presets = {
                "high": Quality(height=1080),
                "medium": Quality(height=720),
                "low": Quality(height=360),
            }

            output = {}  # maps the name of the preset and the filename for this preset
            video_info = await get_video_info(file_name=base_dir + original_name)
            file_name_without_extension = original_name.split(".")[0]
            for preset, quality in presets.items():
                output_name = preset + "_" + file_name_without_extension + ".mp4"
                logger.debug(
                    f"starting compression of {original_name} to {preset} preset"
                )

                config = await create_compressing_config(
                    video_info=video_info,
                    quality=quality,
                    file_name=base_dir + original_name,
                    output_name=base_dir + output_name,
                )

                await start_compressing_the_video(config=config)
                output[preset] = output_name

            thumbnail_name = "tumbnail_" + file_name_without_extension + ".jpg"

            logger.debug(f"starting thumbnail generation for {original_name}")

            video_thumbnail = await generate_thumbnail(
                file_name=base_dir + original_name,
                output_image_name=base_dir + thumbnail_name,
            )

            video.videoMediumQuality = output["medium"]
            video.videoLowQuality = output["low"]
            video.videoHighQuality = output["high"]
            video.videoThumbnail = thumbnail_name

            event = AttachmentProcessed(attachment=video)
            await queue.put(event)

        except SubprocessErorr as e:
            logger.error("Error in compressing")
            await queue.put(ErrorEvent(err=e))

        except Exception as e:
            logger.error(f"Error in something else {e}")
            await queue.put(ErrorEvent(err=e))


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
base_dir = settings.base_dir


@dataclass
class ImageQuality:
    height: int
    width: int
    coefficient: int

@dataclass(frozen=True)
class ImageInfo:
    height: int
    width: int


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
    codec_name: str = None
    bit_rate: int = None


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
        logger.debug(data.decode("utf-8"))
        return await parse_file_info_to_objects(json.loads(data.decode("utf-8")))

    except KeyError:
        logger.error("ffprobe erorr")
        raise ErrorDuringProbe()


async def parse_file_info_to_objects(file_info: dict) -> VideoStreamInfoSchema:
    stream_info = file_info["streams"]
    logger.debug(stream_info)
    format_info = file_info["format"]
    logger.debug(format_info)
    video_info = VideoStreamInfoSchema(
        codec_name=stream_info[0]["codec_name"],
        format_name=format_info["format_name"],
        width=stream_info[0]["width"],
        height=stream_info[0]["height"],
        bit_rate=stream_info[0]["bit_rate"],
        audio=AudioStreamInfoSchema(
            codec_name=stream_info[1]["codec_name"],
            bit_rate=stream_info[1]["bit_rate"],
        )
        if len(stream_info) > 1
        else AudioStreamInfoSchema(),
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

def compress_image(image_info: ImageInfo, quality: ImageQuality, output_name: str, image: Image):
    if quality.height < image_info.height:
        image.thumbnail((quality.width, quality.height))
    image.save(output_name, format='JPEG', quality=quality.coefficient, optimize=True)
        
    

async def start_compressing_the_video(config: str):
    process = await asyncio.create_subprocess_shell(
        config, stderr=asyncio.subprocess.PIPE
    )
    _, err = await process.communicate()

    if err:
        logger.error(f"Error occured during compression {err}")
        raise ErorrDuringCompression()
