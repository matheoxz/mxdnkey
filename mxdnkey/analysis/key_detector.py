import numpy as np
import librosa
from mxdnkey.utils.logger import get_logger

logger = get_logger(__name__)
class KeyDetector:
    def __init__(self):
        pass

    def detect_key(self, audio_data, sample_rate):
        """
        Detects the key of the audio data using a simplified algorithm.
        Returns the detected key as a string.
        """
        try:
            logger.debug("Detecting key for audio data with sample rate: %s", sample_rate)
            # Compute a chromagram representation
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            chroma_avg = np.mean(chroma, axis=1)
        except Exception as e:
            logger.exception("Error detecting key: %s", e)
            raise

        # A simplified algorithm: map the highest energy pitch to a key.
        key_index = chroma_avg.argmax()
        try:
            # Mapping index to musical key (starting from C)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            detected_key = keys[key_index]
        except Exception as e:
            logger.exception("Error detecting key: %s", e)
            raise
        
        logger.debug("Detected key: %s", detected_key)
        return detected_key
