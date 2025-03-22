"""
AudioAnalyzer Module
======================

The AudioAnalyzer performs analysis on an AudioFile instance:
  - BPM analysis (using a beat-tracking algorithm).
  - Key analysis (using a Krumhansl–Schmuckler style approach).

It reports progress via a progress_callback, which (if provided) is called at the completion
of each analysis step (progress as a percentage: 50% after BPM, 100% after Key).
"""

import numpy as np
from .bpm_detector import BPMDetector
from .key_detector import KeyDetector
from waxwerk.utils.logger import get_logger

logger = get_logger(__name__)

class AudioAnalyzer:
    def __init__(self):
        """
        Initializes the AudioAnalyzer with detectors for BPM and Key.
        """
        self.bpm_detector = BPMDetector()
        self.key_detector = KeyDetector()

    def analyze(self, audio_file, progress_callback=None):
        """
        Analyzes audio_file for BPM and Key.
        
        Parameters:
          audio_file: an instance of AudioFile.
          progress_callback: Optional function that accepts a numeric percentage (0-100).
        
        This method calls the appropriate detectors and updates the audio_file's BPM and Key properties.
        """
        logger.info("Starting analysis on file: %s", audio_file.file_path)
        if audio_file.audio_data is None:
            audio_file.load_audio()
        results = {}
        # List of analysis tasks: each tuple is (task_name, analysis_function)
        tasks = [("BPM", self.bpm_detector.detect_bpm),
                 ("Key", self.key_detector.detect_key)]
        total_tasks = len(tasks)
        for i, (task, func) in enumerate(tasks):
            result = func(audio_file.audio_data, audio_file.sample_rate)
            results[task] = result
            if task == "BPM":
                # Expect detector returns array; take first element.
                audio_file.BPM = result
            elif task == "Key":
                audio_file.Key = result
            if progress_callback:
                # Update progress: evenly distribute progress among tasks.
                progress_callback((i + 1) * 100 / total_tasks)
        logger.info("Completed analysis on file: %s", audio_file.file_path)
        return results
