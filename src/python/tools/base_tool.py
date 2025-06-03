import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os

class BaseTool(ABC):
    """Base class for all processing tools"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info_messages: List[str] = []
        
    @abstractmethod
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input files with given options
        
        Args:
            files: List of file paths to process
            options: Dictionary of processing options
            
        Returns:
            Dictionary with processing results
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, files: List[str], options: Dict[str, Any]) -> bool:
        """
        Validate input files and options
        
        Args:
            files: List of file paths to validate
            options: Dictionary of options to validate
            
        Returns:
            True if inputs are valid, False otherwise
        """
        pass
    
    def add_error(self, message: str):
        """Add error message"""
        self.errors.append(message)
        self.logger.error(message)
        
    def add_warning(self, message: str):
        """Add warning message"""
        self.warnings.append(message)
        self.logger.warning(message)
        
    def add_info(self, message: str):
        """Add info message"""
        self.info_messages.append(message)
        self.logger.info(message)
        
    def clear_messages(self):
        """Clear all messages"""
        self.errors.clear()
        self.warnings.clear()
        self.info_messages.clear()
        
    def clear_file_messages(self):
        """Clear messages for current file processing"""
        # Clear all messages for fresh file processing
        self.errors.clear()
        self.warnings.clear()
        self.info_messages.clear()
        
    def get_result(self, success: bool, data: Any = None) -> Dict[str, Any]:
        """
        Get standardized result dictionary
        
        Args:
            success: Whether the operation was successful
            data: Optional data to include in result
            
        Returns:
            Standardized result dictionary
        """
        result = {
            "success": success,
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
            "info": self.info_messages.copy()
        }
        
        if data is not None:
            result["data"] = data
            
        return result
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        exists = os.path.isfile(filepath)
        self.logger.info(f"[BASE] Checking file exists: {filepath} -> {exists}")
        if not exists:
            # Additional debug info
            self.logger.info(f"[BASE] Current directory: {os.getcwd()}")
            self.logger.info(f"[BASE] Path is absolute: {os.path.isabs(filepath)}")
            if os.path.exists(filepath):
                self.logger.info(f"[BASE] Path exists but is not a file (maybe directory?)")
                self.logger.info(f"[BASE] Is directory: {os.path.isdir(filepath)}")
            else:
                self.logger.info(f"[BASE] Path does not exist at all")
                # Try to list parent directory
                parent_dir = os.path.dirname(filepath)
                if os.path.exists(parent_dir):
                    self.logger.info(f"[BASE] Parent directory exists: {parent_dir}")
                    try:
                        files = os.listdir(parent_dir)
                        self.logger.info(f"[BASE] Files in parent directory: {files[:5]}...") # First 5 files
                    except Exception as e:
                        self.logger.error(f"[BASE] Cannot list parent directory: {e}")
                else:
                    self.logger.info(f"[BASE] Parent directory does not exist: {parent_dir}")
        return exists
    
    def create_output_path(self, base_path: str, suffix: str = "") -> str:
        """Create output file path"""
        base_dir = os.path.dirname(base_path)
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        
        if suffix:
            output_name = f"{base_name}_{suffix}.xlsx"
        else:
            output_name = f"{base_name}_output.xlsx"
            
        return os.path.join(base_dir, output_name)