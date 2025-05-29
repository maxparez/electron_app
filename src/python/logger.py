import logging
import os
from datetime import datetime
from pathlib import Path
import sys

class AppLogger:
    """Centralized logging for the application"""
    
    def __init__(self, name, log_dir=None):
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Determine log directory
        if log_dir is None:
            # In production, use app data directory
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                if sys.platform == 'win32':
                    app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
                    log_dir = Path(app_data) / 'NastrojeOPJAK' / 'logs'
                else:
                    log_dir = Path.home() / '.nastroje-opjak' / 'logs'
            else:
                # Development mode
                log_dir = Path(__file__).parent.parent.parent / 'logs'
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler for all logs
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Error file handler
        error_file = self.log_dir / f"{name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
        
        # Log startup
        self.logger.info(f"Logger initialized for {name}")
        self.logger.info(f"Log directory: {self.log_dir}")
    
    def get_logger(self):
        return self.logger
    
    def clean_old_logs(self, days=7):
        """Remove log files older than specified days"""
        import time
        
        current_time = time.time()
        
        for log_file in self.log_dir.glob('*.log'):
            file_age = current_time - log_file.stat().st_mtime
            if file_age > (days * 24 * 60 * 60):
                try:
                    log_file.unlink()
                    self.logger.info(f"Removed old log file: {log_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to remove old log: {e}")
    
    @staticmethod
    def get_crash_handler():
        """Returns a function to log unhandled exceptions"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            logger = logging.getLogger('crash')
            logger.error(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
        
        return handle_exception

# Global logger instances
server_logger = None
tool_logger = None

def init_logging():
    """Initialize all loggers"""
    global server_logger, tool_logger
    
    server_logger = AppLogger('server').get_logger()
    tool_logger = AppLogger('tools').get_logger()
    
    # Set crash handler
    sys.excepthook = AppLogger.get_crash_handler()
    
    # Clean old logs
    AppLogger('server').clean_old_logs()
    
    return server_logger, tool_logger