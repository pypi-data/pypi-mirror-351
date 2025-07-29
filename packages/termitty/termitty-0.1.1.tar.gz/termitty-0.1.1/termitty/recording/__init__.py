"""
Session recording and playback functionality for Termitty.

This package provides the ability to record terminal sessions for:
- Debugging and troubleshooting
- Creating demos and tutorials
- Audit trails and compliance
- Automated testing

Features:
- Record all input/output with timestamps
- Multiple recording formats (JSON, asciinema)
- Playback at different speeds
- Search and filter recordings
"""

from .recorder import SessionRecorder, RecordingFormat
from .player import SessionPlayer, PlaybackSpeed
from .storage import RecordingStorage, Recording

__all__ = [
    'SessionRecorder',
    'RecordingFormat',
    'SessionPlayer', 
    'PlaybackSpeed',
    'RecordingStorage',
    'Recording',
]