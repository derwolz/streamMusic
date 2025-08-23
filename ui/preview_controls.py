"""
Preview controls UI component
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable
from utils.time_utils import seconds_to_time_string, time_components_to_seconds, seconds_to_time_components

class PreviewControlsFrame(ttk.LabelFrame):
    """UI frame for preview controls and time selection"""
    
    def __init__(self, parent, 
                 on_play: Callable[[float, float, bool], None],
                 on_pause: Callable[[], None],
                 on_stop: Callable[[], None],
                 on_set_start: Callable[[], float],
                 on_set_end: Callable[[], float],
                 on_time_change: Callable[[float, float], None]):
        super().__init__(parent, text="Preview & Clip Selection", padding="5")
        
        self.on_play = on_play
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.on_set_start = on_set_start
        self.on_set_end = on_set_end
        self.on_time_change = on_time_change
        
        # Variables
        self.start_time = tk.DoubleVar()
        self.end_time = tk.DoubleVar()
        
        # Precision input variables
        self.start_minutes = tk.IntVar()
        self.start_seconds = tk.IntVar()
        self.start_milliseconds = tk.IntVar()
        self.end_minutes = tk.IntVar()
        self.end_seconds = tk.IntVar()
        self.end_milliseconds = tk.IntVar()
        
        # Update flags to prevent recursion
        self._updating_from_precision = False
        self._updating_from_scales = False
        
        self.setup_ui()
        self.bind_events()
    
    def setup_ui(self):
        """Setup the preview controls UI"""
        self.columnconfigure(1, weight=1)
        
        # Time controls
        time_frame = ttk.Frame(self)
        time_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))
        time_frame.columnconfigure(1, weight=1)
        time_frame.columnconfigure(3, weight=1)
        
        ttk.Label(time_frame, text="Start:").grid(row=0, column=0, sticky=tk.W)
        self.start_scale = ttk.Scale(time_frame, from_=0, to=100, variable=self.start_time, orient=tk.HORIZONTAL)
        self.start_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10))
        
        ttk.Label(time_frame, text="End:").grid(row=0, column=2, sticky=tk.W)
        self.end_scale = ttk.Scale(time_frame, from_=0, to=100, variable=self.end_time, orient=tk.HORIZONTAL)
        self.end_scale.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Time labels
        time_label_frame = ttk.Frame(self)
        time_label_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))
        time_label_frame.columnconfigure(1, weight=1)
        time_label_frame.columnconfigure(3, weight=1)
        
        self.start_time_label = ttk.Label(time_label_frame, text="0:00")
        self.start_time_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 10))
        self.end_time_label = ttk.Label(time_label_frame, text="0:00")
        self.end_time_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Millisecond precision inputs
        self.setup_precision_inputs()
        
        # Preview controls
        control_frame = ttk.Frame(self)
        control_frame.grid(row=3, column=0, columnspan=4, pady=(5, 0))
        
        ttk.Button(control_frame, text="Play Preview", command=self.play_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Pause", command=self.pause_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Stop", command=self.stop_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Set Start", command=self.set_start_time).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Set End", command=self.set_end_time).pack(side=tk.LEFT)
        
        # Position tracker
        position_frame = ttk.Frame(self)
        position_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Label(position_frame, text="Position:").pack(side=tk.LEFT, padx=(0, 5))
        self.position_label = ttk.Label(position_frame, text="0:00.000", font=("Courier", 10))
        self.position_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(position_frame, text="Duration:").pack(side=tk.LEFT, padx=(0, 5))
        self.duration_label = ttk.Label(position_frame, text="0:00.000", font=("Courier", 10))
        self.duration_label.pack(side=tk.LEFT)
    
    def setup_precision_inputs(self):
        """Setup millisecond precision input controls"""
        precision_frame = ttk.LabelFrame(self, text="Precise Time Entry", padding="5")
        precision_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        precision_frame.columnconfigure(1, weight=1)
        precision_frame.columnconfigure(4, weight=1)
        
        # Start time precision inputs
        ttk.Label(precision_frame, text="Start:").grid(row=0, column=0, sticky=tk.W)
        
        start_time_frame = ttk.Frame(precision_frame)
        start_time_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 20))
        
        ttk.Label(start_time_frame, text="M:").pack(side=tk.LEFT)
        start_min_spin = ttk.Spinbox(start_time_frame, from_=0, to=59, width=4, 
                                   textvariable=self.start_minutes, command=self.update_from_precision)
        start_min_spin.pack(side=tk.LEFT, padx=(2, 5))
        
        ttk.Label(start_time_frame, text="S:").pack(side=tk.LEFT)
        start_sec_spin = ttk.Spinbox(start_time_frame, from_=0, to=59, width=4, 
                                   textvariable=self.start_seconds, command=self.update_from_precision)
        start_sec_spin.pack(side=tk.LEFT, padx=(2, 5))
        
        ttk.Label(start_time_frame, text="MS:").pack(side=tk.LEFT)
        start_ms_spin = ttk.Spinbox(start_time_frame, from_=0, to=999, width=5, 
                                  textvariable=self.start_milliseconds, command=self.update_from_precision)
        start_ms_spin.pack(side=tk.LEFT, padx=(2, 0))
        
        # End time precision inputs
        ttk.Label(precision_frame, text="End:").grid(row=0, column=3, sticky=tk.W)
        
        end_time_frame = ttk.Frame(precision_frame)
        end_time_frame.grid(row=0, column=4, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(end_time_frame, text="M:").pack(side=tk.LEFT)
        end_min_spin = ttk.Spinbox(end_time_frame, from_=0, to=59, width=4, 
                                 textvariable=self.end_minutes, command=self.update_from_precision)
        end_min_spin.pack(side=tk.LEFT, padx=(2, 5))
        
        ttk.Label(end_time_frame, text="S:").pack(side=tk.LEFT)
        end_sec_spin = ttk.Spinbox(end_time_frame, from_=0, to=59, width=4, 
                                 textvariable=self.end_seconds, command=self.update_from_precision)
        end_sec_spin.pack(side=tk.LEFT, padx=(2, 5))
        
        ttk.Label(end_time_frame, text="MS:").pack(side=tk.LEFT)
        end_ms_spin = ttk.Spinbox(end_time_frame, from_=0, to=999, width=5, 
                                textvariable=self.end_milliseconds, command=self.update_from_precision)
        end_ms_spin.pack(side=tk.LEFT, padx=(2, 0))
    
    def bind_events(self):
        """Bind events for UI controls"""
        # Bind precision input events
        self.start_minutes.trace_add("write", self.on_precision_change)
        self.start_seconds.trace_add("write", self.on_precision_change)
        self.start_milliseconds.trace_add("write", self.on_precision_change)
        self.end_minutes.trace_add("write", self.on_precision_change)
        self.end_seconds.trace_add("write", self.on_precision_change)
        self.end_milliseconds.trace_add("write", self.on_precision_change)
        
        # Bind scale events
        self.start_scale.bind("<Motion>", self.update_time_labels)
        self.end_scale.bind("<Motion>", self.update_time_labels)
        self.start_time.trace_add("write", self.on_time_change_event)
        self.end_time.trace_add("write", self.on_time_change_event)
    
    def set_song_length(self, length: float):
        """Set the maximum song length for the scales"""
        self.start_scale.configure(to=length)
        self.end_scale.configure(to=length)
        self.end_time.set(length)
        self.update_precision_from_scales()
        self.update_time_labels()
        self.update_duration_display()
    
    def update_time_labels(self, event=None):
        """Update the time label displays"""
        start_text = seconds_to_time_string(self.start_time.get())
        end_text = seconds_to_time_string(self.end_time.get())
        self.start_time_label.config(text=start_text)
        self.end_time_label.config(text=end_text)
    
    def on_time_change_event(self, *args):
        """Handle time changes from scales"""
        if self._updating_from_precision:
            return
            
        # Ensure start time is not greater than end time
        if self.start_time.get() > self.end_time.get():
            self.end_time.set(self.start_time.get())
            
        self.update_time_labels()
        self.update_duration_display()
        self.update_precision_from_scales()
        
        # Notify parent
        self.on_time_change(self.start_time.get(), self.end_time.get())
    
    def update_precision_from_scales(self):
        """Update precision input fields from scale values"""
        if self._updating_from_scales:
            return
            
        self._updating_from_scales = True
        
        try:
            # Update start time precision inputs
            start_min, start_sec, start_ms = seconds_to_time_components(self.start_time.get())
            self.start_minutes.set(start_min)
            self.start_seconds.set(start_sec)
            self.start_milliseconds.set(start_ms)
            
            # Update end time precision inputs
            end_min, end_sec, end_ms = seconds_to_time_components(self.end_time.get())
            self.end_minutes.set(end_min)
            self.end_seconds.set(end_sec)
            self.end_milliseconds.set(end_ms)
        finally:
            self._updating_from_scales = False
    
    def on_precision_change(self, *args):
        """Update scale values from precision input fields"""
        if self._updating_from_scales:
            return
            
        self._updating_from_precision = True
        
        try:
            # Calculate start time from precision inputs
            start_total = time_components_to_seconds(
                self.start_minutes.get(),
                self.start_seconds.get(),
                self.start_milliseconds.get()
            )
            
            # Calculate end time from precision inputs
            end_total = time_components_to_seconds(
                self.end_minutes.get(),
                self.end_seconds.get(),
                self.end_milliseconds.get()
            )
            
            # Validate that end >= start
            if end_total < start_total:
                end_total = start_total
                end_min, end_sec, end_ms = seconds_to_time_components(end_total)
                self.end_minutes.set(end_min)
                self.end_seconds.set(end_sec)
                self.end_milliseconds.set(end_ms)
            
            # Update the scale variables
            self.start_time.set(start_total)
            self.end_time.set(end_total)
            
            # Update displays
            self.update_time_labels()
            self.update_duration_display()
            
            # Notify parent
            self.on_time_change(start_total, end_total)
                
        except (tk.TclError, ValueError):
            pass
        finally:
            self._updating_from_precision = False
    
    def update_from_precision(self):
        """Called when spinbox values change via increment/decrement buttons"""
        self.on_precision_change()
    
    def update_duration_display(self):
        """Update the duration display for the current clip"""
        duration = self.end_time.get() - self.start_time.get()
        duration_text = seconds_to_time_string(duration, include_ms=True)
        self.duration_label.config(text=duration_text)
    
    def update_position_display(self, position: float):
        """Update the position display with millisecond precision"""
        position_text = seconds_to_time_string(position, include_ms=True)
        self.position_label.config(text=position_text)
    
    # Control button handlers
    def play_preview(self):
        """Play preview button handler"""
        self.on_play(self.start_time.get(), self.end_time.get(), False)
    
    def pause_preview(self):
        """Pause preview button handler"""
        self.on_pause()
    
    def stop_preview(self):
        """Stop preview button handler"""
        self.on_stop()
    
    def set_start_time(self):
        """Set start time button handler"""
        position = self.on_set_start()
        if position is not None:
            self.start_time.set(position)
            self.update_time_labels()
            self.update_duration_display()
            self.update_precision_from_scales()
    
    def set_end_time(self):
        """Set end time button handler"""
        position = self.on_set_end()
        if position is not None:
            self.end_time.set(position)
            self.update_time_labels()
            self.update_duration_display()
            self.update_precision_from_scales()
    
    def get_times(self) -> tuple[float, float]:
        """Get current start and end times"""
        return self.start_time.get(), self.end_time.get()
