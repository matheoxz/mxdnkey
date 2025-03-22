"""
AudioProcessor: Utility functions for audio processing.
Handles resampling (speed changes), time-stretching, and BPM validation.
"""

import numpy as np
import logging
from waxwerk.analysis.bpm_detector import BPMDetector

logger = logging.getLogger(__name__)

class AudioProcessor:
    @staticmethod
    def get_valid_bpm(audio_file):
        """
        Returns a valid BPM value from the audio_file.
        If the file’s BPM attribute is not valid, uses BPMDetector as a fallback.
        """
        if hasattr(audio_file, "BPM") and audio_file.BPM is not None and audio_file.BPM > 0:
            logger.debug("Using provided BPM: %s", audio_file.BPM)
            return audio_file.BPM
        try:
            detector = BPMDetector()
            # detector.detect_bpm is assumed to return an array-like value.
            bpm = detector.detect_bpm(audio_file.audio_data, audio_fsile.sample_rate)
            logger.info("Fallback BPM detection returned: %s", bpm)
            return bpm or 120
        except Exception as e:
            logger.error("Error in BPM detection: %s", e)
            return 120

    @staticmethod
    def apply_speed_change(original_audio, current_rate):
        """
        Applies a simple resampling-based speed change (quality-compromised but CPU-friendly).
        If current_rate is 1.0, returns the original audio.
        """
        if current_rate == 1.0:
            logger.debug("No speed change applied, current_rate equals 1.0")
            return original_audio
        new_length = int(len(original_audio) / current_rate)
        indices = np.clip(np.arange(new_length) * current_rate, 0, len(original_audio) - 1).astype(int)
        logger.debug("Applying speed change: current_rate=%s, new_length=%s", current_rate, new_length)
        return original_audio[indices]

    @staticmethod
    def process_stretched_audio(audio, sample_rate, current_rate, time_stretcher):
        """
        Time-stretches the audio using the provided time_stretcher.
        Only processes if the current_rate differs significantly from 1.0.
        """
        if abs(current_rate - 1.0) < 0.01:
            logger.debug("No time-stretching needed, current_rate ~ 1.0")
            return audio
        try:
            stretched = time_stretcher.stretch_audio(audio, sample_rate, current_rate)
            logger.info("Audio successfully time-stretched with rate %s", current_rate)
            return stretched
        except Exception as e:
            logger.error("Time-stretching failed: %s", e)
            return audio
