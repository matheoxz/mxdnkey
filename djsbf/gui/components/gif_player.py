import tkinter as tk
from djsbf.utils.logger import get_logger

logger = get_logger(__name__)

class GIFPlayer(tk.Label):
    def __init__(self, parent, filepath, delay=100):
        super().__init__(parent)
        self.filepath = filepath
        self.delay = delay
        self.frames = []
        self.current_frame = 0
        self.animated = False
        self.load_gif()
        
    def load_gif(self):
        try:
            self.gif = tk.PhotoImage(file=self.filepath, format='gif -index 0')
            self.frames.append(self.gif)
            
            # Load all frames from GIF
            index = 1
            while True:
                try:
                    frame = tk.PhotoImage(
                        file=self.filepath,
                        format=f'gif -index {index}'
                    )
                    self.frames.append(frame)
                    index += 1
                except tk.TclError:
                    break
            
            self.animated = len(self.frames) > 1
            self.config(image=self.frames[0])
            
        except Exception as e:
            logger.error(f"Error loading GIF: {e}")
            self.config(text="GIF Loading Error")

    def start_animation(self):
        if self.animated and not self.stopped:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.config(image=self.frames[self.current_frame])
            self.after(self.delay, self.start_animation)

    def play(self):
        self.stopped = False
        if len(self.frames) > 0:
            self.start_animation()

    def stop(self):
        self.stopped = True