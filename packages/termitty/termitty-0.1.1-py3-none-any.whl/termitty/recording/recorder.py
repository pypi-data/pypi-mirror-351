"""
Session recorder for capturing terminal activity.

This module provides the SessionRecorder class that captures all input
and output during a terminal session for later playback or analysis.
"""

import time
import logging
from typing import Optional, Union, Callable, Any
from pathlib import Path
import json
import gzip

from .formats import Recording, RecordingFormat, EventType, RecordingHeader
from ..core.exceptions import SessionStateException

logger = logging.getLogger(__name__)


class SessionRecorder:
    """
    Records terminal session activity.
    
    This class captures all input and output during a terminal session,
    creating recordings that can be played back or analyzed later.
    
    Features:
    - Real-time recording with minimal overhead
    - Multiple output formats (native, asciinema)
    - Compression support
    - Event markers for navigation
    - Pause/resume functionality
    """
    
    def __init__(self,
                 width: int = 80,
                 height: int = 24,
                 title: Optional[str] = None):
        """
        Initialize a session recorder.
        
        Args:
            width: Terminal width
            height: Terminal height
            title: Optional title for the recording
        """
        self.recording = Recording(
            header=RecordingHeader(
                width=width,
                height=height,
                title=title
            )
        )
        
        self._recording = False
        self._paused = False
        self._start_time = None
        
        # Callbacks
        self._on_input: Optional[Callable[[str], None]] = None
        self._on_output: Optional[Callable[[str], None]] = None
        
        logger.debug(f"Created recorder: {width}x{height}")
    
    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording and not self._paused
    
    @property
    def duration(self) -> float:
        """Get current recording duration in seconds."""
        if self._start_time:
            return time.time() - self._start_time
        return 0.0
    
    def start(self):
        """Start recording."""
        if self._recording:
            logger.warning("Recording already in progress")
            return
        
        self._recording = True
        self._paused = False
        self._start_time = self.recording.header.timestamp
        
        logger.info(f"Started recording: {self.recording.id}")
    
    def stop(self) -> Recording:
        """
        Stop recording and return the recording.
        
        Returns:
            The completed recording
        """
        if not self._recording:
            raise SessionStateException("No recording in progress")
        
        self._recording = False
        self._paused = False
        
        # Add final metadata
        self.recording.metadata["duration"] = self.duration
        self.recording.metadata["event_count"] = len(self.recording.events)
        
        logger.info(f"Stopped recording: {self.recording.id} ({self.duration:.1f}s)")
        
        return self.recording
    
    def pause(self):
        """Pause recording."""
        if not self._recording:
            raise SessionStateException("No recording in progress")
        
        self._paused = True
        logger.debug("Recording paused")
    
    def resume(self):
        """Resume recording."""
        if not self._recording:
            raise SessionStateException("No recording in progress")
        
        self._paused = False
        logger.debug("Recording resumed")
    
    def record_input(self, data: Union[str, bytes]):
        """
        Record user input.
        
        Args:
            data: Input data to record
        """
        if not self.is_recording:
            return
        
        self.recording.add_input(data)
        
        if self._on_input:
            try:
                self._on_input(data if isinstance(data, str) else data.decode('utf-8', errors='replace'))
            except Exception as e:
                logger.error(f"Input callback error: {e}")
    
    def record_output(self, data: Union[str, bytes]):
        """
        Record terminal output.
        
        Args:
            data: Output data to record
        """
        if not self.is_recording:
            return
        
        self.recording.add_output(data)
        
        if self._on_output:
            try:
                self._on_output(data if isinstance(data, str) else data.decode('utf-8', errors='replace'))
            except Exception as e:
                logger.error(f"Output callback error: {e}")
    
    def record_resize(self, width: int, height: int):
        """
        Record terminal resize event.
        
        Args:
            width: New terminal width
            height: New terminal height
        """
        if not self.is_recording:
            return
        
        self.recording.add_resize(width, height)
        logger.debug(f"Recorded resize: {width}x{height}")
    
    def add_marker(self, name: str, description: Optional[str] = None):
        """
        Add a named marker to the recording.
        
        Markers can be used for navigation during playback.
        
        Args:
            name: Marker name
            description: Optional description
        """
        if not self._recording:  # Allow markers even when paused
            raise SessionStateException("No recording in progress")
        
        self.recording.add_marker(name, description)
        logger.debug(f"Added marker: {name}")
    
    def set_input_callback(self, callback: Optional[Callable[[str], None]]):
        """Set callback for input events."""
        self._on_input = callback
    
    def set_output_callback(self, callback: Optional[Callable[[str], None]]):
        """Set callback for output events."""
        self._on_output = callback
    
    def save(self,
             filename: Union[str, Path],
             format: RecordingFormat = RecordingFormat.TERMITTY,
             compress: bool = False) -> Path:
        """
        Save the recording to a file.
        
        Args:
            filename: Output filename
            format: Recording format to use
            compress: Whether to compress the output
        
        Returns:
            Path to the saved file
        """
        if self._recording:
            logger.warning("Saving while still recording")
        
        filepath = Path(filename)
        
        # Add extension if not present
        if not filepath.suffix:
            if format == RecordingFormat.ASCIINEMA:
                filepath = filepath.with_suffix('.cast')
            elif compress:
                filepath = filepath.with_suffix('.json.gz')
            else:
                filepath = filepath.with_suffix('.json')
        
        # Convert to appropriate format
        if format == RecordingFormat.ASCIINEMA:
            content = self.recording.to_asciinema_v2()
            mode = 'w'
        else:
            # JSON or native format
            content = json.dumps(self.recording.to_dict(), indent=2)
            mode = 'w'
        
        # Write file
        if compress and not format == RecordingFormat.ASCIINEMA:
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(filepath, mode, encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Saved recording to: {filepath}")
        return filepath
    
    @classmethod
    def load(cls, filename: Union[str, Path]) -> 'SessionRecorder':
        """
        Load a recording from file.
        
        Args:
            filename: Path to recording file
        
        Returns:
            SessionRecorder with loaded recording
        """
        filepath = Path(filename)
        
        # Detect format and compression
        if filepath.suffix == '.cast':
            # Asciinema format
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            recording = Recording.from_asciinema_v2(content)
        elif filepath.suffix == '.gz':
            # Compressed JSON
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            recording = Recording.from_dict(data)
        else:
            # Regular JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            recording = Recording.from_dict(data)
        
        # Create recorder with loaded recording
        recorder = cls(
            width=recording.header.width,
            height=recording.header.height,
            title=recording.header.title
        )
        recorder.recording = recording
        
        logger.info(f"Loaded recording: {recording.id}")
        return recorder
    
    def get_statistics(self) -> dict:
        """
        Get recording statistics.
        
        Returns:
            Dictionary with recording stats
        """
        stats = {
            "id": self.recording.id,
            "duration": self.duration,
            "event_count": len(self.recording.events),
            "input_count": sum(1 for e in self.recording.events if e.event_type == EventType.INPUT),
            "output_count": sum(1 for e in self.recording.events if e.event_type == EventType.OUTPUT),
            "marker_count": sum(1 for e in self.recording.events if e.event_type == EventType.MARKER),
            "is_recording": self.is_recording,
            "is_paused": self._paused
        }
        
        # Calculate data sizes
        input_size = sum(len(e.data) for e in self.recording.events if e.event_type == EventType.INPUT)
        output_size = sum(len(e.data) for e in self.recording.events if e.event_type == EventType.OUTPUT)
        
        stats["input_bytes"] = input_size
        stats["output_bytes"] = output_size
        stats["total_bytes"] = input_size + output_size
        
        return stats