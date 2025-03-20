import numpy as np
import librosa

class TimeStretcher:
    def __init__(self, original_bpm):
        self.original_bpm = original_bpm
        self.current_rate = 1.0
        
    def calculate_stretch_rate(self, bpm_change_percent):
        """Calculate time stretch rate based on BPM change percentage"""
        target_bpm = self.original_bpm * (1 + bpm_change_percent/100)
        return self.original_bpm / target_bpm
    
    def stretch_audio(self, audio, sample_rate, rate):
        """Time-stretch audio using librosa (preserves pitch)"""
        if rate == 1.0:
            return audio
            
        return librosa.effects.time_stretch(audio, rate=rate)