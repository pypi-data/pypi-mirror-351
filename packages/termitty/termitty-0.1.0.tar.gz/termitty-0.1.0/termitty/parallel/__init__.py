"""
Parallel execution components for Termitty.

This package provides functionality for executing commands across multiple
hosts in parallel, with support for different execution strategies,
connection pooling, and comprehensive result handling.

Key components:
- ParallelExecutor: Main class for parallel command execution
- ConnectionPool: Efficient connection management
- ParallelResults: Result aggregation and analysis
- ExecutionStrategy: Different execution patterns (parallel, rolling, sequential)

Example:
    from termitty.parallel import ParallelExecutor, HostConfig
    
    executor = ParallelExecutor()
    hosts = [
        HostConfig("server1", "admin", password="pass"),
        HostConfig("server2", "admin", key_file="~/.ssh/id_rsa"),
    ]
    
    results = executor.execute("uptime", hosts)
    print(results.summary())
"""

from .executor import (
    ParallelExecutor,
    ExecutionConfig,
    ExecutionStrategy,
    HostConfig,
    execute_parallel
)
from .results import (
    ParallelResults,
    HostResult,
    ResultStatus,
    ResultsCollector
)
from .pool import ConnectionPool, PooledConnection

__all__ = [
    # Main executor
    'ParallelExecutor',
    'ExecutionConfig',
    'ExecutionStrategy',
    'HostConfig',
    'execute_parallel',
    
    # Results
    'ParallelResults',
    'HostResult',
    'ResultStatus',
    'ResultsCollector',
    
    # Connection pooling
    'ConnectionPool',
    'PooledConnection',
]