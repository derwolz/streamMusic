"""
Song details input UI component
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

class SongDetailsFrame(ttk.LabelFrame):
    """UI frame for entering song details (page, comment, volume)"""
    
    def __init__(self, parent, on_add_to_playlist: Callable[[int, str, float, float, float], None]):
        super().__init__(parent, text="Song Details", padding="5")
        
        self.on_add_to_playlist = on_add_to_playlist
        
        # Variables
        self.page_number = tk.IntVar()
        self.comment = tk.StringVar()
        self.volume = tk.DoubleVar(value=1.0)  # Default volume at 100%
        
        # Reference to preview frame for getting times
        self.preview_frame = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the song details UI"""
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        
        # First row: Page and Comment
        ttk.Label(self, text="Page:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self, textvariable=self.page_number, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(self, text="Comment:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(self, textvariable=self.comment).grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(self, text="Add to Playlist", command=self.add_to_playlist).grid(row=0, column=4, padx=(10, 0))
        
        # Second row: Volume control
        volume_frame = ttk.Frame(self)
        volume_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(5, 0))
        volume_frame.columnconfigure(1, weight=1)
        
        ttk.Label(volume_frame, text="Volume:").grid(row=0, column=0, sticky=tk.W)
        self.volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.volume, 
                                     orient=tk.HORIZONTAL, length=200)
        self.volume_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10))
        
        self.volume_label = ttk.Label(volume_frame, text="100%")
        self.volume_label.grid(row=0, column=2, sticky=tk.W)
        
        # Bind volume scale to update label
        self.volume.trace_add("write", self.update_volume_label)
    
    def update_volume_label(self, *args):
        """Update the volume percentage label"""
        volume_percent = int(self.volume.get() * 100)
        self.volume_label.config(text=f"{volume_percent}%")
    
    def set_preview_frame(self, preview_frame):
        """Set reference to preview frame to get current times"""
        self.preview_frame = preview_frame
    
    def add_to_playlist(self):
        """Add current song to playlist"""
        # Get times from preview frame if available
        if self.preview_frame:
            start_time, end_time = self.preview_frame.get_times()
        else:
            start_time, end_time = 0, 0
        
        # Call parent callback with volume
        self.on_add_to_playlist(
            self.page_number.get(),
            self.comment.get(),
            start_time,
            end_time,
            self.volume.get()
        )
        
        # Clear inputs after adding (but keep volume at current setting)
        self.clear_inputs()
    
    def clear_inputs(self):
        """Clear the input fields (but keep volume setting)"""
        self.comment.set("")
        self.page_number.set(0)
        # Don't reset volume - user may want to use same volume for multiple songs
    
    def get_page(self) -> int:
        """Get the current page number"""
        return self.page_number.get()
    
    def get_comment(self) -> str:
        """Get the current comment"""
        return self.comment.get()
    
    def set_page(self, page: int):
        """Set the page number"""
        self.page_number.set(page)
    
    def get_volume(self) -> float:
        """Get the current volume setting"""
        return self.volume.get()
    
    def set_volume(self, volume: float):
        """Set the volume"""
        self.volume.set(max(0.0, min(1.0, volume)))
