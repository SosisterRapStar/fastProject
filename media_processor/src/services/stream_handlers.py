from streaming_form_data.targets import FileTarget, DirectoryTarget
import hashlib
import uuid
from pathlib import Path
import asyncio
from domain.entities import ImageEntity, VideoEntity
from config import logger
from pathlib import Path
from typing import List
import io


images_extentions = ("png", "jpeg", "jpg", "gif", "svg", "WebP")

# class VideoProcessingTargetWithSHA256(DirectoryTarget):
#     def __init__(self, directory_path: str, allow_overwrite: bool = True, *args, **kwargs):
#         super().__init__(directory_path, allow_overwrite, *args, **kwargs)
#         self.video_filenames = []
#         self.image_files = []

#     def on_start(self):
#         self._hash = hashlib.sha256()

#         if not self.multipart_filename:
#             return

#         self.multipart_filename = Path(self.multipart_filename).resolve().name
#         self.temporary_file_name = str(uuid.uuid4()) + self.multipart_filename
#         self._fd = open(
#             Path(self.directory_path) / self.temporary_file_name, self._mode
#         )

#     def on_data_received(self, chunk: bytes):
#         super().on_data_received(chunk)
#         self._hash.update(chunk)

#     def on_finish(self):
#         old_path = Path(self.directory_path) / self.temporary_file_name
#         new_file_name = (
#             f"{self._hash.hexdigest()}.{self.multipart_content_type.split('/')[1]}"
#         )
#         new_path = Path(self.directory_path) / new_file_name

#         old_path.rename(new_path)

#         self.multipart_filenames.append(
#             AttachmentEntity(
#                 messageId=self._hash.hexdigest(),
#                 mimeType=self.multipart_content_type,
#                 originalName=new_file_name,
#             )
#         )

#         self.multipart_content_types.append(self.multipart_content_type)
#         if self._fd:
#             self._fd.close()


class ProcessingTargetWithSHA256(DirectoryTarget):
    def __init__(
        self, directory_path: str, allow_overwrite: bool = True, *args, **kwargs
    ):
        super().__init__(directory_path, allow_overwrite, *args, **kwargs)
        self.video_filenames = []
        self.image_files = []
        self._bytes = None

    def on_start(self):
        print(self.multipart_filename, self.multipart_content_type)
        if self.multipart_filename.split(".")[-1] in images_extentions:
            logger.debug("Starting of dowloading image")
            self._hash = hashlib.sha256()
            self._bytes = io.BytesIO()
            self.multipart_filename = Path(self.multipart_filename).resolve().name

        else:
            logger.debug("Starting of dowloading image")
            self._hash = hashlib.sha256()
            if not self.multipart_filename:
                return

            self.multipart_filename = Path(self.multipart_filename).resolve().name
            self.temporary_file_name = str(uuid.uuid4()) + self.multipart_filename
            self._fd = open(
                Path(self.directory_path) / self.temporary_file_name, self._mode
            )

    def on_data_received(self, chunk: bytes):
        if self._bytes is not None:
            self._bytes.write(chunk)
        elif self._fd:
            self._fd.write(chunk)
        self._hash.update(chunk)

    def on_finish(self):
        if self._bytes:
            in_memory_image = self._bytes
            self.image_files.append(
                [
                    in_memory_image,
                    ImageEntity(
                        messageId=self._hash.hexdigest(),
                        mimeType=self.multipart_content_type,
                        originalName=self._hash.hexdigest()
                        + '.'+self.multipart_filename.split(".")[-1],
                        originalBytes=in_memory_image
                    ),
                ]
            )
            self._bytes = None

        elif self._fd:
            old_path = Path(self.directory_path) / self.temporary_file_name
            new_file_name = (
                f"{self._hash.hexdigest()}.{self.multipart_content_type.split('/')[1]}"
            )
            new_path = Path(self.directory_path) / new_file_name

            old_path.rename(new_path)

            self.video_filenames.append(
                VideoEntity(
                    messageId=self._hash.hexdigest(),
                    mimeType=self.multipart_content_type,
                    originalName=new_file_name,
                )
            )

            self.multipart_content_types.append(self.multipart_content_type)
            if self._fd:
                self._fd.close()


# Хэш берем для того, чтобы узнать есть ли такой файл в S3 по хэшам убираем дубликаты из S3, чтобы не лазить всегда в S3 делаем кэш


class TestTarget(DirectoryTarget):
    """DirectoryTarget writes (streams) the different inputs to an on-disk
    directory."""

    def on_finish(self):
        super().on_finish()
        logger.debug("Finishing parsing")

    @property
    def is_finished(self):
        return self._finished


class ImageProcessingTargetWithSHA256(FileTarget):
    pass
