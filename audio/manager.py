"""
Audio playback management and control
"""
import pygame
import threading
import time
from typing import Optional, Callable
from models.playlist import Song

class AudioManager:
    """Handles audio playback, fading, and timing"""
    
    def __init__(self):
        self.is_playing = False
        self.is_preview_playing = False
        self.fade_duration = 0.5  # Half second fade
        self.current_song_volume = 1.0  # Track current song's base volume
        
        # Preview tracking
        self.preview_start_time = 0
        self.preview_start_timestamp = 0
        self.preview_pause_position = 0
        
        # Timers
        self.fade_timer: Optional[threading.Timer] = None
        self.end_timer: Optional[threading.Timer] = None
        self.position_update_timer: Optional[threading.Timer] = None
        self.active_fade_timers = []
        
        # Callbacks
        self.position_callback: Optional[Callable[[float], None]] = None
        self.song_finished_callback: Optional[Callable[[], None]] = None
    
    def set_position_callback(self, callback: Callable[[float], None]) -> None:
        """Set callback for position updates"""
        self.position_callback = callback
    
    def set_song_finished_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for when song finishes"""
        self.song_finished_callback = callback
    
    def load_file(self, file_path: str) -> None:
        """Load an audio file"""
        pygame.mixer.music.load(file_path)
    
    def play_preview(self, start_time: float, end_time: float, resume: bool = False) -> None:
        """Play preview of a song segment"""
        pygame.mixer.music.set_volume(1.0)
        
        if resume and self.preview_pause_position > 0:
            start_pos = self.preview_pause_position
            self.preview_pause_position = 0
        else:
            start_pos = start_time
        
        pygame.mixer.music.play(start=start_pos)
        self.is_preview_playing = True
        self.preview_start_time = start_pos
        self.preview_start_timestamp = time.time()
        self.preview_end_time = end_time
        
        self._start_position_tracking()
    
    def pause_preview(self) -> None:
        """Pause preview playback"""
        if self.is_preview_playing:
            # Calculate current position before pausing
            elapsed_time = time.time() - self.preview_start_timestamp
            self.preview_pause_position = self.preview_start_time + elapsed_time
            
            pygame.mixer.music.pause()
            self.is_preview_playing = False
            
            if self.position_update_timer:
                self.position_update_timer.cancel()
                self.position_update_timer = None
        elif self.preview_pause_position > 0:
            # Resume from pause
            pygame.mixer.music.unpause()
            self.is_preview_playing = True
            self.preview_start_time = self.preview_pause_position
            self.preview_start_timestamp = time.time()
            self.preview_pause_position = 0
            self._start_position_tracking()
    
    def stop_preview(self) -> None:
        """Stop preview playback"""
        self.cancel_all_timers()
        pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(1.0)
        self.is_preview_playing = False
        self.preview_pause_position = 0
        
        if self.position_callback:
            self.position_callback(0)
    
    def play_song(self, song: Song) -> None:
        """Play a full song with fade out"""
        pygame.mixer.music.set_volume(song.volume)  # Set song-specific volume
        pygame.mixer.music.play(start=song.start_time)
        self.is_playing = True
        
        # Store current song volume for fade calculations
        self.current_song_volume = song.volume
        
        # Calculate duration and schedule fade out
        duration = song.duration
        fade_start_time = max(0, duration - self.fade_duration)
        
        # Schedule fade out
        self.fade_timer = threading.Timer(fade_start_time, self._start_fade_out)
        self.fade_timer.start()
        
        # Schedule song end
        self.end_timer = threading.Timer(duration, self._song_finished)
        self.end_timer.start()
    
    def stop_playback(self) -> None:
        """Stop all playback"""
        self.cancel_all_timers()
        pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(1.0)
        self.is_playing = False
    
    def get_current_position(self) -> float:
        """Get current playback position"""
        if self.is_preview_playing:
            elapsed_time = time.time() - self.preview_start_timestamp
            return self.preview_start_time + elapsed_time
        elif self.preview_pause_position > 0:
            return self.preview_pause_position
        return 0
    
    def cancel_all_timers(self) -> None:
        """Cancel all active timers"""
        if self.fade_timer:
            self.fade_timer.cancel()
            self.fade_timer = None
            
        if self.end_timer:
            self.end_timer.cancel()
            self.end_timer = None
            
        if self.position_update_timer:
            self.position_update_timer.cancel()
            self.position_update_timer = None
            
        # Cancel all fade step timers
        for timer in self.active_fade_timers:
            timer.cancel()
        self.active_fade_timers.clear()
    
    def _start_position_tracking(self) -> None:
        """Start tracking playback position"""
        self._update_position()
    
    def _update_position(self) -> None:
        """Update the current playback position"""
        if self.is_preview_playing and pygame.mixer.music.get_busy():
            elapsed_time = time.time() - self.preview_start_timestamp
            current_pos = self.preview_start_time + elapsed_time
            
            # Check if we've reached the end time
            if current_pos >= self.preview_end_time:
                self.stop_preview()
                return
                
            # Update callback
            if self.position_callback:
                self.position_callback(current_pos)
            
            # Schedule next update
            self.position_update_timer = threading.Timer(0.01, self._update_position)
            self.position_update_timer.start()
        elif self.is_preview_playing and not pygame.mixer.music.get_busy():
            self.stop_preview()
    
    def _start_fade_out(self) -> None:
        """Start the fade out process"""
        self._fade_out_volume(self.current_song_volume)
    
    def _fade_out_volume(self, current_volume: float) -> None:
        """Recursively fade out the volume"""
        if current_volume <= 0:
            pygame.mixer.music.set_volume(0)
            return
            
        fade_steps = 20
        volume_step = self.current_song_volume / fade_steps  # Use song's base volume for calculations
        step_duration = self.fade_duration / fade_steps
        
        new_volume = max(0, current_volume - volume_step)
        pygame.mixer.music.set_volume(new_volume)
        
        if new_volume > 0:
            fade_timer = threading.Timer(step_duration, 
                                       lambda: self._fade_out_volume(new_volume))
            self.active_fade_timers.append(fade_timer)
            fade_timer.start()
    
    def _song_finished(self) -> None:
        """Called when current song finishes"""
        pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(1.0)
        self.is_playing = False
        
        if self.song_finished_callback:
            self.song_finished_callback()
