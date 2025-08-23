"""
Main UI window and application controller
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from typing import Optional

from models.playlist import Playlist, Song
from audio.manager import AudioManager
from network.listener import NetworkListener
from ui.file_selection import FileSelectionFrame
from ui.preview_controls import PreviewControlsFrame
from ui.song_details import SongDetailsFrame
from ui.playlist_view import PlaylistViewFrame
from ui.status_bar import StatusBar

class PlaylistManagerUI:
    """Main application UI controller"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Music Playlist Manager")
        self.root.geometry("1200x800")
        
        # Core components
        self.playlist = Playlist()
        self.audio_manager = AudioManager()
        self.network_listener = NetworkListener()
        
        # Current state
        self.current_file: Optional[str] = None
        self.song_length = 180  # Default song length
        
        # Setup callbacks
        self.audio_manager.set_position_callback(self.on_position_update)
        self.audio_manager.set_song_finished_callback(self.on_song_finished)
        
        # Setup network commands
        self.network_listener.register_command("AdvanceSong", self.advance_song)
        
        # Setup UI
        self.setup_ui()
        
        # Start network listener
        self.network_listener.start_listening()
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main container
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File Selection Section
        self.file_frame = FileSelectionFrame(main_frame, self.on_file_selected, self.on_load_preview)
        self.file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Preview Controls Section  
        self.preview_frame = PreviewControlsFrame(
            main_frame, 
            self.on_preview_play,
            self.on_preview_pause,
            self.on_preview_stop,
            self.on_set_start_time,
            self.on_set_end_time,
            self.on_time_change
        )
        self.preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Song Details Section
        self.details_frame = SongDetailsFrame(main_frame, self.on_add_to_playlist)
        self.details_frame.set_preview_frame(self.preview_frame)  # Connect to preview frame
        self.details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Playlist Section
        self.playlist_frame = PlaylistViewFrame(
            main_frame,
            self.on_playlist_move_up,
            self.on_playlist_move_down,
            self.on_playlist_remove,
            self.on_playlist_play,
            self.on_playlist_stop,
            self.on_playlist_save,
            self.on_playlist_load,
            self.on_playlist_reorder,
            self.on_volume_changed,
            self.on_volumes_normalized
        )
        self.playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Status Bar
        self.status_bar = StatusBar(main_frame)
        self.status_bar.pack(fill=tk.X)
        self.status_bar.set_status("Ready - Listening on port 5556")
    
    # File operations
    def on_file_selected(self, filename: str):
        """Handle file selection"""
        # This is called when user browses for a file
        pass
    
    def on_load_preview(self, filename: str):
        """Load file for preview"""
        if not filename:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            self.audio_manager.load_file(filename)
            self.current_file = filename
            
            # Update preview controls with song length
            self.preview_frame.set_song_length(self.song_length)
            
            self.status_bar.set_status(f"Loaded: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load audio file: {e}")
    
    # Preview controls
    def on_preview_play(self, start_time: float, end_time: float, resume: bool = False):
        """Play preview"""
        if not self.current_file:
            messagebox.showerror("Error", "Please load a file first")
            return
        
        try:
            self.audio_manager.play_preview(start_time, end_time, resume)
            self.status_bar.set_status("Playing preview...")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play file: {e}")
    
    def on_preview_pause(self):
        """Pause/resume preview"""
        self.audio_manager.pause_preview()
        status = "Preview paused" if not self.audio_manager.is_preview_playing else "Playing preview..."
        self.status_bar.set_status(status)
    
    def on_preview_stop(self):
        """Stop preview"""
        self.audio_manager.stop_preview()
        self.status_bar.set_status("Stopped")
    
    def on_set_start_time(self) -> float:
        """Set start time to current position"""
        return self.audio_manager.get_current_position()
    
    def on_set_end_time(self) -> float:
        """Set end time to current position"""
        return self.audio_manager.get_current_position()
    
    def on_time_change(self, start_time: float, end_time: float):
        """Handle time changes from UI"""
        # Validation could be added here
        pass
    
    def on_position_update(self, position: float):
        """Handle position updates from audio manager"""
        self.preview_frame.update_position_display(position)
    
    # Song details
    def on_add_to_playlist(self, page: int, comment: str, start_time: float, end_time: float, volume: float):
        """Add current file to playlist"""
        if not self.current_file:
            messagebox.showerror("Error", "Please load a file first")
            return
        
        if start_time >= end_time:
            messagebox.showerror("Error", "End time must be greater than start time")
            return
        
        song = Song(
            file_path=self.current_file,
            start_time=start_time,
            end_time=end_time,
            page=page,
            comment=comment,
            volume=volume
        )
        
        self.playlist.add_song(song)
        self.playlist_frame.refresh_display(self.playlist)
        self.status_bar.set_status(f"Added song to playlist ({len(self.playlist)} songs)")
    
    # Playlist operations
    def on_playlist_move_up(self, index: int):
        """Move playlist item up"""
        if index > 0:
            self.playlist.swap_songs(index, index - 1)
            self.playlist_frame.refresh_display(self.playlist)
            self.playlist_frame.select_item(index - 1)
    
    def on_playlist_move_down(self, index: int):
        """Move playlist item down"""
        if index < len(self.playlist) - 1:
            self.playlist.swap_songs(index, index + 1)
            self.playlist_frame.refresh_display(self.playlist)
            self.playlist_frame.select_item(index + 1)
    
    def on_playlist_remove(self, index: int):
        """Remove playlist item"""
        self.playlist.remove_song(index)
        self.playlist_frame.refresh_display(self.playlist)
    
    def on_playlist_reorder(self, from_index: int, to_index: int):
        """Reorder playlist via drag and drop"""
        self.playlist.move_song(from_index, to_index)
        self.playlist_frame.refresh_display(self.playlist)
    
    def on_playlist_play(self):
        """Start playlist playback"""
        if len(self.playlist) == 0:
            messagebox.showerror("Error", "Playlist is empty")
            return
        
        self.playlist.set_current_index(0)
        self.play_current_song()
    
    def play_current_song(self):
        """Play the current song in the playlist"""
        current_song = self.playlist.current_song
        if current_song:
            try:
                self.audio_manager.load_file(current_song.file_path)
                self.audio_manager.play_song(current_song)
                
                index = self.playlist.current_index
                total = len(self.playlist)
                filename = os.path.basename(current_song.file_path)
                self.status_bar.set_status(
                    f"Playing: {filename} ({index + 1}/{total}) - Waiting for AdvanceSong command"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not play file: {e}")
                self.advance_song()
    
    def on_song_finished(self):
        """Called when current song finishes playing"""
        current_song = self.playlist.current_song
        if current_song:
            index = self.playlist.current_index
            total = len(self.playlist)
            filename = os.path.basename(current_song.file_path)
            self.status_bar.set_status(
                f"Song finished: {filename} ({index + 1}/{total}) - Waiting for AdvanceSong command"
            )
    
    def advance_song(self):
        """Advance to next song (called by network command)"""
        next_song = self.playlist.advance_to_next()
        if next_song:
            self.play_current_song()
        else:
            self.status_bar.set_status("Playlist completed")
    
    def on_playlist_stop(self):
        """Stop playlist playback"""
        self.audio_manager.stop_playback()
        self.playlist.set_current_index(-1)
        self.status_bar.set_status("Playlist stopped")
    
    def on_playlist_save(self):
        """Save playlist to file"""
        if len(self.playlist) == 0:
            messagebox.showerror("Error", "Playlist is empty")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Playlist",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.playlist.save_to_file(filename)
                self.status_bar.set_status(f"Playlist saved: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save playlist: {e}")
    
    def on_playlist_load(self):
        """Load playlist from file"""
        filename = filedialog.askopenfilename(
            title="Load Playlist",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.playlist.load_from_file(filename)
                self.playlist_frame.refresh_display(self.playlist)
                self.status_bar.set_status(f"Playlist loaded: {os.path.basename(filename)} ({len(self.playlist)} songs)")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load playlist: {e}")
    
    def on_volume_changed(self, song_index: int, volume: float):
        """Handle individual song volume change"""
        if 0 <= song_index < len(self.playlist):
            self.playlist[song_index].volume = volume
            self.playlist_frame.refresh_display(self.playlist)
            self.status_bar.set_status(f"Updated volume for song {song_index + 1}")
    
    def on_volumes_normalized(self):
        """Handle volume normalization completion"""
        self.playlist_frame.refresh_display(self.playlist)
        self.status_bar.set_status("All volumes normalized")
    
    def cleanup(self):
        """Cleanup resources before closing"""
        self.audio_manager.cancel_all_timers()
        self.network_listener.stop_listening()
