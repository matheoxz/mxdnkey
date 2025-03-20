class SimpleTimeStretcher:
    def __init__(self, original_bpm):
        self.original_bpm = original_bpm
        self.current_rate = 1.0
        
    def calculate_rate(self, bpm_change_percent):
        """Calculate playback rate based on BPM change percentage"""
        # Convert percentage to multiplier (e.g., +10% = 1.1)
        rate = 1.0 + (bpm_change_percent / 100)
        return rate