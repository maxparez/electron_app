"""
Logger utilities for consistent logging across tools
"""

import logging
from typing import Optional, Any
from functools import wraps
import time


class ToolLogger:
    """Enhanced logger for tools with consistent formatting"""
    
    def __init__(self, logger: Optional[logging.Logger], prefix: str = ""):
        self.logger = logger or logging.getLogger(__name__)
        self.prefix = prefix
        
    def _format_message(self, message: str) -> str:
        """Format message with prefix"""
        if self.prefix:
            return f"[{self.prefix}] {message}"
        return message
        
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(message), *args, **kwargs)
        
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message), *args, **kwargs)
        
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message), *args, **kwargs)
        
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(message), *args, **kwargs)
        
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(self._format_message(message), *args, **kwargs)
        
    def log_section(self, section_name: str):
        """Log section separator"""
        separator = "=" * 30
        self.info(f"{separator} {section_name} {separator}")
        
    def log_dict(self, name: str, data: dict, level=logging.INFO):
        """Log dictionary contents"""
        self.logger.log(level, self._format_message(f"{name}:"))
        for key, value in data.items():
            self.logger.log(level, self._format_message(f"  {key}: {value}"))
            
    def log_list(self, name: str, data: list, level=logging.INFO):
        """Log list contents"""
        self.logger.log(level, self._format_message(f"{name}: {data}"))


def log_execution_time(prefix: str = ""):
    """Decorator to log method execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            
            # Get logger
            logger = getattr(self, 'logger', logging.getLogger(__name__))
            if hasattr(logger, '_format_message'):
                log_func = logger.info
            else:
                log_func = lambda msg: logger.info(f"[{prefix}] {msg}" if prefix else msg)
                
            log_func(f"Starting {func.__name__}")
            
            try:
                result = func(self, *args, **kwargs)
                elapsed = time.time() - start_time
                log_func(f"Completed {func.__name__} in {elapsed:.2f}s")
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                log_func(f"Failed {func.__name__} after {elapsed:.2f}s: {str(e)}")
                raise
                
        return wrapper
    return decorator


def log_errors(prefix: str = "", reraise: bool = True):
    """Decorator to log exceptions"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Get logger
                logger = getattr(self, 'logger', logging.getLogger(__name__))
                if hasattr(logger, '_format_message'):
                    log_func = logger.error
                else:
                    log_func = lambda msg: logger.error(f"[{prefix}] {msg}" if prefix else msg)
                    
                log_func(f"Error in {func.__name__}: {type(e).__name__}: {str(e)}")
                
                if reraise:
                    raise
                return None
                
        return wrapper
    return decorator