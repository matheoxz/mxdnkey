import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # For the progress bar widget
import threading

from mxdnkey.audio.audio_file import AudioFile
from mxdnkey.analysis.analyzer import AudioAnalyzer

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mxdnkey")
        self.geometry("500x350")
        
        # Create an instance of the AudioAnalyzer
        self.audio_analyzer = AudioAnalyzer()
        self.create_widgets()

    def create_widgets(self):
        # Button to upload a file
        self.upload_btn = tk.Button(self, text="Upload Music", command=self.select_file)
        self.upload_btn.pack(pady=10)
        
        # Frame for file metadata information
        self.metadata_frame = tk.LabelFrame(self, text="File Metadata", padx=5, pady=5)
        self.metadata_frame.pack(fill="x", padx=10, pady=5)
        
        # Create labels for each metadata field with initial placeholder text
        self.title_label = tk.Label(self.metadata_frame, text="Title: -")
        self.title_label.pack(anchor="w")
        
        self.artist_label = tk.Label(self.metadata_frame, text="Artist: -")
        self.artist_label.pack(anchor="w")
        
        self.album_label = tk.Label(self.metadata_frame, text="Album: -")
        self.album_label.pack(anchor="w")
        
        self.duration_label = tk.Label(self.metadata_frame, text="Duration: -")
        self.duration_label.pack(anchor="w")
        
        # Label to display analysis results (BPM & Key)
        self.result_label = tk.Label(self, text="Analysis results will appear here")
        self.result_label.pack(pady=10)
        
        # Progress bar widget from ttk
        self.progressbar = ttk.Progressbar(self, orient="horizontal",
                                           mode="determinate", length=300)
        self.progressbar.pack(pady=10)
        self.progressbar["maximum"] = 100  # Maximum progress value
        self.progressbar["value"] = 0      # Initial progress value

    def select_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac")])
        if filepath:
            # Reset UI elements and disable the upload button during processing
            self.result_label.config(text="Analyzing...")
            self.progressbar["value"] = 0
            self.upload_btn.config(state="disabled")
            
            # Run the analysis and metadata extraction in a new thread to keep the UI responsive
            threading.Thread(target=self.analyze_file, args=(filepath,), daemon=True).start()

    def analyze_file(self, filepath):
        try:
            # Step 1: Create the AudioFile object (which loads metadata)
            audio_file = AudioFile(filepath)
            # Update metadata information on the GUI (run on main thread)
            self.after(0, lambda: self.update_metadata(audio_file.metadata))
            
            # Step 2: Load the audio data (this may take a few seconds)
            audio_file.load_audio()  # Uses default sample rate from config
            self.update_progress(20)  # Update progress to 20%
            
            # Step 3: Perform BPM analysis
            bpm = self.audio_analyzer.bpm_detector.detect_bpm(audio_file.audio_data,
                                                              audio_file.sample_rate)
            self.update_progress(60)  # Update progress to 60% after BPM analysis

            # Step 4: Perform key analysis
            key = self.audio_analyzer.key_detector.detect_key(audio_file.audio_data,
                                                              audio_file.sample_rate)
            self.update_progress(100)  # Analysis complete

            # Prepare and display the analysis results (BPM & Key)
            results = {"BPM": bpm, "Key": key}
            result_text = "\n".join(f"{k}: {v}" for k, v in results.items())
            self.after(0, lambda: self.display_results(result_text))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
            self.after(0, lambda: self.upload_btn.config(state="normal"))

    def update_progress(self, value):
        """Safely update the progress bar from the worker thread."""
        self.after(0, lambda: self.progressbar.configure(value=value))

    def update_metadata(self, metadata):
        """
        Extract and display common metadata: Title, Artist, Album, Duration.
        This example assumes an ID3-like metadata structure.
        """
        # Initialize default strings
        title = "Unknown"
        artist = "Unknown"
        album = "Unknown"
        duration = "Unknown"
        
        if metadata:
            try:
            # Check for Title: first ID3 (MP3) then common lowercase keys
                if "TIT2" in metadata:
                    title = metadata["TIT2"].text[0]
                elif "title" in metadata:
                    title_value = metadata.get("title")
                    # Metadata values could be lists or plain strings
                    title = title_value[0] if isinstance(title_value, list) else title_value

                # Check for Artist: first ID3 then common key lookup
                if "TPE1" in metadata:
                    artist = metadata["TPE1"].text[0]
                elif "artist" in metadata:
                    artist_value = metadata.get("artist")
                    artist = artist_value[0] if isinstance(artist_value, list) else artist_value

                # Check for Album: first ID3 then common key lookup
                if "TALB" in metadata:
                    album = metadata["TALB"].text[0]
                elif "album" in metadata:
                    album_value = metadata.get("album")
                    album = album_value[0] if isinstance(album_value, list) else album_value
                
            except Exception:
                pass  # Add additional handling if needed
                
            # Duration can be extracted from the info attribute if available.
            if hasattr(metadata, "info") and hasattr(metadata.info, "length"):
                duration_sec = metadata.info.length
                minutes = int(duration_sec // 60)
                seconds = int(duration_sec % 60)
                duration = f"{minutes}m {seconds}s"
        
        # Update metadata labels (all done on the main thread)
        self.title_label.config(text=f"Title: {title}")
        self.artist_label.config(text=f"Artist: {artist}")
        self.album_label.config(text=f"Album: {album}")
        self.duration_label.config(text=f"Duration: {duration}")

    def display_results(self, text):
        """Display the analysis results (BPM and Key) and re-enable file upload."""
        self.result_label.config(text=text)
        self.upload_btn.config(state="normal")

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
