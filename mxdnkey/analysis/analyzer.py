import os
import concurrent.futures
from tqdm import tqdm

from .bpm_detector import BPMDetector
from .key_detector import KeyDetector
# from .genre_classifier import GenreClassifier  # Uncomment if implemented
from mxdnkey.utils.logger import get_logger

logger = get_logger(__name__)

class AudioAnalyzer:
    def __init__(self):
        """
        Initializes the AudioAnalyzer with BPM and Key detectors.
        """
        self.bpm_detector = BPMDetector()
        self.key_detector = KeyDetector()
        # self.genre_classifier = GenreClassifier()  # Uncomment if implemented

    def analyze(self, audio_file):
        """
        Analyzes the audio file and returns a dictionary of results.
        """
        try:
            logger.info("Analyzing audio file: %s", audio_file.filepath)
            if audio_file.audio_data is None:
                audio_file.load_audio()
            logger.debug("Audio data loaded successfully.")

            results = {}

            # Define the analysis steps as a list of tuples: (Step Name, Analysis Function)
            tasks = [
                ("BPM Analysis", self.bpm_detector.detect_bpm),
                ("Key Analysis", self.key_detector.detect_key)
            ]

            # Use tqdm to show progress for this single-file analysis
            with tqdm(total=len(tasks), desc="Analyzing Audio", ncols=100) as pbar:
                for task_name, func in tasks:
                    # Call the analysis function.
                    result = func(audio_file.audio_data, audio_file.sample_rate)
                    # Use the first word of the task name as a friendly key (e.g. "BPM" or "Key")
                    key_name = task_name.split()[0]
                    results[key_name] = result

                    # Update the progress bar, optionally showing the most recent result.
                    pbar.set_postfix_str(f"{task_name}: {result}")
                    pbar.update(1)
        except Exception as e:
            logger.exception("Error analyzing audio file: %s", e)
            raise
        return results

    def analyze_file_wrapper(self, file_path):
        """
        Helper method that instantiates an AudioFile from the given file path and then calls analyze.
        """
        from mxdnkey.audio.audio_file import AudioFile  # Import here to avoid cyclic dependencies
        audio_file = AudioFile(file_path)
        return self.analyze(audio_file)

    def analyze_folder(self, folder_path):
        """
        Analyzes all audio files in the specified folder in parallel.
        Returns a dictionary that maps file paths to their analysis results.
        """
        # Define a set of allowed file extensions
        allowed_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.wma'}

        # List all files in the folder that have an allowed extension
        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in allowed_extensions
        ]
        logger.info("Found %d audio files in folder: %s", len(files), folder_path)

        results = {}
        # Use a ThreadPoolExecutor to parallelize the analysis across files.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit each audio file analysis task and build a dict mapping futures to file names.
            future_to_file = {
                executor.submit(self.analyze_file_wrapper, file_path): file_path for file_path in files
            }
            # Use tqdm to display progress on the overall folder analysis.
            for future in tqdm(concurrent.futures.as_completed(future_to_file),
                               total=len(future_to_file),
                               desc="Analyzing Folder", ncols=100):
                file_path = future_to_file[future]
                try:
                    data = future.result()
                    results[file_path] = data
                    logger.info("Analysis complete for %s", file_path)
                except Exception as exc:
                    logger.error("Error processing file %s: %s", file_path, exc)
        return results
