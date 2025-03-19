#!/usr/bin/env python3
"""
Main entry point for the mxdnkey application.
Supports both CLI and GUI operation modes.
"""

import argparse
import sys

from mxdnkey.audio.audio_file import AudioFile
from mxdnkey.analysis.analyzer import AudioAnalyzer
import mxdnkey.config as config
from mxdnkey.utils.logger import get_logger

logger = get_logger(__name__)

def run_cli(audio_filepath):
    """
    Run the application in command-line mode with the provided audio file.
    """
    logger.info("Starting CLI analysis for file: %s", audio_filepath)
    try:
        # Create an AudioFile instance and load the file using the configured sample rate
        audio_file = AudioFile(audio_filepath)
        audio_file.load_audio(sr=config.SAMPLE_RATE)
        logger.debug("Audio file loaded successfully.")
        
        # Run the analysis using AudioAnalyzer
        analyzer = AudioAnalyzer()
        results = analyzer.analyze(audio_file)
        logger.info("Audio analysis completed.")
        
        # Print the results to the console
        print("Audio Analysis Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
    except Exception as e:
        logger.exception("Error processing file '%s': %s", audio_filepath, e)
        print(f"Error processing file '{audio_filepath}': {e}")

def run_gui():
    """
    Launch the graphical interface of the application.
    """
    logger.info("Launching GUI mode...")
    try:
        # Import here to avoid dependency issues if someone runs CLI only
        from mxdnkey.gui.main_window import MainWindow
        import tkinter as tk

        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.exception("Error launching GUI: %s", e)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="mxdnkey: A lightweight audio analysis tool for extracting BPM, Key, and more."
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to an audio file for CLI-based analysis."
    )
    args = parser.parse_args()

    if args.gui:
        run_gui()
    elif args.file:
        run_cli(args.file)
    else:
        logger.warning("No mode specified. Use --gui for the graphical interface or --file <path> for CLI analysis.")
        print("No mode specified. Use --gui for the graphical interface or --file <path> for CLI analysis.")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
