import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os

from mxdnkey.analysis.analyzer import AudioAnalyzer
from mxdnkey.gui.player_window import PlayerWindow

from logging import getLogger

logger = getLogger(__name__)
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mxdnkey")
        self.geometry("900x600")  # Increased window size for the table
        self.audio_analyzer = AudioAnalyzer()
        self.create_widgets()

    def create_widgets(self):
        # Button to open a music folder
        self.open_folder_btn = tk.Button(self, text="Open Music Folder", command=self.select_folder)
        self.open_folder_btn.pack(pady=10)

        # Frame for the table
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Table header (now include a "Play" column)
        headers = ["Index", "Genre", "Artist", "Album", "Title", "Progress", "BPM", "Key", "Camelot", "Play"]
        for col, header in enumerate(headers):
            lbl = tk.Label(self.table_frame, text=header, font=("Arial", 10, "bold"),
                           borderwidth=1, relief="solid")
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

        # Dictionary to store row widgets (for updates)
        self.row_widgets = {}

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            # Clear previous rows (if any)
            for widget in self.table_frame.winfo_children():
                grid_info = widget.grid_info()
                if "row" in grid_info and int(grid_info["row"]) > 0:
                    widget.destroy()
            self.row_widgets = {}

            # List allowed audio files from the folder
            allowed_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.wma'}
            files = [os.path.join(folder_path, f).replace('\\', '/') for f in os.listdir(folder_path)
                     if os.path.splitext(f)[1].lower() in allowed_extensions]

            logger.debug("Found %d files in the folder: %s", len(files), folder_path)

            print("Found files: ", files)

            # For each file, add a row to the table and start its analysis in a thread.
            for idx, file_path in enumerate(files, start=1):
                self.add_table_row(idx, file_path)
                threading.Thread(target=self.analyze_file_gui,
                                 args=(file_path, idx),
                                 daemon=True).start()

    def add_table_row(self, idx, file_path):
        # Attempt to extract basic metadata.
        try:
            from mxdnkey.audio.audio_file import AudioFile
            audio_file = AudioFile(file_path)
            metadata = audio_file.metadata
        except Exception as e:
            metadata = None
        genre, artist, album, title = self.extract_metadata(metadata)

        # Create the cells for each column.
        idx_lbl = tk.Label(self.table_frame, text=str(idx), borderwidth=1, relief="solid")
        idx_lbl.grid(row=idx, column=0, sticky="nsew", padx=1, pady=1)

        genre_lbl = tk.Label(self.table_frame, text=genre, borderwidth=1, relief="solid")
        genre_lbl.grid(row=idx, column=1, sticky="nsew", padx=1, pady=1)

        artist_lbl = tk.Label(self.table_frame, text=artist, borderwidth=1, relief="solid")
        artist_lbl.grid(row=idx, column=2, sticky="nsew", padx=1, pady=1)

        album_lbl = tk.Label(self.table_frame, text=album, borderwidth=1, relief="solid")
        album_lbl.grid(row=idx, column=3, sticky="nsew", padx=1, pady=1)

        title_lbl = tk.Label(self.table_frame, text=title, borderwidth=1, relief="solid")
        title_lbl.grid(row=idx, column=4, sticky="nsew", padx=1, pady=1)

        progress_bar = ttk.Progressbar(self.table_frame, orient="horizontal", mode="determinate", maximum=100)
        progress_bar.grid(row=idx, column=5, sticky="nsew", padx=1, pady=1)

        bpm_lbl = tk.Label(self.table_frame, text="Pending", borderwidth=1, relief="solid")
        bpm_lbl.grid(row=idx, column=6, sticky="nsew", padx=1, pady=1)

        key_lbl = tk.Label(self.table_frame, text="Pending", borderwidth=1, relief="solid")
        key_lbl.grid(row=idx, column=7, sticky="nsew", padx=1, pady=1)

        camelot_lbl = tk.Label(self.table_frame, text="Pending", borderwidth=1, relief="solid")
        camelot_lbl.grid(row=idx, column=8, sticky="nsew", padx=1, pady=1)

        # Add a Play button that opens the PlayerWindow
        play_btn = tk.Button(self.table_frame, text="Play", command=lambda fp=file_path: self.open_player(fp))
        play_btn.grid(row=idx, column=9, sticky="nsew", padx=1, pady=1)

        # Store row widgets to update progress and analysis results.
        self.row_widgets[idx] = {
            "progress_bar": progress_bar,
            "bpm_label": bpm_lbl,
            "key_label": key_lbl,
            "camelot_label": camelot_lbl
        }

    def extract_metadata(self, metadata):
        """
        Extracts common metadata fields (genre, artist, album, title)
        handling both ID3 tags and generic lowercase keys.
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
                    value = metadata.get("genre")
                    genre = value[0] if isinstance(value, list) else value

                if "TIT2" in metadata:
                    title = metadata["TIT2"].text[0]
                elif "title" in metadata:
                    value = metadata.get("title")
                    title = value[0] if isinstance(value, list) else value

                if "TPE1" in metadata:
                    artist = metadata["TPE1"].text[0]
                elif "artist" in metadata:
                    value = metadata.get("artist")
                    artist = value[0] if isinstance(value, list) else value

                if "TALB" in metadata:
                    album = metadata["TALB"].text[0]
                elif "album" in metadata:
                    value = metadata.get("album")
                    album = value[0] if isinstance(value, list) else value
            except Exception as e:
                print("Error extracting metadata:", e)
        return genre, artist, album, title

    def analyze_file_gui(self, file_path, row_index):
        """Analyzes a single file, updating its row’s progress bar, BPM, Key, and Camelot columns."""
        try:
            from mxdnkey.audio.audio_file import AudioFile
            audio_file = AudioFile(file_path)
            audio_file.load_audio()
            self.update_row_progress(row_index, 20)

            bpm = self.audio_analyzer.bpm_detector.detect_bpm(
                audio_file.audio_data, audio_file.sample_rate
            )
            self.update_row_progress(row_index, 60)

            key_results = self.audio_analyzer.key_detector.detect_key(
                audio_file.audio_data, audio_file.sample_rate
            )
            self.update_row_progress(row_index, 100)

            self.after(0, lambda: self.row_widgets[row_index]["bpm_label"].config(text=bpm))
            self.after(0, lambda: self.row_widgets[row_index]["key_label"].config(text=str(key_results["key"])))
            self.after(0, lambda: self.row_widgets[row_index]["camelot_label"].config(text=str(key_results["camelot"])))
        except Exception as e:
            self.after(0, lambda: self.row_widgets[row_index]["bpm_label"].config(text="Error"))
            self.after(0, lambda: self.row_widgets[row_index]["key_label"].config(text="Error"))
            self.after(0, lambda: self.row_widgets[row_index]["camelot_label"].config(text="Error"))
            print(f"Error processing file {file_path}: {e}")

    def update_row_progress(self, row_index, value):
        """Safely updates the progress bar for a specific row."""
        if row_index in self.row_widgets:
            self.after(0, lambda: self.row_widgets[row_index]["progress_bar"].configure(value=value))

    def open_player(self, file_path):
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "The selected file does not exist or the file path is invalid.")
            return
        PlayerWindow(self, file_path)

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()