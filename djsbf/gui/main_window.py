import tkinter as tk
from djsbf.gui.table_window import TableWindow
from djsbf.utils.logger import get_logger
from tkinter import filedialog
from djsbf.gui.components.gif_player import GIFPlayer
from djsbf.utils.folder_utils import FolderHandler as fs

from djsbf import config

logger = get_logger(__name__)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DJ organizer")
        self.geometry("250x350")
        self.create_initial_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_initial_widgets(self):
        """Creates initial layout with GIF and Open button"""
        # Create animated GIF player
        bf = fs.get_random_file(config.GIF_FOLDER, '.gif')
        logger.debug("Your BF is %s", bf)
        self.gif_player = GIFPlayer(self, bf, delay=50)
        self.gif_player.place(relx=0.5, rely=0.3, anchor='center')
        self.gif_player.play()

        # Open Music Folder button
        self.open_folder_btn = tk.Button(
            self,
            text="Open Music Folder",
            command=self.select_folder,
            relief='solid',
            borderwidth=1
        )
        self.open_folder_btn.place(
            relx=0.5,
            rely=0.7,
            anchor='center',
            relwidth=0.8,
            relheight=0.1
        )

    def select_folder(self):
        """Handles folder selection and opens table window"""
        folder_path = filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            self.gif_player.stop()
            self.withdraw()
            TableWindow(self, folder_path)

    def on_close(self):
        """Handle window close event"""
        self.gif_player.stop()
        self.destroy()

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()