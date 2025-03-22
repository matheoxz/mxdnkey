import numpy as np
import librosa

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
        self.keys = ["C", "C#", "D", "D#", "E", "F",
                     "F#", "G", "G#", "A", "A#", "B"]
        
        # Mapping musical keys to Camelot Wheel notation
        # For major keys (commonly designated as "B")
        self.camelot_major = {
            "C": "8B",  "C#": "3B", "D": "10B", "D#": "5B",
            "E": "12B", "F": "7B",  "F#": "2B", "G": "9B",
            "G#": "4B", "A": "11B", "A#": "6B", "B": "1B"
        }
        
        # For minor keys (commonly designated as "A")
        self.camelot_minor = {
            "C": "5A",  "C#": "12A", "D": "7A", "D#": "2A",
            "E": "9A",  "F": "4A",  "F#": "11A", "G": "6A",
            "G#": "1A", "A": "8A",   "A#": "3A", "B": "10A"
        }
    
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
        best_key = None
        best_mode = None  # 'major' or 'minor'
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
                best_mode = "major"
            if corr_minor > best_corr:
                best_corr = corr_minor
                best_key = self.keys[i]
                best_mode = "minor"
        
        # Map to Camelot Wheel notation.
        if best_mode == "major":
            camelot = self.camelot_major.get(best_key, "N/A")
        else:
            camelot = self.camelot_minor.get(best_key, "N/A")
        
        # Return a dictionary containing the detected key and its Camelot mapping.
        return {"key": f"{best_key} {best_mode}", "camelot": camelot}
