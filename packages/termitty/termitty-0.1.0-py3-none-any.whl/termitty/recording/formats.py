"""
Recording formats and data structures for session recordings.

This module defines the formats used for recording terminal sessions,
including compatibility with standard formats like asciinema.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Union
import json
import time
import uuid


class RecordingFormat(Enum):
    """Supported recording formats."""
    TERMITTY = "termitty"      # Native Termitty format
    ASCIINEMA = "asciinema"    # asciinema v2 format
    JSON = "json"               # Simple JSON format
    
    
class EventType(Enum):
    """Types of events in a recording."""
    INPUT = "i"        # User input
    OUTPUT = "o"       # Terminal output
    RESIZE = "r"       # Terminal resize
    MARKER = "m"       # User-defined marker
    ERROR = "e"        # Error event
    

@dataclass
class RecordingEvent:
    """A single event in a recording."""
    timestamp: float                    # Seconds since start
    event_type: EventType              # Type of event
    data: Union[str, bytes]            # Event data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "data": self.data if isinstance(self.data, str) else self.data.decode('utf-8', errors='replace'),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecordingEvent':
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            event_type=EventType(data["event_type"]),
            data=data["data"],
            metadata=data.get("metadata", {})
        )


@dataclass
class RecordingHeader:
    """Header information for a recording."""
    version: int = 2                   # Format version
    width: int = 80                    # Terminal width
    height: int = 24                   # Terminal height
    timestamp: float = field(default_factory=time.time)  # Start time
    title: Optional[str] = None        # Recording title
    env: Dict[str, Any] = field(default_factory=dict)    # Environment info
    
    def __post_init__(self):
        """Initialize default environment info."""
        if not self.env:
            self.env = {
                "SHELL": "/bin/bash",
                "TERM": "xterm-256color"
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "width": self.width,
            "height": self.height,
            "timestamp": self.timestamp,
            "title": self.title,
            "env": self.env
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecordingHeader':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Recording:
    """A complete terminal session recording."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    header: RecordingHeader = field(default_factory=RecordingHeader)
    events: List[RecordingEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event_type: EventType, data: Union[str, bytes], metadata: Optional[Dict[str, Any]] = None):
        """Add an event to the recording."""
        timestamp = time.time() - self.header.timestamp
        event = RecordingEvent(
            timestamp=timestamp,
            event_type=event_type,
            data=data,
            metadata=metadata or {}
        )
        self.events.append(event)
    
    def add_input(self, data: Union[str, bytes]):
        """Add user input event."""
        self.add_event(EventType.INPUT, data)
    
    def add_output(self, data: Union[str, bytes]):
        """Add terminal output event."""
        self.add_event(EventType.OUTPUT, data)
    
    def add_resize(self, width: int, height: int):
        """Add terminal resize event."""
        self.add_event(
            EventType.RESIZE,
            f"{width}x{height}",
            {"width": width, "height": height}
        )
    
    def add_marker(self, name: str, description: Optional[str] = None):
        """Add a named marker for navigation."""
        self.add_event(
            EventType.MARKER,
            name,
            {"description": description} if description else {}
        )
    
    def duration(self) -> float:
        """Get total duration of recording in seconds."""
        if not self.events:
            return 0.0
        return self.events[-1].timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "header": self.header.to_dict(),
            "events": [e.to_dict() for e in self.events],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recording':
        """Create from dictionary."""
        recording = cls(
            id=data.get("id", str(uuid.uuid4())),
            header=RecordingHeader.from_dict(data["header"]),
            metadata=data.get("metadata", {})
        )
        recording.events = [RecordingEvent.from_dict(e) for e in data["events"]]
        return recording
    
    def to_asciinema_v2(self) -> str:
        """Convert to asciinema v2 format."""
        # Header
        header = {
            "version": 2,
            "width": self.header.width,
            "height": self.header.height,
            "timestamp": self.header.timestamp,
            "env": self.header.env
        }
        if self.header.title:
            header["title"] = self.header.title
        
        lines = [json.dumps(header)]
        
        # Events
        for event in self.events:
            if event.event_type == EventType.OUTPUT:
                # asciinema format: [timestamp, "o", data]
                lines.append(json.dumps([
                    event.timestamp,
                    "o",
                    event.data
                ]))
            elif event.event_type == EventType.INPUT:
                # Include input as output with marker
                lines.append(json.dumps([
                    event.timestamp,
                    "o",
                    f"\033[36m{event.data}\033[0m"  # Cyan color for input
                ]))
        
        return '\n'.join(lines)
    
    @classmethod
    def from_asciinema_v2(cls, content: str) -> 'Recording':
        """Create recording from asciinema v2 format."""
        lines = content.strip().split('\n')
        if not lines:
            raise ValueError("Empty asciinema file")
        
        # Parse header
        header_data = json.loads(lines[0])
        header = RecordingHeader(
            version=header_data.get("version", 2),
            width=header_data.get("width", 80),
            height=header_data.get("height", 24),
            timestamp=header_data.get("timestamp", time.time()),
            title=header_data.get("title"),
            env=header_data.get("env", {})
        )
        
        recording = cls(header=header)
        
        # Parse events
        for line in lines[1:]:
            if not line.strip():
                continue
                
            event_data = json.loads(line)
            if len(event_data) >= 3:
                timestamp, event_type, data = event_data[:3]
                
                if event_type == "o":
                    recording.events.append(RecordingEvent(
                        timestamp=timestamp,
                        event_type=EventType.OUTPUT,
                        data=data
                    ))
        
        return recording