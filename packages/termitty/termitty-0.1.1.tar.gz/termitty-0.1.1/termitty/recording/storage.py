"""
Storage management for terminal recordings.

This module provides functionality for organizing, storing, and
retrieving terminal session recordings.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import shutil
import logging

from .formats import Recording, RecordingFormat

logger = logging.getLogger(__name__)


class RecordingStorage:
    """
    Manages storage and retrieval of terminal recordings.
    
    This class provides a simple database-backed storage system for
    managing recordings, including metadata, search, and organization.
    
    Features:
    - SQLite database for metadata
    - File-based storage for recordings
    - Search and filter capabilities
    - Tag support for organization
    - Import/export functionality
    """
    
    def __init__(self, storage_dir: Union[str, Path]):
        """
        Initialize recording storage.
        
        Args:
            storage_dir: Directory for storing recordings and database
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.storage_dir / "recordings.db"
        self.recordings_dir = self.storage_dir / "recordings"
        self.recordings_dir.mkdir(exist_ok=True)
        
        self._init_database()
        logger.info(f"Initialized storage at: {self.storage_dir}")
    
    def _init_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recordings (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    timestamp REAL,
                    duration REAL,
                    width INTEGER,
                    height INTEGER,
                    event_count INTEGER,
                    file_path TEXT,
                    format TEXT,
                    compressed BOOLEAN,
                    tags TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON recordings (timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_duration ON recordings (duration)
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recording_tags (
                    recording_id TEXT,
                    tag_id INTEGER,
                    FOREIGN KEY (recording_id) REFERENCES recordings (id),
                    FOREIGN KEY (tag_id) REFERENCES tags (id),
                    PRIMARY KEY (recording_id, tag_id)
                )
            """)
            
            conn.commit()
    
    def save_recording(self,
                      recording: Recording,
                      format: RecordingFormat = RecordingFormat.TERMITTY,
                      compress: bool = True,
                      tags: Optional[List[str]] = None) -> Path:
        """
        Save a recording to storage.
        
        Args:
            recording: Recording to save
            format: Storage format
            compress: Whether to compress
            tags: Optional tags for organization
        
        Returns:
            Path to saved recording file
        """
        # Determine filename
        timestamp_str = datetime.fromtimestamp(recording.header.timestamp).strftime('%Y%m%d_%H%M%S')
        base_name = f"{timestamp_str}_{recording.id[:8]}"
        
        if format == RecordingFormat.ASCIINEMA:
            filename = f"{base_name}.cast"
            compress = False  # Don't compress asciinema files
        elif compress:
            filename = f"{base_name}.json.gz"
        else:
            filename = f"{base_name}.json"
        
        file_path = self.recordings_dir / filename
        
        # Save the recording file
        from .recorder import SessionRecorder
        recorder = SessionRecorder(
            width=recording.header.width,
            height=recording.header.height,
            title=recording.header.title
        )
        recorder.recording = recording
        recorder.save(file_path, format=format, compress=compress)
        
        # Save metadata to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO recordings 
                (id, title, timestamp, duration, width, height, event_count, 
                 file_path, format, compressed, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recording.id,
                recording.header.title or "",
                recording.header.timestamp,
                recording.duration(),
                recording.header.width,
                recording.header.height,
                len(recording.events),
                str(file_path.relative_to(self.storage_dir)),
                format.value,
                compress,
                json.dumps(tags or []),
                json.dumps(recording.metadata)
            ))
            
            # Handle tags
            if tags:
                for tag in tags:
                    # Insert tag if not exists
                    conn.execute("""
                        INSERT OR IGNORE INTO tags (name) VALUES (?)
                    """, (tag,))
                    
                    # Link recording to tag
                    conn.execute("""
                        INSERT OR IGNORE INTO recording_tags (recording_id, tag_id)
                        SELECT ?, id FROM tags WHERE name = ?
                    """, (recording.id, tag))
            
            conn.commit()
        
        logger.info(f"Saved recording: {recording.id} to {file_path}")
        return file_path
    
    def load_recording(self, recording_id: str) -> Optional[Recording]:
        """
        Load a recording by ID.
        
        Args:
            recording_id: Recording ID
        
        Returns:
            Recording object or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT file_path FROM recordings WHERE id = ?
            """, (recording_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Recording not found: {recording_id}")
                return None
            
            file_path = self.storage_dir / row[0]
            
            if not file_path.exists():
                logger.error(f"Recording file missing: {file_path}")
                return None
            
            from .recorder import SessionRecorder
            recorder = SessionRecorder.load(file_path)
            return recorder.recording
    
    def list_recordings(self,
                       tags: Optional[List[str]] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       min_duration: Optional[float] = None,
                       max_duration: Optional[float] = None,
                       limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List recordings with optional filters.
        
        Args:
            tags: Filter by tags (AND operation)
            start_date: Filter by start date
            end_date: Filter by end date
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            limit: Maximum number of results
        
        Returns:
            List of recording metadata dictionaries
        """
        query = """
            SELECT DISTINCT r.id, r.title, r.timestamp, r.duration, 
                   r.width, r.height, r.event_count, r.file_path,
                   r.format, r.compressed, r.tags, r.metadata, r.created_at
            FROM recordings r
        """
        
        conditions = []
        params = []
        
        # Handle tag filtering
        if tags:
            for i, tag in enumerate(tags):
                query += f"""
                    INNER JOIN recording_tags rt{i} ON r.id = rt{i}.recording_id
                    INNER JOIN tags t{i} ON rt{i}.tag_id = t{i}.id AND t{i}.name = ?
                """
                params.append(tag)
        
        # Add other filters
        if start_date:
            conditions.append("r.timestamp >= ?")
            params.append(start_date.timestamp())
        
        if end_date:
            conditions.append("r.timestamp <= ?")
            params.append(end_date.timestamp())
        
        if min_duration is not None:
            conditions.append("r.duration >= ?")
            params.append(min_duration)
        
        if max_duration is not None:
            conditions.append("r.duration <= ?")
            params.append(max_duration)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY r.timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            recordings = []
            for row in cursor:
                recordings.append({
                    "id": row["id"],
                    "title": row["title"],
                    "timestamp": row["timestamp"],
                    "duration": row["duration"],
                    "width": row["width"],
                    "height": row["height"],
                    "event_count": row["event_count"],
                    "file_path": row["file_path"],
                    "format": row["format"],
                    "compressed": bool(row["compressed"]),
                    "tags": json.loads(row["tags"]),
                    "metadata": json.loads(row["metadata"]),
                    "created_at": row["created_at"]
                })
        
        return recordings
    
    def delete_recording(self, recording_id: str) -> bool:
        """
        Delete a recording.
        
        Args:
            recording_id: Recording ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get file path
            cursor = conn.execute("""
                SELECT file_path FROM recordings WHERE id = ?
            """, (recording_id,))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            file_path = self.storage_dir / row[0]
            
            # Delete from database
            conn.execute("DELETE FROM recording_tags WHERE recording_id = ?", (recording_id,))
            conn.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))
            conn.commit()
            
            # Delete file
            if file_path.exists():
                file_path.unlink()
            
            logger.info(f"Deleted recording: {recording_id}")
            return True
    
    def add_tags(self, recording_id: str, tags: List[str]):
        """Add tags to a recording."""
        with sqlite3.connect(self.db_path) as conn:
            for tag in tags:
                # Insert tag if not exists
                conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                
                # Link recording to tag
                conn.execute("""
                    INSERT OR IGNORE INTO recording_tags (recording_id, tag_id)
                    SELECT ?, id FROM tags WHERE name = ?
                """, (recording_id, tag))
            
            # Update tags in recordings table
            cursor = conn.execute("""
                SELECT tags FROM recordings WHERE id = ?
            """, (recording_id,))
            
            row = cursor.fetchone()
            if row:
                existing_tags = json.loads(row[0])
                all_tags = list(set(existing_tags + tags))
                
                conn.execute("""
                    UPDATE recordings SET tags = ? WHERE id = ?
                """, (json.dumps(all_tags), recording_id))
            
            conn.commit()
    
    def remove_tags(self, recording_id: str, tags: List[str]):
        """Remove tags from a recording."""
        with sqlite3.connect(self.db_path) as conn:
            for tag in tags:
                conn.execute("""
                    DELETE FROM recording_tags 
                    WHERE recording_id = ? AND tag_id = (
                        SELECT id FROM tags WHERE name = ?
                    )
                """, (recording_id, tag))
            
            # Update tags in recordings table
            cursor = conn.execute("""
                SELECT tags FROM recordings WHERE id = ?
            """, (recording_id,))
            
            row = cursor.fetchone()
            if row:
                existing_tags = json.loads(row[0])
                remaining_tags = [t for t in existing_tags if t not in tags]
                
                conn.execute("""
                    UPDATE recordings SET tags = ? WHERE id = ?
                """, (json.dumps(remaining_tags), recording_id))
            
            conn.commit()
    
    def get_all_tags(self) -> List[str]:
        """Get list of all tags in use."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name FROM tags ORDER BY name")
            return [row[0] for row in cursor]
    
    def export_recording(self, recording_id: str, output_path: Union[str, Path]):
        """Export a recording to a file."""
        recording = self.load_recording(recording_id)
        if not recording:
            raise ValueError(f"Recording not found: {recording_id}")
        
        output_path = Path(output_path)
        
        # Determine format from extension
        if output_path.suffix == '.cast':
            format = RecordingFormat.ASCIINEMA
        else:
            format = RecordingFormat.TERMITTY
        
        from .recorder import SessionRecorder
        recorder = SessionRecorder(
            width=recording.header.width,
            height=recording.header.height,
            title=recording.header.title
        )
        recorder.recording = recording
        recorder.save(output_path, format=format)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Total recordings
            total = conn.execute("SELECT COUNT(*) FROM recordings").fetchone()[0]
            
            # Total duration
            total_duration = conn.execute("SELECT SUM(duration) FROM recordings").fetchone()[0] or 0
            
            # Total events
            total_events = conn.execute("SELECT SUM(event_count) FROM recordings").fetchone()[0] or 0
            
            # Storage size
            total_size = sum(f.stat().st_size for f in self.recordings_dir.glob("*") if f.is_file())
        
        return {
            "total_recordings": total,
            "total_duration_seconds": total_duration,
            "total_events": total_events,
            "storage_size_bytes": total_size,
            "storage_path": str(self.storage_dir)
        }