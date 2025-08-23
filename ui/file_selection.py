"""
File selection UI component
"""
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable

class FileSelectionFrame(ttk.LabelFrame):
    """UI frame for file selection and loading"""
    
    def __init__(self, parent, on_file_selected: Callable[[str], None], 
                 on_load_preview: Callable[[str], None]):
        super().__init__(parent, text="Song Selection", padding="5")
        
        self.on_file_selected = on_file_selected
        self.on_load_preview = on_load_preview
        
        # Variables
        self.selected_file = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the file selection UI"""
        self.columnconfigure(1, weight=1)
        
        ttk.Label(self, text="File:").grid(row=0, column=0, sticky=tk.W)
        
        self.file_entry = ttk.Entry(self, textvariable=self.selected_file, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        ttk.Button(self, text="Browse", command=self.browse_file).grid(row=0, column=2)
        ttk.Button(self, text="Load & Preview", command=self.load_preview).grid(row=0, column=3, padx=(5, 0))
    
    def browse_file(self):
        """Open file browser dialog"""
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg *.m4a"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.selected_file.set(filename)
            self.on_file_selected(filename)
    
    def load_preview(self):
        """Load the selected file for preview"""
        filename = self.selected_file.get()
        if filename:
            self.on_load_preview(filename)
    
    def get_selected_file(self) -> str:
        """Get the currently selected file"""
        return self.selected_file.get()
