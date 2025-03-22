"""
Configuration file for the mxdnkey application.
Define application-wide settings and tunable parameters here.
"""

# Audio processing settings
SAMPLE_RATE = 22050    # Default sample rate for loading audio files

# BPM detection parameters
BPM_BUFFER_SIZE = 4096  # (Optional) Buffer size for beat tracking, adjust as needed

# Key detection parameters
KEY_DETECTION_THRESHOLD = 0.0  # Placeholder if you want to implement threshold-based key detection

# Logging configuration
LOG_LEVEL = "DEBUG"    # Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

# More configuration settings can be added here in the future.
