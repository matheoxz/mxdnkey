import tkinter as tk
import os
import time

import simpleaudio as sa
from pydub import AudioSegment
from logging import getLogger

logger = getLogger(__name__)

###########################
# Player window for playback and visualization
###########################
class PlayerWindow(tk.Toplevel):
    def __init__(self, master, file_path):

        AudioSegment.converter = "../ff/ffmpeg.exe"
        AudioSegment.ffmpeg = "../ff/ffmpeg.exe"

        print("############################################")
        print("Opening PlayerWindow for file: %s", file_path)
        print("############################################")

        super().__init__(master)
        self.title("Player: " + os.path.basename(file_path))
        self.geometry("600x400")
        self.file_path = file_path

        # Load the audio for playback and obtain the duration (in ms)
        self.audio_segment = AudioSegment.from_file(file_path)
        self.duration_ms = len(self.audio_segment)
        self.playback_position = 0  # in milliseconds
        self.play_obj = None
        self.is_paused = False
        self.play_start_time = None

        # Create a canvas for waveform visualization (here we’ll simply draw a moving red line).
        self.canvas = tk.Canvas(self, bg="white", height=200)
        self.canvas.pack(fill="x", padx=10, pady=10)
        # Draw a playhead (red vertical line). This line will move over time.
        self.playhead = self.canvas.create_line(0, 0, 0, self.canvas.winfo_reqheight(), fill="red", width=2)

        # Control buttons frame (Play, Pause, Stop)
        controls_frame = tk.Frame(self)
        controls_frame.pack(pady=10)

        self.play_button = tk.Button(controls_frame, text="Play", command=self.play_audio)
        self.play_button.pack(side="left", padx=5)
        self.pause_button = tk.Button(controls_frame, text="Pause", command=self.pause_audio)
        self.pause_button.pack(side="left", padx=5)
        self.stop_button = tk.Button(controls_frame, text="Stop", command=self.stop_audio)
        self.stop_button.pack(side="left", padx=5)

        # Start updating the playhead position
        self.update_playhead()

    def play_audio(self):
        """Start (or resume) audio playback from the current playback_position."""
        # If already playing, do nothing.
        if self.play_obj and self.play_obj.is_playing():
            return

        # Resume playback from the recorded position
        segment = self.audio_segment[self.playback_position:]
        raw_data = segment.raw_data
        num_channels = segment.channels
        bytes_per_sample = segment.sample_width
        sample_rate = segment.frame_rate

        self.play_obj = sa.play_buffer(raw_data, num_channels, bytes_per_sample, sample_rate)
        # Record the time at which the playback starts/resumes.
        self.play_start_time = time.time()
        self.is_paused = False

    def pause_audio(self):
        """Pause playback by stopping the current audio and recording the elapsed time."""
        if self.play_obj and self.play_obj.is_playing():
            self.play_obj.stop()
            elapsed = (time.time() - self.play_start_time) * 1000  # Convert to milliseconds
            self.playback_position += int(elapsed)
            self.is_paused = True

    def stop_audio(self):
        """Stop playback and reset the playback_position."""
        if self.play_obj:
            self.play_obj.stop()
        self.playback_position = 0
        self.is_paused = False

    def update_playhead(self):
        """Updates the red playhead position according to the current playback time."""
        if self.play_obj and self.play_obj.is_playing():
            elapsed = (time.time() - self.play_start_time) * 1000  # in ms
            current_time = self.playback_position + elapsed
        else:
            current_time = self.playback_position

        canvas_width = self.canvas.winfo_width()
        if self.duration_ms > 0:
            pos = int(canvas_width * current_time / self.duration_ms)
        else:
            pos = 0

        # Update playhead coordinates: vertical line at x=pos
        self.canvas.coords(self.playhead, pos, 0, pos, self.canvas.winfo_height())
        # Schedule the next update
        self.after(50, self.update_playhead)