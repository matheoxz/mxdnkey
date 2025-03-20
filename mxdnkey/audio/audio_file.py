"""
AudioFile Module
================

Represents a music file with the following properties:
  • title (str)
  • album (str)
  • artist (str)
  • BPM (float)         - Beats per Minute
  • Key (dict)          - Detected key (e.g., {"key": "C major", "camelot": "8B"})
  • file_path (str)
  • metadata (dict)
  • sample_rate (number)
  • rating (int, 0 to 5)
  • audio_data (numpy array)

The object provides getters and setters for all these properties.
Metadata (title, album, artist, etc.) are extracted during initialization.
Audio data (and sample_rate) are loaded on-demand via load_audio().
Audio analysis (BPM and Key) is performed by calling analyze(), which triggers
the external Analyzer class. A progress callback (0–100%) is used to update GUI elements.
"""

import os
import mutagen
import librosa
import numpy as np
from mxdnkey.utils.logger import get_logger

logger = get_logger(__name__)

class AudioFile:
    def __init__(self, file_path):
        logger.debug("Initializing AudioFile with path: %s", file_path)
        if not os.path.exists(file_path):
            logger.error("File '%s' does not exist.", file_path)
            raise FileNotFoundError(f"{file_path} does not exist.")

        self._file_path = file_path
        self.metadata = self._load_metadata()

        # Audio will be loaded on-demand.
        self.audio_data = None
        self.sample_rate = None

        # Initialize analysis properties.
        self._bpm = None
        self._key = None

        # User rating property (default 0).
        self._rating = 0

    def _load_metadata(self):
        """
        Loads metadata from the file using mutagen's easy mode.
        Returns the metadata object (or None if not found).
        """
        try:
            logger.debug("Loading metadata for file: %s", self._file_path)
            tag = mutagen.File(self._file_path, easy=True)
            if tag is None:
                logger.debug("No metadata found for file: %s", self._file_path)
            else:
                logger.debug("Metadata successfully loaded.")
            return tag
        except Exception as err:
            logger.exception("Error loading metadata: %s", err)
            return None

    def load_audio(self):
        """
        Loads the audio data and sample rate using librosa.
        """
        try:
            logger.info("Loading audio data from file: %s", self._file_path)
            self.audio_data, self.sample_rate = librosa.load(self._file_path, sr=None)
            logger.debug("Audio loaded with sample rate: %s", self.sample_rate)
        except Exception as e:
            logger.exception("Error loading audio: %s", e)
            raise

    def analyze(self, progress_callback=None):
        """
        Triggers analysis of audio data for BPM and Key.
        
        If audio data is not already loaded, it loads it. Then it calls the external
        Analyzer class to perform analysis, updating the BPM and Key properties.
        
        Parameters:
          progress_callback (function): Optional callback receiving progress (0-100).
          
        NOTE: This method does NOT run during __init__; it must be triggered explicitly.
        """
        if self.audio_data is None:
            self.load_audio()
        from mxdnkey.analysis.analyzer import AudioAnalyzer
        analyzer = AudioAnalyzer()
        logger.info("Starting analysis for file: %s", self._file_path)
        analyzer.analyze(self, progress_callback)
        logger.info("Analysis complete for file: %s", self._file_path)

    def get_audio_form(self, size):
        """
        Returns a version of the audio data truncated (or padded) to 'size' samples.
        Useful for generating a waveform for visualization.
        """
        if self.audio_data is None:
            logger.info("Audio data not loaded; calling load_audio() to generate waveform.")
            self.load_audio()
        current_length = len(self.audio_data)
        if current_length >= size:
            logger.debug("Truncating audio to %s samples for waveform.", size)
            return self.audio_data[:size]
        else:
            logger.debug("Padding audio to %s samples for waveform.", size)
            return np.pad(self.audio_data, (0, size - current_length), mode='constant')

    def _get_metadata_tag(self, *tag_names):
        """
        Helper to retrieve the first non-empty metadata tag among tag_names.
        Supports both ID3 tags (e.g., TIT2) and lowercase keys.
        Returns the tag value as a string or "Unknown" if not found.
        """
        if self.metadata is None:
            logger.debug("No metadata available for file: %s", self._file_path)
            return "Unknown"
        for tag in tag_names:
            try:
                value = self.metadata.get(tag)
                if value:
                    if isinstance(value, list):
                        logger.debug("Found metadata tag %s: %s", tag, value[0])
                        return value[0]
                    else:
                        logger.debug("Found metadata tag %s: %s", tag, value)
                        return value
            except Exception as e:
                logger.debug("Error retrieving metadata tag %s: %s", tag, e)
        logger.info("No metadata found among tags: %s", tag_names)
        return "Unknown"

    # ------------------ Property Getters and Setters ---------------------
    @property
    def file_path(self):
        """Returns the file path of the audio file."""
        logger.debug("Accessing file_path property.")
        return self._file_path

    @property
    def title(self):
        """Title extracted from metadata."""
        return self._get_metadata_tag("title", "TIT2")

    @property
    def artist(self):
        """Artist extracted from metadata."""
        return self._get_metadata_tag("artist", "TPE1")

    @property
    def album(self):
        """Album extracted from metadata."""
        return self._get_metadata_tag("album", "TALB")
    
    @property
    def genre(self):
        """Genre extracted from metadata."""
        return self._get_metadata_tag("genre", "TCON")

    @property
    def BPM(self):
        """The calculated BPM (float)."""
        return self._bpm

    @BPM.setter
    def BPM(self, value):
        logger.info("Setting BPM to %s", value)
        self._bpm = float(value)

    @property
    def Key(self):
        """The detected key as a dictionary e.g. {'key': 'C major', 'camelot': '8B'}."""
        return self._key

    @Key.setter
    def Key(self, value):
        logger.info("Setting Key to %s", value)
        self._key = value

    @property
    def Rating(self):
        """User rating (int, between 0 and 5)."""
        logger.debug("Accessing Rating property: %s", self._rating)
        return self._rating

    @Rating.setter
    def Rating(self, value):
        if not isinstance(value, (int, float)) or not (0 <= value <= 5):
            logger.error("Invalid Rating: %s. Must be between 0 and 5.", value)
            raise ValueError("Rating must be between 0 and 5.")
        logger.info("Setting Rating to %s", value)
        self._rating = int(value)
