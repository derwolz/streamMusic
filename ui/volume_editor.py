"""
Volume editor dialog for individual song volume adjustment
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from models.playlist import Playlist, Song

class VolumeEditorDialog:
    """Dialog for editing individual song volumes"""
    
    def __init__(self, parent, playlist: Playlist, on_volume_changed: Callable[[int, float], None]):
        self.parent = parent
        self.playlist = playlist
        self.on_volume_changed = on_volume_changed
        self.result = None
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the volume editor dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Volume Editor")
        self.dialog.geometry("600x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, 
                 text="Adjust individual song volumes. Double-click a song to test playback.",
                 font=("TkDefaultFont", 9, "italic")).pack(pady=(0, 10))
        
        # Volume list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for volume controls
        columns = ("Song", "Volume", "Control")
        self.volume_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        self.volume_tree.heading("Song", text="Song")
        self.volume_tree.heading("Volume", text="Volume")
        self.volume_tree.heading("Control", text="Adjust")
        
        self.volume_tree.column("Song", width=300)
        self.volume_tree.column("Volume", width=80)
        self.volume_tree.column("Control", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.volume_tree.yview)
        self.volume_tree.configure(yscrollcommand=scrollbar.set)
        
        self.volume_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Volume controls frame (will be populated when item is selected)
        self.controls_frame = ttk.LabelFrame(main_frame, text="Volume Control", padding="10")
        self.controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_song_label = ttk.Label(self.controls_frame, text="Select a song to adjust volume")
        self.current_song_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Volume scale (initially disabled)
        ttk.Label(self.controls_frame, text="Volume:").grid(row=1, column=0, sticky=tk.W)
        
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_scale = ttk.Scale(self.controls_frame, from_=0.0, to=1.0, 
                                     variable=self.volume_var, orient=tk.HORIZONTAL, 
                                     length=300, state="disabled")
        self.volume_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        self.volume_label = ttk.Label(self.controls_frame, text="100%")
        self.volume_label.grid(row=1, column=2, sticky=tk.W)
        
        self.controls_frame.columnconfigure(1, weight=1)
        
        # Quick preset buttons
        preset_frame = ttk.Frame(self.controls_frame)
        preset_frame.grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Label(preset_frame, text="Quick presets:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(preset_frame, text="25%", command=lambda: self.set_volume(0.25), width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="50%", command=lambda: self.set_volume(0.50), width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="75%", command=lambda: self.set_volume(0.75), width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="100%", command=lambda: self.set_volume(1.00), width=6).pack(side=tk.LEFT, padx=2)
        
        # Normalize all button
        ttk.Button(preset_frame, text="Normalize All", command=self.normalize_all_volumes, 
                  width=12).pack(side=tk.LEFT, padx=(20, 2))
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Close", command=self.close_dialog).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset All", command=self.reset_all_volumes).pack(side=tk.RIGHT)
        
        # Populate the list
        self.populate_volume_list()
        
        # Bind events
        self.volume_tree.bind("<<TreeviewSelect>>", self.on_song_select)
        self.volume_var.trace_add("write", self.on_volume_change)
        
        # Current selection
        self.current_song_index = -1
    
    def populate_volume_list(self):
        """Populate the volume list with songs"""
        for item in self.volume_tree.get_children():
            self.volume_tree.delete(item)
        
        for i, song in enumerate(self.playlist):
            volume_text = f"{int(song.volume * 100)}%"
            self.volume_tree.insert("", "end", values=(
                song.filename,
                volume_text,
                "← Select to adjust"
            ))
    
    def on_song_select(self, event):
        """Handle song selection"""
        selection = self.volume_tree.selection()
        if selection:
            item = selection[0]
            self.current_song_index = self.volume_tree.index(item)
            song = self.playlist[self.current_song_index]
            
            # Update controls
            self.current_song_label.config(text=f"Adjusting: {song.filename}")
            self.volume_var.set(song.volume)
            self.volume_scale.config(state="normal")
            self.update_volume_label()
    
    def on_volume_change(self, *args):
        """Handle volume change from scale"""
        if self.current_song_index >= 0:
            new_volume = self.volume_var.get()
            
            # Update the song in the playlist
            song = self.playlist[self.current_song_index]
            song.volume = new_volume
            
            # Update the display
            self.update_volume_display(self.current_song_index, new_volume)
            self.update_volume_label()
            
            # Notify parent of change
            self.on_volume_changed(self.current_song_index, new_volume)
    
    def update_volume_display(self, song_index: int, volume: float):
        """Update the volume display for a specific song"""
        children = self.volume_tree.get_children()
        if 0 <= song_index < len(children):
            item = children[song_index]
            song = self.playlist[song_index]
            volume_text = f"{int(volume * 100)}%"
            
            self.volume_tree.item(item, values=(
                song.filename,
                volume_text,
                "← Select to adjust"
            ))
    
    def update_volume_label(self):
        """Update the volume percentage label"""
        volume_percent = int(self.volume_var.get() * 100)
        self.volume_label.config(text=f"{volume_percent}%")
    
    def set_volume(self, volume: float):
        """Set volume to specific value"""
        if self.current_song_index >= 0:
            self.volume_var.set(volume)
    
    def normalize_all_volumes(self):
        """Set all volumes to 100%"""
        for i, song in enumerate(self.playlist):
            song.volume = 1.0
            self.update_volume_display(i, 1.0)
            self.on_volume_changed(i, 1.0)
        
        # Update current selection if any
        if self.current_song_index >= 0:
            self.volume_var.set(1.0)
    
    def reset_all_volumes(self):
        """Reset all volumes to default (100%)"""
        self.normalize_all_volumes()
    
    def close_dialog(self):
        """Close the dialog"""
        self.dialog.destroy()

class VolumeNormalizerDialog:
    """Dialog for smart volume normalization based on audio analysis"""
    
    def __init__(self, parent, playlist: Playlist, on_volumes_normalized: Callable[[], None]):
        self.parent = parent
        self.playlist = playlist
        self.on_volumes_normalized = on_volumes_normalized
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the volume normalizer dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Volume Normalizer")
        self.dialog.geometry("500x300")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 100,
            self.parent.winfo_rooty() + 100
        ))
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Volume Normalizer", 
                               font=("TkDefaultFont", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = ("This tool helps normalize volumes across your playlist. "
                    "Choose a normalization method below:")
        ttk.Label(main_frame, text=desc_text, wraplength=450).pack(pady=(0, 20))
        
        # Normalization options
        self.norm_method = tk.StringVar(value="uniform")
        
        options_frame = ttk.LabelFrame(main_frame, text="Normalization Method", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(options_frame, text="Set all to 100% (Uniform)", 
                       variable=self.norm_method, value="uniform").pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(options_frame, text="Set all to 75% (Conservative)", 
                       variable=self.norm_method, value="conservative").pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(options_frame, text="Set all to 50% (Quiet)", 
                       variable=self.norm_method, value="quiet").pack(anchor=tk.W, pady=2)
        
        # Custom level option
        custom_frame = ttk.Frame(options_frame)
        custom_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Radiobutton(custom_frame, text="Custom level:", 
                       variable=self.norm_method, value="custom").pack(side=tk.LEFT)
        
        self.custom_volume = tk.DoubleVar(value=0.8)
        custom_scale = ttk.Scale(custom_frame, from_=0.1, to=1.0, 
                               variable=self.custom_volume, orient=tk.HORIZONTAL, length=150)
        custom_scale.pack(side=tk.LEFT, padx=(10, 5))
        
        self.custom_label = ttk.Label(custom_frame, text="80%")
        self.custom_label.pack(side=tk.LEFT)
        
        self.custom_volume.trace_add("write", self.update_custom_label)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.close_dialog).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Apply", command=self.apply_normalization).pack(side=tk.RIGHT)
    
    def update_custom_label(self, *args):
        """Update the custom volume label"""
        volume_percent = int(self.custom_volume.get() * 100)
        self.custom_label.config(text=f"{volume_percent}%")
    
    def apply_normalization(self):
        """Apply the selected normalization"""
        method = self.norm_method.get()
        
        if method == "uniform":
            target_volume = 1.0
        elif method == "conservative":
            target_volume = 0.75
        elif method == "quiet":
            target_volume = 0.5
        elif method == "custom":
            target_volume = self.custom_volume.get()
        else:
            target_volume = 1.0
        
        # Apply to all songs
        for song in self.playlist:
            song.volume = target_volume
        
        # Notify parent
        self.on_volumes_normalized()
        
        self.close_dialog()
    
    def close_dialog(self):
        """Close the dialog"""
        self.dialog.destroy()
