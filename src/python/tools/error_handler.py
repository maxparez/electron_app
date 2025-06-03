"""
Centralized error handling for tools
"""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import traceback
import logging


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ToolError(Exception):
    """Custom exception for tool errors"""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.severity = severity
        self.details = details or {}
        

class ErrorHandler:
    """Centralized error handler for tools"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info_messages: List[Dict[str, Any]] = []
        
    def add_message(self, message: str, severity: ErrorSeverity, 
                   details: Optional[Dict[str, Any]] = None):
        """Add a message with severity"""
        msg_dict = {
            'message': message,
            'severity': severity.value,
            'details': details or {}
        }
        
        if severity == ErrorSeverity.ERROR or severity == ErrorSeverity.CRITICAL:
            self.errors.append(msg_dict)
            self.logger.error(message)
        elif severity == ErrorSeverity.WARNING:
            self.warnings.append(msg_dict)
            self.logger.warning(message)
        else:
            self.info_messages.append(msg_dict)
            self.logger.info(message)
            
    def add_error(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Add an error message"""
        self.add_message(message, ErrorSeverity.ERROR, details)
        
    def add_warning(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a warning message"""
        self.add_message(message, ErrorSeverity.WARNING, details)
        
    def add_info(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Add an info message"""
        self.add_message(message, ErrorSeverity.INFO, details)
        
    def clear_messages(self):
        """Clear all messages"""
        self.errors.clear()
        self.warnings.clear()
        self.info_messages.clear()
        
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
        
    def get_error_messages(self) -> List[str]:
        """Get list of error messages"""
        return [e['message'] for e in self.errors]
        
    def get_warning_messages(self) -> List[str]:
        """Get list of warning messages"""
        return [w['message'] for w in self.warnings]
        
    def get_info_messages(self) -> List[str]:
        """Get list of info messages"""
        return [i['message'] for i in self.info_messages]
        
    def get_all_messages(self) -> Dict[str, List[str]]:
        """Get all messages categorized by severity"""
        return {
            'errors': self.get_error_messages(),
            'warnings': self.get_warning_messages(),
            'info': self.get_info_messages()
        }
        
    def handle_exception(self, e: Exception, context: str = "") -> None:
        """Handle an exception and add appropriate error message"""
        if isinstance(e, ToolError):
            self.add_message(str(e), e.severity, e.details)
        else:
            # Get traceback
            tb = traceback.format_exc()
            
            # Create error message
            error_msg = f"Unexpected error in {context}: {type(e).__name__}: {str(e)}"
            
            # Add error with details
            self.add_error(error_msg, {
                'exception_type': type(e).__name__,
                'exception_str': str(e),
                'traceback': tb,
                'context': context
            })
            

def safe_execute(handler: ErrorHandler, func: Callable, *args, 
                context: str = "", default=None, **kwargs):
    """
    Safely execute a function with error handling
    
    Args:
        handler: ErrorHandler instance
        func: Function to execute
        args: Function arguments
        context: Context for error messages
        default: Default return value on error
        kwargs: Function keyword arguments
        
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handler.handle_exception(e, context or func.__name__)
        return default