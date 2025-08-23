"""
Playlist view and management UI component
"""
import tkinter as tk
from tkinter import ttk
import os
from typing import Callable, Optional
from models.playlist import Playlist
from utils.time_utils import seconds_to_time_string

class PlaylistViewFrame(ttk.LabelFrame):
    """UI frame for viewing and managing the playlist"""
    
    def __init__(self, parent,
                 on_move_up: Callable[[int], None],
                 on_move_down: Callable[[int], None], 
                 on_remove: Callable[[int], None],
                 on_play: Callable[[], None],
                 on_stop: Callable[[], None],
                 on_save: Callable[[], None],
                 on_load: Callable[[], None],
                 on_reorder: Callable[[int, int], None],
                 on_volume_changed: Callable[[int, float], None] = None,
                 on_volumes_normalized: Callable[[], None] = None):
        super().__init__(parent, text="Playlist", padding="5")
        
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down
        self.on_remove = on_remove
        self.on_play = on_play
        self.on_stop = on_stop
        self.on_save = on_save
        self.on_load = on_load
        self.on_reorder = on_reorder
        self.on_volume_changed = on_volume_changed or (lambda i, v: None)
        self.on_volumes_normalized = on_volumes_normalized or (lambda: None)
        
        # Reference to current playlist (set by refresh_display)
        self.current_playlist = None
        
        # Drag and drop state
        self.drag_start_index: Optional[int] = None
        
        self.setup_ui()
        self.bind_events()
    
    def setup_ui(self):
        """Setup the playlist view UI"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Playlist treeview
        columns = ("Order", "File", "Start", "End", "Volume", "Page", "Comment")
        self.playlist_tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.playlist_tree.heading(col, text=col)
            
        self.playlist_tree.column("Order", width=50)
        self.playlist_tree.column("File", width=200)
        self.playlist_tree.column("Start", width=60)
        self.playlist_tree.column("End", width=60)
        self.playlist_tree.column("Volume", width=60)
        self.playlist_tree.column("Page", width=50)
        self.playlist_tree.column("Comment", width=150)
        
        # Scrollbar for treeview
        playlist_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=playlist_scroll.set)
        
        self.playlist_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        playlist_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Playlist controls
        playlist_control_frame = ttk.Frame(self)
        playlist_control_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(playlist_control_frame, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(playlist_control_frame, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(playlist_control_frame, text="Remove", command=self.remove_song).pack(side=tk.LEFT, padx=(0, 20))
        
        # Volume controls
        ttk.Button(playlist_control_frame, text="Edit Volumes", command=self.edit_volumes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(playlist_control_frame, text="Normalize", command=self.normalize_volumes).pack(side=tk.LEFT, padx=(0, 20))
        
        # Playback controls
        ttk.Button(playlist_control_frame, text="Play Playlist", command=self.play_playlist).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(playlist_control_frame, text="Stop Playlist", command=self.stop_playlist).pack(side=tk.LEFT, padx=(0, 20))
        
        # File operations
        ttk.Button(playlist_control_frame, text="Load Playlist", command=self.load_playlist).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(playlist_control_frame, text="Save Playlist", command=self.save_playlist).pack(side=tk.LEFT)
    
    def bind_events(self):
        """Bind events for drag and drop and selection"""
        self.playlist_tree.bind("<Button-1>", self.on_click)
        self.playlist_tree.bind("<B1-Motion>", self.on_drag)
        self.playlist_tree.bind("<ButtonRelease-1>", self.on_drop)
    
    def refresh_display(self, playlist: Playlist):
        """Refresh the playlist display"""
        self.current_playlist = playlist  # Store reference for volume editing
        
        # Clear existing items
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)
            
        # Add all playlist items
        for i, song in enumerate(playlist):
            start_text = seconds_to_time_string(song.start_time)
            end_text = seconds_to_time_string(song.end_time)
            volume_text = f"{int(song.volume * 100)}%"
            
            self.playlist_tree.insert("", "end", values=(
                i + 1,
                song.filename,
                start_text,
                end_text,
                volume_text,
                song.page,
                song.comment
            ))
    
    def get_selected_index(self) -> Optional[int]:
        """Get the index of the currently selected item"""
        selection = self.playlist_tree.selection()
        if selection:
            item = selection[0]
            return self.playlist_tree.index(item)
        return None
    
    def select_item(self, index: int):
        """Select an item by index"""
        children = self.playlist_tree.get_children()
        if 0 <= index < len(children):
            item = children[index]
            self.playlist_tree.selection_set(item)
    
    # Button handlers
    def move_up(self):
        """Move selected item up"""
        index = self.get_selected_index()
        if index is not None and index > 0:
            self.on_move_up(index)
    
    def move_down(self):
        """Move selected item down"""
        index = self.get_selected_index()
        if index is not None:
            self.on_move_down(index)
    
    def remove_song(self):
        """Remove selected item"""
        index = self.get_selected_index()
        if index is not None:
            self.on_remove(index)
    
    def play_playlist(self):
        """Start playlist playback"""
        self.on_play()
    
    def stop_playlist(self):
        """Stop playlist playback"""
        self.on_stop()
    
    def save_playlist(self):
        """Save playlist to file"""
        self.on_save()
    
    def load_playlist(self):
        """Load playlist from file"""
        self.on_load()
    
    def edit_volumes(self):
        """Open volume editor dialog"""
        if self.current_playlist and len(self.current_playlist) > 0:
            from ui.volume_editor import VolumeEditorDialog
            dialog = VolumeEditorDialog(self, self.current_playlist, self.on_volume_changed)
        else:
            from tkinter import messagebox
            messagebox.showwarning("No Songs", "Please add songs to the playlist first.")
    
    def normalize_volumes(self):
        """Open volume normalizer dialog"""
        if self.current_playlist and len(self.current_playlist) > 0:
            from ui.volume_editor import VolumeNormalizerDialog
            dialog = VolumeNormalizerDialog(self, self.current_playlist, self.on_volumes_normalized)
        else:
            from tkinter import messagebox
            messagebox.showwarning("No Songs", "Please add songs to the playlist first.")
    
    # Drag and drop handlers
    def on_click(self, event):
        """Handle mouse click for drag start"""
        self.drag_start_index = None
        item = self.playlist_tree.identify_row(event.y)
        if item:
            self.drag_start_index = self.playlist_tree.index(item)
    
    def on_drag(self, event):
        """Handle mouse drag"""
        if hasattr(self, 'drag_start_index') and self.drag_start_index is not None:
            # Visual feedback could be added here
            pass
    
    def on_drop(self, event):
        """Handle mouse drop for reordering"""
        if not hasattr(self, 'drag_start_index') or self.drag_start_index is None:
            return
            
        drop_item = self.playlist_tree.identify_row(event.y)
        if drop_item:
            drop_index = self.playlist_tree.index(drop_item)
            
            if drop_index != self.drag_start_index:
                self.on_reorder(self.drag_start_index, drop_index)
