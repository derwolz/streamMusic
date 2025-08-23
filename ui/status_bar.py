"""
Status bar UI component
"""
import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Label):
    """Status bar for displaying application status"""
    
    def __init__(self, parent):
        super().__init__(parent, relief=tk.SUNKEN)
        
        self.status_text = tk.StringVar()
        self.config(textvariable=self.status_text)
    
    def set_status(self, message: str):
        """Set the status message"""
        self.status_text.set(message)
    
    def get_status(self) -> str:
        """Get the current status message"""
        return self.status_text.get()
    
    def clear_status(self):
        """Clear the status message"""
        self.status_text.set("")
