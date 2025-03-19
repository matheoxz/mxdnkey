import librosa
from mxdnkey.utils.logger import get_logger

logger = get_logger(__name__)

class BPMDetector:
    def __init__(self):
        pass

    def detect_bpm(self, audio_data, sample_rate):
        """
        Detects the BPM of the audio data using librosa's beat tracking.
        Returns the detected BPM as a float.
        """
        try:
            logger.debug("Detecting BPM for audio data with sample rate: %s", sample_rate)
            # Use librosa’s built-in beat tracking
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            logger.debug("Detected BPM: %s", tempo)
            return tempo
        except Exception as e:
            logger.exception("Error detecting BPM: %s", e)
            raise
