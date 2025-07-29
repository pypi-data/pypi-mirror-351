"""
Results handling for parallel execution.

This module provides classes for collecting, aggregating, and analyzing
results from parallel command execution across multiple hosts.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import statistics

from ..transport.base import CommandResult
from ..core.exceptions import TermittyException


class ResultStatus(Enum):
    """Status of a parallel execution result."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class HostResult:
    """Result from a single host."""
    host: str
    status: ResultStatus
    command_result: Optional[CommandResult] = None
    error: Optional[Exception] = None
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ResultStatus.SUCCESS
    
    @property
    def output(self) -> str:
        """Get command output if available."""
        if self.command_result:
            return self.command_result.output
        return ""
    
    @property
    def exit_code(self) -> Optional[int]:
        """Get exit code if available."""
        if self.command_result:
            return self.command_result.exit_code
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'host': self.host,
            'status': self.status.value,
            'success': self.success,
            'output': self.output,
            'exit_code': self.exit_code,
            'error': str(self.error) if self.error else None,
            'duration': self.duration,
            'metadata': self.metadata
        }


@dataclass
class ParallelResults:
    """
    Aggregated results from parallel execution.
    
    This class collects results from multiple hosts and provides
    methods for analysis and reporting.
    """
    
    command: str
    total_hosts: int
    start_time: float = 0.0
    end_time: float = 0.0
    results: Dict[str, HostResult] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.start_time == 0.0:
            self.start_time = time.time()
    
    def add_result(self, host: str, result: HostResult):
        """Add a result for a host."""
        self.results[host] = result
    
    def mark_complete(self):
        """Mark the parallel execution as complete."""
        self.end_time = time.time()
    
    @property
    def duration(self) -> float:
        """Total execution duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def completed_count(self) -> int:
        """Number of completed hosts."""
        return len(self.results)
    
    @property
    def success_count(self) -> int:
        """Number of successful executions."""
        return sum(1 for r in self.results.values() if r.success)
    
    @property
    def failure_count(self) -> int:
        """Number of failed executions."""
        return sum(1 for r in self.results.values() 
                  if r.status in (ResultStatus.FAILED, ResultStatus.ERROR))
    
    @property
    def timeout_count(self) -> int:
        """Number of timed out executions."""
        return sum(1 for r in self.results.values() 
                  if r.status == ResultStatus.TIMEOUT)
    
    @property
    def success_rate(self) -> float:
        """Percentage of successful executions."""
        if self.completed_count == 0:
            return 0.0
        return (self.success_count / self.completed_count) * 100
    
    @property
    def all_succeeded(self) -> bool:
        """Check if all hosts succeeded."""
        return self.success_count == self.total_hosts
    
    @property
    def any_failed(self) -> bool:
        """Check if any host failed."""
        return self.failure_count > 0
    
    def get_successful_hosts(self) -> List[str]:
        """Get list of successful hosts."""
        return [host for host, result in self.results.items() if result.success]
    
    def get_failed_hosts(self) -> List[str]:
        """Get list of failed hosts."""
        return [host for host, result in self.results.items() 
                if result.status in (ResultStatus.FAILED, ResultStatus.ERROR)]
    
    def get_by_status(self, status: ResultStatus) -> Dict[str, HostResult]:
        """Get results filtered by status."""
        return {host: result for host, result in self.results.items() 
                if result.status == status}
    
    def get_outputs(self) -> Dict[str, str]:
        """Get outputs from all hosts."""
        return {host: result.output for host, result in self.results.items() 
                if result.command_result}
    
    def get_unique_outputs(self) -> Dict[str, List[str]]:
        """Group hosts by unique output."""
        output_groups = {}
        for host, result in self.results.items():
            if result.command_result:
                output = result.output.strip()
                if output not in output_groups:
                    output_groups[output] = []
                output_groups[output].append(host)
        return output_groups
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        durations = [r.duration for r in self.results.values() if r.duration > 0]
        
        stats = {
            'total_hosts': self.total_hosts,
            'completed': self.completed_count,
            'successful': self.success_count,
            'failed': self.failure_count,
            'timeout': self.timeout_count,
            'success_rate': self.success_rate,
            'total_duration': self.duration,
        }
        
        if durations:
            stats.update({
                'min_duration': min(durations),
                'max_duration': max(durations),
                'avg_duration': statistics.mean(durations),
                'median_duration': statistics.median(durations),
            })
        
        return stats
    
    def summary(self) -> str:
        """Get a text summary of results."""
        lines = [
            f"Parallel Execution Summary",
            f"Command: {self.command}",
            f"Hosts: {self.completed_count}/{self.total_hosts}",
            f"Success: {self.success_count} ({self.success_rate:.1f}%)",
            f"Failed: {self.failure_count}",
            f"Duration: {self.duration:.2f}s",
        ]
        
        if self.any_failed:
            lines.append(f"\nFailed hosts: {', '.join(self.get_failed_hosts())}")
        
        # Show unique outputs
        unique_outputs = self.get_unique_outputs()
        if len(unique_outputs) > 1:
            lines.append("\nUnique outputs:")
            for output, hosts in unique_outputs.items():
                lines.append(f"  {len(hosts)} hosts: {output[:50]}...")
        
        return '\n'.join(lines)
    
    def raise_on_failure(self):
        """Raise exception if any executions failed."""
        if self.any_failed:
            failed = self.get_failed_hosts()
            raise TermittyException(
                f"Parallel execution failed on {len(failed)} hosts: {', '.join(failed)}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'command': self.command,
            'total_hosts': self.total_hosts,
            'duration': self.duration,
            'statistics': self.get_statistics(),
            'results': {host: result.to_dict() 
                       for host, result in self.results.items()}
        }


class ResultsCollector:
    """
    Collects and manages results from parallel executions.
    
    This class can track multiple parallel executions and provide
    aggregated statistics across all executions.
    """
    
    def __init__(self):
        """Initialize the results collector."""
        self.executions: List[ParallelResults] = []
        self._current_execution: Optional[ParallelResults] = None
    
    def start_execution(self, command: str, hosts: List[str]) -> ParallelResults:
        """Start tracking a new parallel execution."""
        execution = ParallelResults(
            command=command,
            total_hosts=len(hosts),
            start_time=time.time()
        )
        self._current_execution = execution
        self.executions.append(execution)
        return execution
    
    def add_host_result(self, host: str, result: HostResult):
        """Add a result for a host in the current execution."""
        if self._current_execution:
            self._current_execution.add_result(host, result)
    
    def complete_execution(self) -> Optional[ParallelResults]:
        """Mark current execution as complete."""
        if self._current_execution:
            self._current_execution.mark_complete()
            execution = self._current_execution
            self._current_execution = None
            return execution
        return None
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics across all executions."""
        if not self.executions:
            return {}
        
        total_hosts = sum(e.total_hosts for e in self.executions)
        total_success = sum(e.success_count for e in self.executions)
        total_duration = sum(e.duration for e in self.executions)
        
        return {
            'total_executions': len(self.executions),
            'total_hosts': total_hosts,
            'total_success': total_success,
            'overall_success_rate': (total_success / total_hosts * 100) if total_hosts > 0 else 0,
            'total_duration': total_duration,
            'executions': [e.to_dict() for e in self.executions]
        }
    
    def clear(self):
        """Clear all collected results."""
        self.executions.clear()
        self._current_execution = None