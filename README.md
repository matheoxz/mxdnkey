# djsbf - DJ music library organizer

## Overview
mxdnkey is a Python-based application designed to organize and analyze music files in a user's library. It provides a command-line interface for managing audio files, analyzing metadata, and performing various audio analyses.

## Features
- Organize music files into folders based on metadata
- Analyze audio files to extract metadata and perform various audio analyses
- Provide a command-line interface for managing audio files
- Provide a GUI for managing audio files

# Project Structure

mxdnkey/
├── mxdnkey/
│   ├── __init__.py
│   ├── main.py                   # Application entry point (initializes UI and/or CLI)
│   ├── config.py                 # Global configuration variables
│   ├── audio/
│   │   ├── __init__.py
│   │   └── audio_file.py         # Defines the AudioFile class to handle file loading and metadata
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── analyzer.py           # The main AudioAnalyzer class that coordinates analyses
│   │   ├── bpm_detector.py       # Contains BPMDetector class/functions (e.g., using librosa.beat.beat_track)
│   │   ├── key_detector.py       # Contains KeyDetector class/functions (e.g., analyze chroma features)
│   │   └── genre_classifier.py   # Contains GenreClassifier class/functions (e.g., using lightweight ML or rules)
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py        # Contains the UI logic if you choose to use Tkinter
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Utility for logging events (wraps the Python logging module)
│
├── tests/                        # Unit and integration tests
│   ├── __init__.py
│   ├── test_audio_file.py
│   ├── test_bpm_detector.py
│   ├── test_key_detector.py
│   └── test_genre_classifier.py
│
├── requirements.txt              # List all external dependencies
└── README.md                     # Overview and usage instructions
