"""
Configuration management for Termitty.

This module handles all configuration aspects of Termitty, providing a centralized
way to manage settings. It supports multiple configuration sources:
1. Default values (defined in code)
2. Configuration files (INI format)
3. Environment variables
4. Runtime modifications

The precedence order (highest to lowest):
Runtime modifications > Environment variables > Config files > Defaults
"""

import os
import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConnectionConfig:
    """Configuration for SSH connections."""
    
    default_port: int = 22
    default_timeout: float = 30.0
    connection_retries: int = 3
    retry_delay: float = 1.0
    keepalive_interval: float = 5.0
    # Authentication preferences in order
    auth_methods: list = field(default_factory=lambda: ['publickey', 'password', 'keyboard-interactive'])
    known_hosts_policy: str = 'warning'  # 'strict', 'warning', 'auto-add'
    compression: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.default_port < 1 or self.default_port > 65535:
            raise ValueError(f"Invalid port number: {self.default_port}")
        
        if self.default_timeout <= 0:
            raise ValueError(f"Timeout must be positive: {self.default_timeout}")
        
        valid_policies = {'strict', 'warning', 'auto-add'}
        if self.known_hosts_policy not in valid_policies:
            raise ValueError(f"Invalid known_hosts_policy: {self.known_hosts_policy}. "
                           f"Must be one of {valid_policies}")


@dataclass
class TerminalConfig:
    """Configuration for terminal emulation and interaction."""
    
    terminal_type: str = 'xterm-256color'
    width: int = 80
    height: int = 24
    encoding: str = 'utf-8'
    line_ending: str = '\n'  # or '\r\n' for Windows
    echo: bool = True  # Whether to echo commands in output
    ansi_colors: bool = True  # Whether to process ANSI color codes
    buffer_size: int = 1024 * 64  # 64KB buffer for reading output


@dataclass
class ExecutionConfig:
    """Configuration for command execution behavior."""
    
    default_timeout: float = 300.0  # 5 minutes for long-running commands
    check_return_code: bool = False  # Whether to raise on non-zero exit codes
    capture_stderr: bool = True
    environment_handling: str = 'merge'  # 'merge', 'replace', or 'inherit'
    shell: str = '/bin/bash'
    shell_prompt_pattern: str = r'[$#] '  # Regex pattern for detecting prompts
    sudo_password_prompt: str = r'\[sudo\] password'
    working_directory_tracking: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging behavior."""
    
    log_level: str = 'WARNING'
    log_commands: bool = True
    log_output: bool = False  # Can be verbose
    mask_passwords: bool = True
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    debug_ssh_transport: bool = False  # Enable paramiko/asyncssh debug logging


class TermittyConfig:
    """
    Main configuration class that combines all configuration sections.
    
    This class handles loading configuration from various sources and provides
    a unified interface for accessing configuration values throughout Termitty.
    """
    
    def __init__(self):
        """Initialize with default configurations."""
        self.connection = ConnectionConfig()
        self.terminal = TerminalConfig()
        self.execution = ExecutionConfig()
        self.logging = LoggingConfig()
        
        # Track which config file we loaded from (if any)
        self._config_file: Optional[Path] = None
        
        # Allow runtime overrides
        self._overrides: Dict[str, Dict[str, Any]] = {}
        
        # Load configurations in order of precedence
        self._load_default_config_file()
        self._load_environment_variables()
        self._apply_logging_config()
    
    def _load_default_config_file(self):
        """
        Load configuration from default file locations.
        
        Searches for config files in order:
        1. ./termitty.ini (current directory)
        2. ~/.termitty/config.ini (user home)
        3. /etc/termitty/config.ini (system-wide)
        """
        search_paths = [
            Path.cwd() / 'termitty.ini',
            Path.home() / '.termitty' / 'config.ini',
            Path('/etc/termitty/config.ini')
        ]
        
        for config_path in search_paths:
            if config_path.exists():
                try:
                    self.load_from_file(config_path)
                    logger.info(f"Loaded configuration from {config_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load config from {config_path}: {e}")
    
    def load_from_file(self, file_path: Path):
        """Load configuration from an INI file."""
        parser = configparser.ConfigParser()
        parser.read(file_path)
        
        self._config_file = file_path
        
        # Map INI sections to our configuration objects
        section_mapping = {
            'connection': self.connection,
            'terminal': self.terminal,
            'execution': self.execution,
            'logging': self.logging
        }
        
        for section_name, config_obj in section_mapping.items():
            if section_name in parser:
                for key, value in parser[section_name].items():
                    if hasattr(config_obj, key):
                        # Convert string values to appropriate types
                        current_value = getattr(config_obj, key)
                        converted_value = self._convert_config_value(value, type(current_value))
                        setattr(config_obj, key, converted_value)
                    else:
                        logger.warning(f"Unknown configuration key: {section_name}.{key}")
    
    def _convert_config_value(self, value: str, target_type: type) -> Any:
        """Convert string configuration values to appropriate Python types."""
        if target_type == bool:
            return value.lower() in ('true', 'yes', '1', 'on')
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == list:
            # Assume comma-separated values
            return [v.strip() for v in value.split(',') if v.strip()]
        else:
            return value
    
    def _load_environment_variables(self):
        """
        Load configuration from environment variables.
        
        Environment variables follow the pattern: TERMITTY_SECTION_KEY
        For example: TERMITTY_CONNECTION_DEFAULT_PORT=2222
        """
        prefix = 'TERMITTY_'
        
        for env_var, value in os.environ.items():
            if env_var.startswith(prefix):
                parts = env_var[len(prefix):].lower().split('_', 1)
                if len(parts) == 2:
                    section, key = parts
                    self._apply_override(section, key, value)
    
    def _apply_override(self, section: str, key: str, value: Any):
        """Apply a configuration override."""
        section_mapping = {
            'connection': self.connection,
            'terminal': self.terminal,
            'execution': self.execution,
            'logging': self.logging
        }
        
        if section in section_mapping:
            config_obj = section_mapping[section]
            if hasattr(config_obj, key):
                current_value = getattr(config_obj, key)
                converted_value = self._convert_config_value(str(value), type(current_value))
                setattr(config_obj, key, converted_value)
                
                # Track this override
                if section not in self._overrides:
                    self._overrides[section] = {}
                self._overrides[section][key] = converted_value
                
                logger.debug(f"Applied config override: {section}.{key} = {converted_value}")
    
    def _apply_logging_config(self):
        """Apply the logging configuration to Python's logging system."""
        log_level = getattr(logging, self.logging.log_level.upper(), logging.WARNING)
        
        # Configure Termitty's logger
        termitty_logger = logging.getLogger('termitty')
        termitty_logger.setLevel(log_level)
        
        # Configure SSH library logging if debug is enabled
        if self.logging.debug_ssh_transport:
            logging.getLogger('paramiko').setLevel(logging.DEBUG)
            logging.getLogger('asyncssh').setLevel(logging.DEBUG)
    
    def set(self, section: str, key: str, value: Any):
        """
        Set a configuration value at runtime.
        
        Args:
            section: Configuration section ('connection', 'terminal', etc.)
            key: Configuration key
            value: New value
        
        Example:
            config.set('connection', 'default_timeout', 60.0)
        """
        self._apply_override(section, key, value)
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all current configuration settings as a dictionary."""
        return {
            'connection': self.connection.__dict__,
            'terminal': self.terminal.__dict__,
            'execution': self.execution.__dict__,
            'logging': self.logging.__dict__,
            'config_file': str(self._config_file) if self._config_file else None,
            'overrides': self._overrides
        }


# Global configuration instance
# This allows all parts of Termitty to access the same configuration
config = TermittyConfig()