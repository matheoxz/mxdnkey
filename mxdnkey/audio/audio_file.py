import os
import mutagen
import librosa
from mxdnkey.utils.logger import get_logger

logger = get_logger(__name__)

class AudioFile:
    def __init__(self, filepath):
        logger.debug("Searching file %s.", filepath)
        self.filepath = filepath
        if not os.path.exists(filepath):
            logger.error("File %s does not exist.", filepath)
            raise FileNotFoundError(f"{filepath} does not exist.")
        else:
            logger.debug("File %s found.", filepath)
        self.metadata = self._load_metadata()
        self.audio_data, self.sample_rate = None, None

    def _load_metadata(self):
        """
        Loads metadata from the audio file using mutagen.
        Returns the metadata object if successful, or None if an error occurs.
        """
        try:
            logger.debug("Loading metadata for file: %s", self.filepath)
            tag = mutagen.File(self.filepath)
            logger.debug("Metadata loaded successfully! ")
            return tag
        except Exception as err:
            logger.exception("Error loading metadata: %s", err)
            return None

    def load_audio(self):
        """
        Loads the audio data from the file using librosa.
        Returns the audio data and sample rate if successful, or raises an exception if an error occurs.
        """
        try:
            logger.info("Loading audio data from file: %s", self.filepath)
            self.audio_data, self.sample_rate = librosa.load(self.filepath)
            logger.debug("Audio data loaded. Sample rate: %s", self.sample_rate)
        except Exception as e:
            logger.exception("Error loading audio: %s", e)
            raise
