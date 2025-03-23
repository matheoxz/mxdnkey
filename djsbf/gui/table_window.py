import tkinter as tk
import os
import tkinter.messagebox as messagebox
from tkinter import filedialog, ttk
import threading
from djsbf.utils.folder_utils import FolderHandler
from djsbf.dataclass.audio_file import AudioFile
from djsbf.enums.key_enums import Tonic, Mode, CamelotKey, get_camelot_from_tonic_and_mode
from djsbf.utils.logger import get_logger

from djsbf import config

logger = get_logger(__name__)


class TableWindow(tk.Toplevel):
    def __init__(self, parent, folder_path):
        super().__init__(parent)
        self.folder_path = folder_path
        self.title("DJ BF - Library")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.row_widgets = {}
        
        self.create_widgets()
        self.process_files()

    def create_widgets(self):
        """Creates buttons and table"""
        # Button frame at top left
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side='top', anchor='nw', pady=10)
        
        self.open_folder_btn = tk.Button(
            self.button_frame, 
            text="Open Music Folder", 
            command=self.select_folder
        )
        self.rename_files_btn = tk.Button(
            self.button_frame, 
            text="Rename Files",
            state="disabled",
        )

        self.open_folder_btn.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        self.rename_files_btn.grid(row=0, column=1, sticky='nsew', padx=0, pady=0)

        
        self.button_frame.grid_columnconfigure(0, weight=1, uniform='buttons')
        self.button_frame.grid_columnconfigure(1, weight=1, uniform='buttons')
        self.button_frame.grid_rowconfigure(0, weight=1)

        # Create table
        self.create_table()

    def select_folder(self):
        """Handle folder selection in table window"""
        folder_path = filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            self.folder_path = folder_path
            self._clear_table()
            self.process_files()

    def rename_files(self, audio_file: AudioFile, camelot: bool = True):
        """Renames files in the selected folder based on metadata"""
        if camelot:
            key = audio_file.key.camelot.value
        else:
            key = audio_file.key.tonic.value + ("M" if audio_file.key.mode == Mode.MAJOR else "m")
        
        if audio_file.artist and audio_file.title:
            new_file_name = f"[{key}][{audio_file.BPM:.2f}] {audio_file.artist} - {audio_file.title}.{self.get_extension(audio_file.file_path)}"
        else:
            new_file_name = f"[{key}][{audio_file.BPM:.2f}] {audio_file.file_path.split('/')[-1]}"
        
        new_file_path = f"{audio_file.file_path.rsplit('/', 1)[0]}/{new_file_name}"

        try:
            self.update_row_progress(audio_file, 50, "blue")
            os.rename(audio_file.file_path, new_file_path)
            logger.info("Renamed file: %s -> %s", audio_file.file_path, new_file_path)
            audio_file.file_path = new_file_path
            self.update_row_progress(audio_file, 100, "blue")
        except Exception as e:
            logger.error("Error renaming file: %s -> %s", audio_file.file_path, new_file_path)
            logger.error(e)

    def get_extension(self, file_path):
        """Get file extension from file path"""
        return file_path.split(".")[-1]

    def process_files(self):
        """Process audio files in the selected folder"""
        files = FolderHandler.get_audio_files(self.folder_path)
        logger.debug("Found %d audio files in folder: %s", len(files), self.folder_path)
        
        max_threads = min(config.MAX_ANALYSIS_THREADS, len(files))
        semaphore = threading.Semaphore(max_threads)
        audio_files = []

        def thread_target(file_path, idx):
            with semaphore:
                audio_files.append(self.analyze_file_gui(file_path, idx))
                if len(audio_files) == len(files):
                    self.after(0, lambda: self.rename_files_btn.config(state="normal", command=lambda: [self.rename_files(af) for af in audio_files]))
        
        for idx, file_path in enumerate(files, start=1):
            self.add_table_row(idx, file_path)
            threading.Thread(target=thread_target, args=(file_path, idx), daemon=True).start()


    def create_table(self):
        """Creates the table for displaying audio file metadata."""
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.table_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        headers = ["Index", "Genre", "Artist", "Album", "Title", "Progress", "BPM", "Key", "Camelot", "Player"]
        for col, header in enumerate(headers):
            lbl = tk.Label(self.table_frame, text=header, font=("Arial", 10, "bold"),
                           borderwidth=1, relief="solid")
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)
        self.row_widgets = {}

        self.table_frame.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _clear_table(self):
        for widget in self.table_frame.winfo_children():
            info = widget.grid_info()
            if "row" in info and int(info["row"]) > 0:
                widget.destroy()
        self.row_widgets = {}

    def add_table_row(self, idx, file_path):
        try:
            from djsbf.dataclass.audio_file import AudioFile
            audio_file = AudioFile(file_path)
        except Exception as e:
            logger.error("Error creating AudioFile for '%s': %s", file_path, e)
            return
        
        idx_lbl = tk.Label(self.table_frame, text=str(idx), borderwidth=1, relief="solid")
        idx_lbl.grid(row=idx, column=0, sticky="nsew", padx=1, pady=1)
        genre_lbl = tk.Label(self.table_frame, 
            text=audio_file.metadata.get("TCON", ["Unknown"])[0] 
            if audio_file.metadata and "TCON" in audio_file.metadata
            else audio_file.metadata.get("genre", ["Unknown"])[0] 
            if audio_file.metadata and "genre" in audio_file.metadata
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
        play_btn = tk.Button(self.table_frame, text="▶", state="disabled")
        play_btn.grid(row=idx, column=9, sticky="nsew", padx=1, pady=1)
        self.row_widgets[idx] = {
            "progress_bar": progress_bar,
            "bpm_label": bpm_lbl,
            "key_label": key_lbl,
            "camelot_label": camelot_lbl,
            "player": play_btn
        }

    def analyze_file_gui(self, file_path, row_index):
        try:
            from djsbf.dataclass.audio_file import AudioFile
            audio_file = AudioFile(file_path)
            def progress_callback(percentage):
                self.update_row_progress(row_index, percentage)
            audio_file.analyze(progress_callback)
            bpm = audio_file.BPM
            key_info = audio_file.key
            self.after(0, lambda: self.row_widgets[row_index]["bpm_label"].config(text=f"{bpm:.2f}"))
            self.after(0, lambda: self.row_widgets[row_index]["key_label"].config(text=f"{key_info.tonic.value} {key_info.mode.value}"))
            self.after(0, lambda: self.row_widgets[row_index]["camelot_label"].config(text=key_info.camelot.value))
            self.after(0, lambda: self.row_widgets[row_index]["player"].config(state="normal", command=lambda af=audio_file: self.open_player(af)))
            return audio_file
        except Exception as e:
            logger.error("Error analyzing file %s: %s", file_path, e)
            self.after(0, lambda: self.row_widgets[row_index]["bpm_label"].config(text="Error"))
            self.after(0, lambda: self.row_widgets[row_index]["key_label"].config(text="Error"))
            self.after(0, lambda: self.row_widgets[row_index]["camelot_label"].config(text="Error"))

    def update_row_progress(self, row_index, value, color="green"):
        if row_index in self.row_widgets:
            self.after(0, lambda: self.row_widgets[row_index]["progress_bar"].configure(value=value))
            if color:
                self.after(0, lambda: self.row_widgets[row_index]["progress_bar"].configure(style=f"{color}.Horizontal.TProgressbar"))
                style = ttk.Style()
                style.configure(f"{color}.Horizontal.TProgressbar", troughcolor='white', background=color)

    def open_player(self, audio_file):
        from djsbf.gui.player_window import PlayerWindow
        if audio_file is None:
            logger.error("Cannot open player for file %s: Analysis not done.", audio_file.file_path)
            messagebox.showwarning("Analysis Incomplete", "Please wait until the analysis is complete before playing the file.")
        else:
            PlayerWindow(self, audio_file)