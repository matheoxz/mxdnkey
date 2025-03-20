"""
PlayerWindow: A Tkinter Toplevel window for audio playback,
visualization, and interactive controls such as seeking, volume,
BPM, and key adjustments.

Non-GUI audio processing has been delegated to the AudioProcessor utility.
"""

import threading
import numpy as np
import tkinter as tk
from tkinter import messagebox
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from logging import getLogger

from mxdnkey.utils.audio_processor import AudioProcessor
from mxdnkey.utils.simple_time_stretcher import SimpleTimeStretcher
from mxdnkey.audio.audio_file import AudioFile

logger = getLogger(__name__)

class PlayerWindow(tk.Toplevel):
    def __init__(self, parent, audio_file: AudioFile):
        """
        Initialize the PlayerWindow with the given audio_file.
        audio_file is expected to have attributes:
           - audio_data, sample_rate,
           - title, artist, album (and optionally BPM)
        """
        super().__init__(parent)
        self.title("mxdnkey Player")
        self.geometry("800x650")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        logger.debug("Initializing PlayerWindow for file: %s", audio_file.file_path)

        self.audio_file = audio_file
        self.pa = pyaudio.PyAudio()
        self._init_audio_properties()
        self._init_playback_attributes()
        self._init_bpm_and_stretcher()
        self.create_widgets()

        self.draw_waveform()
        self.start_playback()
        self.bind_seek_events()

    def _init_audio_properties(self):
        """Ensure audio data is loaded and set property variables."""
        if self.audio_file.audio_data is None:
            try:
                logger.debug("Loading audio data...")
                self.audio_file.load_audio()
            except Exception as e:
                logger.error("Failed to load audio: %s", e)
                messagebox.showerror("Error", f"Failed to load audio: {str(e)}")
                self.destroy()
                return
        self.original_audio = self.audio_file.audio_data.astype(np.float32)
        self.sample_rate = self.audio_file.sample_rate
        self.total_duration = len(self.original_audio) / self.sample_rate

    def _init_playback_attributes(self):
        """Initialize variables used for playback and seeking."""
        self.current_position = 0     # in samples
        self.is_playing = False
        self.stream = None
        self.volume = 0.6             # Default volume (60%)
        self.seek_lock = threading.Lock()
        self.modified_audio = None    # Buffer for speed-changed audio
        self.modified_pos = 0

    def _init_bpm_and_stretcher(self):
        """Set BPM and initialize a SimpleTimeStretcher."""
        self.original_bpm = AudioProcessor.get_valid_bpm(self.audio_file)
        self.time_stretcher = SimpleTimeStretcher(self.original_bpm)
        self.current_rate = 1.0

    def create_widgets(self):
        """Create all GUI components."""
        self._create_waveform_display()
        self._create_metadata_display()
        self._create_time_display()
        self._create_control_frame()
        # Schedule regular progress updates.
        self.after(100, self.update_progress)

    def _create_waveform_display(self):
        """Creates the waveform display using a Matplotlib Figure."""
        self.figure = plt.Figure(figsize=(8, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(pady=10)

    def _create_metadata_display(self):
        """Creates a label to display track metadata."""
        meta_text = f"{self.audio_file.title or 'Unknown'} - {self.audio_file.artist or 'Unknown'} - {self.audio_file.album or 'Unknown'}"
        self.meta_label = tk.Label(self, text=meta_text)
        self.meta_label.pack(pady=5)

    def _create_time_display(self):
        """Creates a label to display elapsed and total time."""
        self.time_label = tk.Label(self, text="00:00 / 00:00")
        self.time_label.pack()

    def _create_control_frame(self):
        """Creates playback controls and volume/BPM/key sliders."""
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)

        # Play/Pause Button
        self.play_btn = tk.Button(control_frame, text="⏸", command=self.toggle_playback)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        # Volume Control
        volume_frame = tk.Frame(control_frame)
        volume_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(volume_frame, from_=0.0, to=2.0, resolution=0.1,
                                      orient=tk.HORIZONTAL, command=self.update_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(side=tk.LEFT)

        # BPM Control
        bpm_frame = tk.Frame(control_frame)
        bpm_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(bpm_frame, text="BPM:").pack(side=tk.LEFT)
        self.bpm_slider = tk.Scale(bpm_frame, from_=-10, to=10, orient=tk.HORIZONTAL,
                                   command=self.update_bpm, resolution=0.1, length=150)
        self.bpm_slider.set(0)
        self.bpm_slider.pack(side=tk.LEFT)
        self.bpm_display = tk.Label(bpm_frame, text=f"{self.original_bpm:.2f} BPM")
        self.bpm_display.pack(side=tk.LEFT, padx=5)

        # Key Control (Placeholder)
        key_frame = tk.Frame(control_frame)
        key_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(key_frame, text="Key:").pack(side=tk.LEFT)
        self.key_slider = tk.Scale(key_frame, from_=-6, to=6, orient=tk.HORIZONTAL,
                                   command=self.update_key, resolution=1)
        self.key_slider.set(0)
        self.key_slider.pack(side=tk.LEFT)

    def bind_seek_events(self):
        """Binds mouse events on the waveform canvas for seeking."""
        widget = self.canvas.get_tk_widget()
        widget.bind("<Button-1>", self.on_click_seek)
        widget.bind("<B1-Motion>", self.on_drag_seek)
        widget.bind("<ButtonRelease-1>", self.on_release_seek)

    def draw_waveform(self):
        """Draw the full waveform (downsampled for performance) on the Matplotlib canvas."""
        logger.debug("Drawing waveform...")
        self.ax.clear()
        downsample_factor = max(1, len(self.original_audio) // 10000)
        self.vis_audio = self.original_audio[::downsample_factor]
        self.ax.plot(self.vis_audio, alpha=0.5)
        self.seek_line = self.ax.axvline(0, color='r', linewidth=1)
        self.ax.set_xlim(0, len(self.vis_audio))
        self.canvas.draw()
        self.sample_ratio = len(self.original_audio) / len(self.vis_audio)
        logger.info("Waveform drawn with sample_ratio: %s", self.sample_ratio)

    def start_playback(self):
        """Initializes and starts audio playback using PyAudio."""
        logger.info("Starting playback...")
        self.is_playing = True
        self.play_btn.config(text="⏸")
        self.stream = self.pa.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            output=True,
            stream_callback=self.audio_callback
        )

    def audio_callback(self, in_data, frame_count, time_info, status):
        """
        PyAudio stream callback.
        Reads a chunk of audio data (modified if necessary) and applies volume.
        """
        with self.seek_lock:
            if self.modified_audio is not None:
                end_pos = self.modified_pos + frame_count
                if end_pos > len(self.modified_audio):
                    end_pos = len(self.modified_audio)
                chunk = self.modified_audio[self.modified_pos:end_pos]
                self.modified_pos = end_pos % len(self.modified_audio)
                self.current_position = int(self.modified_pos / self.current_rate)
            else:
                end_pos = self.current_position + frame_count
                if end_pos > len(self.original_audio):
                    end_pos = len(self.original_audio)
                chunk = self.original_audio[self.current_position:end_pos]
                self.current_position = end_pos % len(self.original_audio)

        # Apply volume control.
        chunk = chunk * self.volume
        if len(chunk) < frame_count:
            chunk = np.pad(chunk, (0, frame_count - len(chunk)), mode='constant')
        return (chunk.astype(np.float32).tobytes(), pyaudio.paContinue)

    def toggle_playback(self):
        """Toggle between play and pause states."""
        self.is_playing = not self.is_playing
        self.play_btn.config(text="⏸" if self.is_playing else "▶")
        if self.is_playing:
            if self.stream.is_stopped():
                self.stream.start_stream()
            logger.debug("Resuming playback.")
        else:
            if self.stream.is_active():
                self.stream.stop_stream()
            logger.debug("Playback paused.")

    def update_volume(self, value):
        """Update playback volume."""
        self.volume = float(value)
        logger.debug("Volume updated to: %s", self.volume)

    def update_bpm(self, value):
        """Update BPM according to the slider and apply speed change."""
        try:
            bpm_change = float(value)
            self.current_rate = 1.0 + (bpm_change / 100)
            current_bpm = self.original_bpm * self.current_rate
            self.bpm_display.config(text=f"{current_bpm:.1f} BPM")
            # Update modified audio buffer using AudioProcessor.
            self.modified_audio = AudioProcessor.apply_speed_change(self.original_audio, self.current_rate)
            self.modified_pos = int(self.current_position * self.current_rate)
            logger.info("BPM updated: slider_change=%s, current_rate=%s", bpm_change, self.current_rate)
        except Exception as e:
            logger.error("Error updating BPM: %s", e)

    def update_key(self, value):
        """Placeholder for handling key shifting."""
        logger.info("Key shift: %s semitones", value)
        # Future implementation: apply pitch shifting.

    def update_progress(self):
        """Update the seek line and time label based on current playback position."""
        with self.seek_lock:
            current_pos = self.current_position
        if self.original_audio is not None and self.sample_rate:
            duration = self.total_duration
            current_time = current_pos / self.sample_rate
            if hasattr(self, "seek_line"):
                vis_position = current_pos / self.sample_ratio
                self.seek_line.set_xdata([vis_position, vis_position])
                self.canvas.draw_idle()
            self.time_label.config(text=f"{self.format_time(current_time)} / {self.format_time(duration)}")
        self.after(10, self.update_progress)

    def format_time(self, seconds):
        """Convert seconds to mm:ss format."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def on_close(self):
        """Clean up: stop stream, terminate PyAudio, then close the window."""
        logger.info("Closing PlayerWindow...")
        self.is_playing = False
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logger.error("Error closing stream: %s", e)
        try:
            self.pa.terminate()
        except Exception as e:
            logger.error("Error terminating PyAudio: %s", e)
        self.destroy()

    def on_click_seek(self, event):
        """Handle initial click on the waveform for seeking."""
        self._update_seek_position(event.x)

    def on_drag_seek(self, event):
        """Handle dragging on the waveform for seeking."""
        self._update_seek_position(event.x)

    def on_release_seek(self, event):
        """Finalize seeking when user releases the mouse button."""
        self._update_seek_position(event.x)

    def _update_seek_position(self, x_pixel):
        """Convert a canvas x-coordinate to a sample position and update playback."""
        try:
            # Convert pixel coordinate to data coordinate via Matplotlib transformation
            x_data = self.ax.transData.inverted().transform((x_pixel, 0))[0]
            x_data = max(0, min(x_data, len(self.vis_audio)))
            vis_position = int(x_data)
            actual_position = int(vis_position * self.sample_ratio)
            with self.seek_lock:
                if self.modified_audio is not None:
                    self.modified_pos = int(actual_position * self.current_rate)
                    self.current_position = actual_position
                else:
                    self.current_position = actual_position
                    self.modified_pos = int(actual_position * self.current_rate)
            logger.debug("Seek position updated: vis=%s, actual=%s", vis_position, actual_position)
            if self.is_playing:
                self.restart_playback()
        except Exception as e:
            logger.error("Error updating seek position: %s", e)

    def restart_playback(self):
        """Restart the audio stream to apply the new seek position."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logger.error("Error restarting playback: %s", e)
        self.start_playback()