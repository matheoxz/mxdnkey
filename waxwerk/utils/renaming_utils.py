from waxwerk.dataclass.audio_file import AudioFile
import os
from waxwerk.utils.logger import get_logger

logger = get_logger(__name__)

class RenamingUtils:
    def rename_file(audio_file: AudioFile, ):
        """
        Renames the file based on its metadata.
        """
        logger.info("Renaming file: %s", audio_file._file_path)
        file_extension = os.path.splitext(audio_file._file_path)[1]

        new_file_path = audio_file.metadata["title"][0] + ".mp3"
        os.rename(audio_file._file_path, new_file_path)
        audio_file._file_path = new_file_path
        logger.info("File renamed to: %s", new_file_path)