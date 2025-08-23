"""
Music Playlist Manager - Main Application Entry Point
"""
import tkinter as tk
import pygame
from ui.main_window import PlaylistManagerUI

def main():
    # Initialize pygame mixer
    pygame.mixer.init()
    
    # Create main window
    root = tk.Tk()
    app = PlaylistManagerUI(root)
    
    # Handle window closing
    def on_closing():
        app.cleanup()
        pygame.mixer.quit()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
