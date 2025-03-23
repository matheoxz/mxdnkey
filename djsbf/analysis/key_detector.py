import numpy as np
import librosa
from djsbf.utils.logger import get_logger
from djsbf.enums import Tonic, Mode
from djsbf.dataclass.audio_file import AudioFile
from djsbf.dataclass.key import Key

class KeyDetector:
    def __init__(self):
        # Key templates based on Krumhansl’s experiments
        self.major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                                       2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        self.minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                       2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        # Normalize the profiles
        self.major_profile = self.major_profile / np.sum(self.major_profile)
        self.minor_profile = self.minor_profile / np.sum(self.minor_profile)
        
        # List of keys corresponding to each pitch class index.
        self.keys = list(Tonic)
    
    def detect_key(self, audio_data, sample_rate):
        # Compute a chromagram from the audio signal.
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        # Average over time to form a single 12-element vector.
        chroma_mean = np.mean(chroma, axis=1)
        
        # Normalize the chroma vector.
        if np.sum(chroma_mean) > 0:
            chroma_norm = chroma_mean / np.sum(chroma_mean)
        else:
            chroma_norm = chroma_mean
        
        best_corr = -np.inf
        best_key: Tonic = None
        best_mode: Mode = None  
        # Loop through all 12 keys
        for i in range(12):
            # Rotate (shift) the key templates according to the candidate key.
            major_rot = np.roll(self.major_profile, i)
            minor_rot = np.roll(self.minor_profile, i)
            
            # Compute correlation between the chroma vector and the rotated templates.
            corr_major = np.corrcoef(chroma_norm, major_rot)[0, 1]
            corr_minor = np.corrcoef(chroma_norm, minor_rot)[0, 1]
            
            if corr_major > best_corr:
                best_corr = corr_major
                best_key = self.keys[i]
                best_mode = Mode.MAJOR
            if corr_minor > best_corr:
                best_corr = corr_minor
                best_key = self.keys[i]
                best_mode = Mode.MINOR
        
        # Return a dictionary containing the detected key
        return Key(tonic=best_key, mode=best_mode) if best_key else None
