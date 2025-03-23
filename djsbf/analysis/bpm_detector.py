import librosa
from djsbf.utils.logger import get_logger

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
            return tempo[0]
            
        except Exception as e:
            logger.exception("Error detecting BPM: %s", e)
            raise

    def detect_tempo(self, audio_data, sample_rate):
        """
        Detects the BPM of the audio data using librosa's improved beat tracking.
        Returns the detected BPM as a float.
        """
        try:
            logger.debug("Detecting BPM for audio data with sample rate: %s", sample_rate)
            
            # Step 1: Compute the onset envelope
            onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
            logger.debug("Onset envelope computed. First few values: %s", onset_env[:5])

            # Step 2: Estimate the global tempo using the onset envelope.
            # librosa.beat.tempo returns an array; we take the first estimate.
            tempo_arr = librosa.beat.tempo(onset_envelope=onset_env, sr=sample_rate)
            bpm = tempo_arr[0]

            logger.debug("Detected BPM (improved): %s", bpm)
            return bpm  
            
        except Exception as e:
            logger.exception("Error detecting BPM: %s", e)
            raise   

