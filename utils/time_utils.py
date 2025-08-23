"""
Time formatting and conversion utilities
"""

def seconds_to_time_string(seconds: float, include_ms: bool = False) -> str:
    """Convert seconds to time string format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if include_ms:
        milliseconds = int((seconds % 1) * 1000)
        return f"{minutes}:{secs:02d}.{milliseconds:03d}"
    else:
        return f"{minutes}:{secs:02d}"

def time_components_to_seconds(minutes: int, seconds: int, milliseconds: int = 0) -> float:
    """Convert time components to total seconds"""
    return minutes * 60 + seconds + milliseconds / 1000.0

def seconds_to_time_components(seconds: float) -> tuple[int, int, int]:
    """Convert seconds to time components (minutes, seconds, milliseconds)"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return minutes, secs, milliseconds

class TimeConverter:
    """Helper class for time conversions with validation"""
    
    @staticmethod
    def validate_time_components(minutes: int, seconds: int, milliseconds: int) -> bool:
        """Validate time components are within valid ranges"""
        return (0 <= minutes <= 999 and 
                0 <= seconds <= 59 and 
                0 <= milliseconds <= 999)
    
    @staticmethod
    def clamp_time_components(minutes: int, seconds: int, milliseconds: int) -> tuple[int, int, int]:
        """Clamp time components to valid ranges"""
        minutes = max(0, min(999, minutes))
        seconds = max(0, min(59, seconds))
        milliseconds = max(0, min(999, milliseconds))
        return minutes, seconds, milliseconds
    
    @staticmethod
    def format_duration(start_seconds: float, end_seconds: float, include_ms: bool = True) -> str:
        """Format a duration between two time points"""
        duration = end_seconds - start_seconds
        return seconds_to_time_string(duration, include_ms)
