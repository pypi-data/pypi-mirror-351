"""
Session player for playing back recorded terminal sessions.

This module provides the SessionPlayer class that can play back
recorded terminal sessions with various controls and features.
"""

import time
import threading
from enum import Enum
from typing import Optional, Callable, List, Union
from pathlib import Path
import logging

from .formats import Recording, RecordingEvent, EventType
from .recorder import SessionRecorder

logger = logging.getLogger(__name__)


class PlaybackSpeed(Enum):
    """Playback speed options."""
    QUARTER = 0.25
    HALF = 0.5
    NORMAL = 1.0
    DOUBLE = 2.0
    QUAD = 4.0
    INSTANT = 0.0  # No delays


class PlaybackState(Enum):
    """Player state."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"


class SessionPlayer:
    """
    Plays back recorded terminal sessions.
    
    This class provides VCR-like controls for playing back terminal
    recordings, including play, pause, seek, and speed controls.
    
    Features:
    - Variable playback speed
    - Seek to timestamp or marker
    - Event filtering
    - Progress callbacks
    - Real-time or instant playback
    """
    
    def __init__(self, recording: Optional[Recording] = None):
        """
        Initialize session player.
        
        Args:
            recording: Recording to play (can be set later)
        """
        self.recording = recording
        self._state = PlaybackState.STOPPED
        self._speed = PlaybackSpeed.NORMAL
        self._position = 0.0  # Current playback position in seconds
        self._event_index = 0  # Current event index
        
        # Playback thread
        self._playback_thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        # Callbacks
        self._on_output: Optional[Callable[[str], None]] = None
        self._on_input: Optional[Callable[[str], None]] = None
        self._on_resize: Optional[Callable[[int, int], None]] = None
        self._on_marker: Optional[Callable[[str, dict], None]] = None
        self._on_progress: Optional[Callable[[float, float], None]] = None
        
        # Event filters
        self._show_input = True
        self._show_output = True
        self._show_markers = True
    
    @property
    def state(self) -> PlaybackState:
        """Get current playback state."""
        return self._state
    
    @property
    def speed(self) -> PlaybackSpeed:
        """Get current playback speed."""
        return self._speed
    
    @speed.setter
    def speed(self, value: PlaybackSpeed):
        """Set playback speed."""
        self._speed = value
        logger.debug(f"Playback speed set to: {value.value}x")
    
    @property
    def position(self) -> float:
        """Get current playback position in seconds."""
        return self._position
    
    @property
    def duration(self) -> float:
        """Get total recording duration."""
        return self.recording.duration() if self.recording else 0.0
    
    @property
    def progress(self) -> float:
        """Get playback progress as percentage (0-100)."""
        if not self.recording or self.duration == 0:
            return 0.0
        return (self._position / self.duration) * 100
    
    def load(self, recording: Union[Recording, str, Path]):
        """
        Load a recording to play.
        
        Args:
            recording: Recording object or path to recording file
        """
        if isinstance(recording, (str, Path)):
            # Load from file
            recorder = SessionRecorder.load(recording)
            self.recording = recorder.recording
        else:
            self.recording = recording
        
        self.reset()
        logger.info(f"Loaded recording: {self.recording.id}")
    
    def play(self):
        """Start or resume playback."""
        if not self.recording:
            raise ValueError("No recording loaded")
        
        if self._state == PlaybackState.PLAYING:
            logger.warning("Already playing")
            return
        
        if self._state == PlaybackState.PAUSED:
            # Resume from pause
            self._pause_event.clear()
            self._state = PlaybackState.PLAYING
            logger.debug("Resumed playback")
        else:
            # Start new playback
            self._state = PlaybackState.PLAYING
            self._stop_event.clear()
            self._pause_event.clear()
            
            self._playback_thread = threading.Thread(
                target=self._playback_loop,
                name="SessionPlayer",
                daemon=True
            )
            self._playback_thread.start()
            logger.debug("Started playback")
    
    def pause(self):
        """Pause playback."""
        if self._state != PlaybackState.PLAYING:
            logger.warning("Not currently playing")
            return
        
        self._pause_event.set()
        self._state = PlaybackState.PAUSED
        logger.debug("Paused playback")
    
    def stop(self):
        """Stop playback and reset position."""
        if self._state == PlaybackState.STOPPED:
            return
        
        self._stop_event.set()
        self._pause_event.clear()
        
        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=1.0)
        
        self.reset()
        logger.debug("Stopped playback")
    
    def reset(self):
        """Reset playback position to beginning."""
        self._position = 0.0
        self._event_index = 0
        self._state = PlaybackState.STOPPED
    
    def seek(self, position: float):
        """
        Seek to specific position in seconds.
        
        Args:
            position: Target position in seconds
        """
        if not self.recording:
            return
        
        # Clamp position
        position = max(0, min(position, self.duration))
        
        # Find corresponding event index
        self._event_index = 0
        for i, event in enumerate(self.recording.events):
            if event.timestamp > position:
                break
            self._event_index = i
        
        self._position = position
        logger.debug(f"Seeked to: {position:.1f}s")
    
    def seek_to_marker(self, marker_name: str):
        """
        Seek to a named marker.
        
        Args:
            marker_name: Name of marker to seek to
        """
        if not self.recording:
            return
        
        for i, event in enumerate(self.recording.events):
            if event.event_type == EventType.MARKER and event.data == marker_name:
                self.seek(event.timestamp)
                return
        
        logger.warning(f"Marker not found: {marker_name}")
    
    def get_markers(self) -> List[tuple]:
        """
        Get list of all markers in recording.
        
        Returns:
            List of (timestamp, name, description) tuples
        """
        if not self.recording:
            return []
        
        markers = []
        for event in self.recording.events:
            if event.event_type == EventType.MARKER:
                markers.append((
                    event.timestamp,
                    event.data,
                    event.metadata.get("description", "")
                ))
        
        return markers
    
    def set_output_callback(self, callback: Optional[Callable[[str], None]]):
        """Set callback for output events."""
        self._on_output = callback
    
    def set_input_callback(self, callback: Optional[Callable[[str], None]]):
        """Set callback for input events."""
        self._on_input = callback
    
    def set_resize_callback(self, callback: Optional[Callable[[int, int], None]]):
        """Set callback for resize events."""
        self._on_resize = callback
    
    def set_marker_callback(self, callback: Optional[Callable[[str, dict], None]]):
        """Set callback for marker events."""
        self._on_marker = callback
    
    def set_progress_callback(self, callback: Optional[Callable[[float, float], None]]):
        """Set callback for playback progress updates."""
        self._on_progress = callback
    
    def set_event_filters(self, show_input: bool = True, show_output: bool = True, show_markers: bool = True):
        """
        Configure which event types to play back.
        
        Args:
            show_input: Whether to play input events
            show_output: Whether to play output events
            show_markers: Whether to trigger marker callbacks
        """
        self._show_input = show_input
        self._show_output = show_output
        self._show_markers = show_markers
    
    def _playback_loop(self):
        """Main playback loop (runs in thread)."""
        try:
            last_timestamp = 0.0
            
            while self._event_index < len(self.recording.events) and not self._stop_event.is_set():
                # Handle pause
                if self._pause_event.is_set():
                    time.sleep(0.1)
                    continue
                
                # Get current event
                event = self.recording.events[self._event_index]
                
                # Calculate delay
                if self._speed != PlaybackSpeed.INSTANT:
                    delay = (event.timestamp - last_timestamp) / self._speed.value
                    if delay > 0:
                        # Use small sleeps for better responsiveness
                        end_time = time.time() + delay
                        while time.time() < end_time and not self._stop_event.is_set():
                            if self._pause_event.is_set():
                                break
                            time.sleep(0.01)
                
                if self._stop_event.is_set() or self._pause_event.is_set():
                    continue
                
                # Process event
                self._process_event(event)
                
                # Update position
                last_timestamp = event.timestamp
                self._position = event.timestamp
                self._event_index += 1
                
                # Progress callback
                if self._on_progress:
                    try:
                        self._on_progress(self._position, self.duration)
                    except Exception as e:
                        logger.error(f"Progress callback error: {e}")
            
            # Playback finished
            if not self._stop_event.is_set():
                self._state = PlaybackState.FINISHED
                logger.debug("Playback finished")
            
        except Exception as e:
            logger.error(f"Playback error: {e}")
            self._state = PlaybackState.STOPPED
    
    def _process_event(self, event: RecordingEvent):
        """Process a single playback event."""
        try:
            if event.event_type == EventType.OUTPUT and self._show_output:
                if self._on_output:
                    data = event.data if isinstance(event.data, str) else event.data.decode('utf-8', errors='replace')
                    self._on_output(data)
            
            elif event.event_type == EventType.INPUT and self._show_input:
                if self._on_input:
                    data = event.data if isinstance(event.data, str) else event.data.decode('utf-8', errors='replace')
                    self._on_input(data)
            
            elif event.event_type == EventType.RESIZE:
                if self._on_resize:
                    width = event.metadata.get("width", 80)
                    height = event.metadata.get("height", 24)
                    self._on_resize(width, height)
            
            elif event.event_type == EventType.MARKER and self._show_markers:
                if self._on_marker:
                    self._on_marker(event.data, event.metadata)
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")