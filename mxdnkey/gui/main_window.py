"""
MainWindow Module
===================

Provides a Tkinter window for selecting a folder and processing audio files.
For each audio file, an AudioFile object is instantiated;
its analysis (BPM and Key) is triggered (with progress callback updating its row's progress bar).
A table is displayed with metadata (genre, artist, album, title) and analysis (BPM, Key, Camelot),
and a Play button per row opens a PlayerWindow for playback.
Files are processed in parallel.
"""

import tkinter as tk
from tkinter import filedialog, ttk
import threading
import os
from mxdnkey.gui.player_window import PlayerWindow
from mxdnkey.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mxdnkey")
        self.geometry("900x600")
        self.create_widgets()

    def create_widgets(self):
        """Creates main GUI widgets: a folder selection button and a frame for the table."""
        self.open_folder_btn = tk.Button(self, text="Open Music Folder", command=self.select_folder)
        self.open_folder_btn.pack(pady=10)
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        headers = ["Index", "Genre", "Artist", "Album", "Title", "Progress", "BPM", "Key", "Camelot", "Play"]
        for col, header in enumerate(headers):
            lbl = tk.Label(self.table_frame, text=header, font=("Arial", 10, "bold"),
                           borderwidth=1, relief="solid")
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)
        self.row_widgets = {}

    def select_folder(self):
        """Opens a folder dialog, lists audio files, and begins parallel analysis."""
        folder_path = filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            self._clear_table()
            allowed_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.wma'}
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                     if os.path.splitext(f)[1].lower() in allowed_extensions]
            logger.debug("Found %d audio files in folder: %s", len(files), folder_path)
            for idx, file_path in enumerate(files, start=1):
                self.add_table_row(idx, file_path)
                threading.Thread(target=self.analyze_file_gui, args=(file_path, idx), daemon=True).start()

    def _clear_table(self):
        """Removes previous table rows (except for the header row)."""
        for widget in self.table_frame.winfo_children():
            info = widget.grid_info()
            if "row" in info and int(info["row"]) > 0:
                widget.destroy()
        self.row_widgets = {}

    def add_table_row(self, idx, file_path):
        """
        Creates a new row in the table.
        An AudioFile object is created to extract metadata.
        A Play button is provided to open a PlayerWindow.
        """
        try:
            from mxdnkey.audio.audio_file import AudioFile
            audio_file = AudioFile(file_path)
        except Exception as e:
            logger.error("Error creating AudioFile for '%s': %s", file_path, e)
            return
        idx_lbl = tk.Label(self.table_frame, text=str(idx), borderwidth=1, relief="solid")
        idx_lbl.grid(row=idx, column=0, sticky="nsew", padx=1, pady=1)
        genre_lbl = tk.Label(self.table_frame, text=audio_file.metadata.get("TCON", ["Unknown"])[0] 
                              if audio_file.metadata and "TCON" in audio_file.metadata
                              else audio_file.metadata.get("genre", ["Unknown"])[0] if audio_file.metadata and "genre" in audio_file.metadata
                              else "Unknown", borderwidth=1, relief="solid")
        genre_lbl.grid(row=idx, column=1, sticky="nsew", padx=1, pady=1)
        artist_lbl = tk.Label(self.table_frame, text=audio_file.artist, borderwidth=1, relief="solid")
        artist_lbl.grid(row=idx, column=2, sticky="nsew", padx=1, pady=1)
        album_lbl = tk.Label(self.table_frame, text=audio_file.album, borderwidth=1, relief="solid")
        album_lbl.grid(row=idx, column=3, sticky="nsew", padx=1, pady=1)
        title_lbl = tk.Label(self.table_frame, text=audio_file.title, borderwidth=1, relief="solid")
        title_lbl.grid(row=idx, column=4, sticky="nsew", padx=1, pady=1)
        progress_bar = ttk.Progressbar(self.table_frame, orient="horizontal", mode="determinate", maximum=100)
        progress_bar.grid(row=idx, column=5, sticky="nsew", padx=1, pady=1)
        bpm_lbl = tk.Label(self.table_frame, text="Pending", borderwidth=1, relief="solid")
        bpm_lbl.grid(row=idx, column=6, sticky="nsew", padx=1, pady=1)
        key_lbl = tk.Label(self.table_frame, text="Pending", borderwidth=1, relief="solid")
        key_lbl.grid(row=idx, column=7, sticky="nsew", padx=1, pady=1)
        camelot_lbl = tk.Label(self.table_frame, text="Pending", borderwidth=1, relief="solid")
        camelot_lbl.grid(row=idx, column=8, sticky="nsew", padx=1, pady=1)
        play_btn = tk.Button(self.table_frame, text="Play", command=lambda af=audio_file: self.open_player(af))
        play_btn.grid(row=idx, column=9, sticky="nsew", padx=1, pady=1)
        self.row_widgets[idx] = {
            "progress_bar": progress_bar,
            "bpm_label": bpm_lbl,
            "key_label": key_lbl,
            "camelot_label": camelot_lbl
        }

    def extract_metadata(self, metadata):
        """
        Extracts common fields (genre, artist, album, title) from a metadata object.
        Supports ID3 and lowercase key tagging.
        """
        genre = "Unknown"
        artist = "Unknown"
        album = "Unknown"
        title = "Unknown"
        if metadata:
            try:
                if "TCON" in metadata:
                    genre = metadata["TCON"].text[0]
                elif "genre" in metadata:
                    val = metadata.get("genre")
                    genre = val[0] if isinstance(val, list) else val
                if "TIT2" in metadata:
                    title = metadata["TIT2"].text[0]
                elif "title" in metadata:
                    val = metadata.get("title")
                    title = val[0] if isinstance(val, list) else val
                if "TPE1" in metadata:
                    artist = metadata["TPE1"].text[0]
                elif "artist" in metadata:
                    val = metadata.get("artist")
                    artist = val[0] if isinstance(val, list) else val
                if "TALB" in metadata:
                    album = metadata["TALB"].text[0]
                elif "album" in metadata:
                    val = metadata.get("album")
                    album = val[0] if isinstance(val, list) else val
            except Exception as e:
                logger.error("Error extracting metadata: %s", e)
        return genre, artist, album, title

    def analyze_file_gui(self, file_path, row_index):
        """
        For the given file, triggers its analysis (which updates BPM and Key).
        Uses a progress callback to update the progress bar for this row.
        """
        try:
            from mxdnkey.audio.audio_file import AudioFile
            audio_file = AudioFile(file_path)
            def progress_callback(percentage):
                self.update_row_progress(row_index, percentage)
            # Trigger analysis (BPM and Key)
            audio_file.analyze(progress_callback)
            bpm = audio_file.BPM
            key_info = audio_file.Key if audio_file.Key is not None else {"key": "Unknown", "camelot": "Unknown"}
            self.after(0, lambda: self.row_widgets[row_index]["bpm_label"].config(text=f"{bpm:.2f}"))
            self.after(0, lambda: self.row_widgets[row_index]["key_label"].config(text=str(key_info.get("key", "Unknown"))))
            self.after(0, lambda: self.row_widgets[row_index]["camelot_label"].config(text=str(key_info.get("camelot", "Unknown"))))
        except Exception as e:
            logger.error("Error analyzing file %s: %s", file_path, e)
            self.after(0, lambda: self.row_widgets[row_index]["bpm_label"].config(text="Error"))
            self.after(0, lambda: self.row_widgets[row_index]["key_label"].config(text="Error"))
            self.after(0, lambda: self.row_widgets[row_index]["camelot_label"].config(text="Error"))

    def update_row_progress(self, row_index, value):
        """Updates the progress bar for a specific row in a thread-safe manner."""
        if row_index in self.row_widgets:
            self.after(0, lambda: self.row_widgets[row_index]["progress_bar"].configure(value=value))

    def open_player(self, audio_file):
        """Opens a new PlayerWindow for the specified AudioFile instance."""
        from mxdnkey.gui.player_window import PlayerWindow
        PlayerWindow(self, audio_file)

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()