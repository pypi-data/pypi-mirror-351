"""
I/O handler for interactive shell sessions.

This module manages the real-time input/output streams between Termitty
and the remote shell, including buffering, encoding, and event handling.
"""

import threading
import queue
import time
import logging
from typing import Optional, Callable, Any, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IOEventType(Enum):
    """Types of I/O events."""
    DATA_RECEIVED = "data_received"
    DATA_SENT = "data_sent"
    ERROR = "error"
    EOF = "eof"
    TIMEOUT = "timeout"


@dataclass
class IOEvent:
    """Represents an I/O event."""
    event_type: IOEventType
    data: Optional[Union[str, bytes]] = None
    error: Optional[Exception] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class IOHandler:
    """
    Handles real-time I/O for interactive shell sessions.
    
    This class manages the bidirectional flow of data between the local
    terminal and the remote shell, handling encoding, buffering, and
    event notifications.
    """
    
    def __init__(self, 
                 channel,
                 encoding: str = 'utf-8',
                 buffer_size: int = 4096):
        """
        Initialize the I/O handler.
        
        Args:
            channel: The SSH channel for communication
            encoding: Character encoding to use
            buffer_size: Size of read buffer
        """
        self.channel = channel
        self.encoding = encoding
        self.buffer_size = buffer_size
        
        # Queues for thread-safe communication
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.event_queue = queue.Queue()
        
        # Thread control
        self._stop_event = threading.Event()
        self._reader_thread = None
        self._writer_thread = None
        
        # Callbacks
        self._data_callback: Optional[Callable[[bytes], None]] = None
        self._event_callback: Optional[Callable[[IOEvent], None]] = None
        
        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.start_time = time.time()
        
        # Buffer for incomplete data
        self._incomplete_buffer = b''
    
    def start(self):
        """Start the I/O handler threads."""
        if self._reader_thread or self._writer_thread:
            raise RuntimeError("I/O handler already started")
        
        self._stop_event.clear()
        
        # Start reader thread
        self._reader_thread = threading.Thread(
            target=self._reader_loop,
            name="IOHandler-Reader",
            daemon=True
        )
        self._reader_thread.start()
        
        # Start writer thread
        self._writer_thread = threading.Thread(
            target=self._writer_loop,
            name="IOHandler-Writer",
            daemon=True
        )
        self._writer_thread.start()
        
        logger.debug("I/O handler started")
    
    def stop(self, timeout: float = 5.0):
        """
        Stop the I/O handler threads.
        
        Args:
            timeout: Maximum time to wait for threads to stop
        """
        self._stop_event.set()
        
        # Wait for threads to stop
        if self._reader_thread:
            self._reader_thread.join(timeout)
            if self._reader_thread.is_alive():
                logger.warning("Reader thread did not stop cleanly")
        
        if self._writer_thread:
            self._writer_thread.join(timeout)
            if self._writer_thread.is_alive():
                logger.warning("Writer thread did not stop cleanly")
        
        self._reader_thread = None
        self._writer_thread = None
        
        logger.debug("I/O handler stopped")
    
    def send(self, data: Union[str, bytes]):
        """
        Send data to the remote shell.
        
        Args:
            data: Data to send (string or bytes)
        """
        if isinstance(data, str):
            data = data.encode(self.encoding)
        
        self.input_queue.put(data)
    
    def send_line(self, line: str):
        """
        Send a line of text with newline.
        
        Args:
            line: Line to send (newline will be added)
        """
        self.send(line + '\n')
    
    def read(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Read data from the output queue.
        
        Args:
            timeout: Maximum time to wait for data
        
        Returns:
            Data if available, None if timeout
        """
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def read_until(self, 
                   pattern: Union[str, bytes],
                   timeout: float = 30.0) -> Optional[bytes]:
        """
        Read data until a pattern is found.
        
        Args:
            pattern: Pattern to search for
            timeout: Maximum time to wait
        
        Returns:
            All data up to and including the pattern, or None if timeout
        """
        if isinstance(pattern, str):
            pattern = pattern.encode(self.encoding)
        
        buffer = b''
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            data = self.read(timeout=0.1)
            if data:
                buffer += data
                if pattern in buffer:
                    return buffer
        
        # Timeout reached
        self._emit_event(IOEvent(IOEventType.TIMEOUT, data=buffer))
        return None
    
    def set_data_callback(self, callback: Optional[Callable[[bytes], None]]):
        """
        Set callback for when data is received.
        
        Args:
            callback: Function to call with received data
        """
        self._data_callback = callback
    
    def set_event_callback(self, callback: Optional[Callable[[IOEvent], None]]):
        """
        Set callback for I/O events.
        
        Args:
            callback: Function to call with events
        """
        self._event_callback = callback
    
    def get_statistics(self) -> dict:
        """
        Get I/O statistics.
        
        Returns:
            Dictionary with statistics
        """
        uptime = time.time() - self.start_time
        return {
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'uptime_seconds': uptime,
            'send_rate_bps': self.bytes_sent / uptime if uptime > 0 else 0,
            'receive_rate_bps': self.bytes_received / uptime if uptime > 0 else 0,
        }
    
    def _reader_loop(self):
        """Reader thread main loop."""
        logger.debug("Reader thread started")
        
        while not self._stop_event.is_set():
            try:
                # Check if channel is ready to read
                if self.channel.recv_ready():
                    # Read available data
                    data = self.channel.recv(self.buffer_size)
                    
                    if data:
                        self.bytes_received += len(data)
                        
                        # Add to output queue
                        self.output_queue.put(data)
                        
                        # Call data callback if set
                        if self._data_callback:
                            try:
                                self._data_callback(data)
                            except Exception as e:
                                logger.error(f"Data callback error: {e}")
                        
                        # Emit event
                        self._emit_event(IOEvent(IOEventType.DATA_RECEIVED, data=data))
                    else:
                        # Empty data means EOF
                        self._emit_event(IOEvent(IOEventType.EOF))
                        break
                
                # Check for stderr data
                if self.channel.recv_stderr_ready():
                    stderr_data = self.channel.recv_stderr(self.buffer_size)
                    if stderr_data:
                        # Add stderr to output queue (could separate if needed)
                        self.output_queue.put(stderr_data)
                        self.bytes_received += len(stderr_data)
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Reader thread error: {e}")
                self._emit_event(IOEvent(IOEventType.ERROR, error=e))
                break
        
        logger.debug("Reader thread stopped")
    
    def _writer_loop(self):
        """Writer thread main loop."""
        logger.debug("Writer thread started")
        
        while not self._stop_event.is_set():
            try:
                # Get data to send (with timeout to check stop event)
                data = self.input_queue.get(timeout=0.1)
                
                if data:
                    # Send all data
                    sent = 0
                    while sent < len(data):
                        n = self.channel.send(data[sent:])
                        if n <= 0:
                            raise IOError("Channel send returned 0")
                        sent += n
                        self.bytes_sent += n
                    
                    # Emit event
                    self._emit_event(IOEvent(IOEventType.DATA_SENT, data=data))
                    
            except queue.Empty:
                # No data to send, continue
                continue
            except Exception as e:
                logger.error(f"Writer thread error: {e}")
                self._emit_event(IOEvent(IOEventType.ERROR, error=e))
                break
        
        logger.debug("Writer thread stopped")
    
    def _emit_event(self, event: IOEvent):
        """Emit an I/O event."""
        # Add to event queue
        try:
            self.event_queue.put_nowait(event)
        except queue.Full:
            logger.warning("Event queue full, dropping event")
        
        # Call event callback if set
        if self._event_callback:
            try:
                self._event_callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")
    
    def flush_output(self) -> bytes:
        """
        Flush all pending output data.
        
        Returns:
            All pending output data
        """
        data = b''
        while True:
            try:
                chunk = self.output_queue.get_nowait()
                data += chunk
            except queue.Empty:
                break
        return data
    
    def clear_queues(self):
        """Clear all queues."""
        # Clear output queue
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
        
        # Clear input queue
        while not self.input_queue.empty():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break
        
        # Clear event queue
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except queue.Empty:
                break