"""
Playlist data model and operations
"""
import json
import os
from typing import List, Dict, Any, Optional

class Song:
    """Represents a single song in the playlist"""
    def __init__(self, file_path: str, start_time: float, end_time: float, 
                 page: int = 0, comment: str = "", volume: float = 1.0):
        self.file_path = file_path
        self.start_time = start_time
        self.end_time = end_time
        self.page = page
        self.comment = comment
        self.volume = max(0.0, min(1.0, volume))  # Clamp volume between 0.0 and 1.0
    
    @property
    def duration(self) -> float:
        """Return the duration of the clip in seconds"""
        return self.end_time - self.start_time
    
    @property
    def filename(self) -> str:
        """Return just the filename without path"""
        return os.path.basename(self.file_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert song to dictionary for serialization"""
        return {
            "file_path": self.file_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "page": self.page,
            "comment": self.comment,
            "volume": self.volume
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Song':
        """Create Song from dictionary"""
        return cls(
            file_path=data["file_path"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            page=data.get("page", 0),
            comment=data.get("comment", ""),
            volume=data.get("volume", 1.0)
        )

class Playlist:
    """Manages a collection of songs"""
    def __init__(self):
        self.songs: List[Song] = []
        self._current_index = -1
    
    def add_song(self, song: Song) -> None:
        """Add a song to the playlist"""
        self.songs.append(song)
    
    def remove_song(self, index: int) -> None:
        """Remove a song at the given index"""
        if 0 <= index < len(self.songs):
            del self.songs[index]
            # Adjust current index if necessary
            if self._current_index >= index and self._current_index > 0:
                self._current_index -= 1
            elif self._current_index >= len(self.songs):
                self._current_index = -1
    
    def move_song(self, from_index: int, to_index: int) -> None:
        """Move a song from one position to another"""
        if (0 <= from_index < len(self.songs) and 
            0 <= to_index < len(self.songs) and 
            from_index != to_index):
            song = self.songs.pop(from_index)
            self.songs.insert(to_index, song)
            
            # Adjust current index
            if self._current_index == from_index:
                self._current_index = to_index
            elif from_index < self._current_index <= to_index:
                self._current_index -= 1
            elif to_index <= self._current_index < from_index:
                self._current_index += 1
    
    def swap_songs(self, index1: int, index2: int) -> None:
        """Swap two songs in the playlist"""
        if (0 <= index1 < len(self.songs) and 
            0 <= index2 < len(self.songs)):
            self.songs[index1], self.songs[index2] = self.songs[index2], self.songs[index1]
            
            # Adjust current index
            if self._current_index == index1:
                self._current_index = index2
            elif self._current_index == index2:
                self._current_index = index1
    
    def clear(self) -> None:
        """Clear all songs from the playlist"""
        self.songs.clear()
        self._current_index = -1
    
    @property
    def current_song(self) -> Optional[Song]:
        """Get the currently selected song"""
        if 0 <= self._current_index < len(self.songs):
            return self.songs[self._current_index]
        return None
    
    @property
    def current_index(self) -> int:
        """Get the current song index"""
        return self._current_index
    
    def set_current_index(self, index: int) -> None:
        """Set the current song index"""
        if -1 <= index < len(self.songs):
            self._current_index = index
    
    def advance_to_next(self) -> Optional[Song]:
        """Advance to the next song and return it"""
        if self._current_index < len(self.songs) - 1:
            self._current_index += 1
            return self.current_song
        else:
            self._current_index = -1
            return None
    
    def has_next(self) -> bool:
        """Check if there's a next song"""
        return self._current_index < len(self.songs) - 1
    
    def __len__(self) -> int:
        """Return the number of songs in the playlist"""
        return len(self.songs)
    
    def __getitem__(self, index: int) -> Song:
        """Get a song by index"""
        return self.songs[index]
    
    def __iter__(self):
        """Iterate over songs"""
        return iter(self.songs)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert playlist to dictionary for serialization"""
        return [song.to_dict() for song in self.songs]
    
    def from_dict(self, data: List[Dict[str, Any]]) -> None:
        """Load playlist from dictionary"""
        self.songs = [Song.from_dict(song_data) for song_data in data]
        self._current_index = -1
    
    def save_to_file(self, filename: str) -> None:
        """Save playlist to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filename: str) -> None:
        """Load playlist from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.from_dict(data)
