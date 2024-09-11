from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio


# TODO: доделать адаптеры, чтобы убрать зависимость от ффмпега
# TODO: сделать UoF чтобы формировать конфиги
@dataclass
class BaseCompressConfigInterface(ABC):
    @abstractmethod
    def add_resolution_resizing(new_height):
        raise NotImplementedError

    @abstractmethod
    def add_transcode_audio_to_aac():
        raise NotImplementedError

    @abstractmethod
    def add_transcode_video_to_h264():
        raise NotImplementedError


@dataclass
class Thumbnailer(ABC):
    @abstractmethod
    async def generate_video_thumbnail(file_name: str, output_name: str, timestamp):
        raise NotImplemented


@dataclass
class FFmpegThumbnailer(Thumbnailer):
    async def generate_video_thumbnail(
        file_name: str, output_image_name: str, timestamp="00:00:01"
    ):
        config = f"ffmpeg -ss {timestamp} -i {file_name} -frames:v 1 -q:v 2 {output_image_name}"
        await asyncio.create_subprocess_shell(config)


@dataclass
class FFmpeg(BaseCompressConfigInterface):
    def add_resolution_resizing(new_height: str) -> str:
        return f"-vf scale=-1:{new_height}"

    def add_transcode_audio_to_aac() -> str:
        return "-c:a aac"

    def add_transcode_video_to_h264() -> str:
        return "-profile:v main -c:v libx264 -pix_fmt yuv420p"
