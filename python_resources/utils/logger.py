import os
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Logger:
    def __init__(self, log_dir: str = ".log"):
        self.log_dir = log_dir
        today = datetime.now().strftime("%Y-%m-%d")
        self.current_log_file = os.path.join(self.log_dir, f"ck3-workshop-{today}.log")

    def init(self) -> None:
        """Initialize the logger by creating the log directory"""
        os.makedirs(self.log_dir, exist_ok=True)

    def format_message(self, level: LogLevel, message: str) -> str:
        """Format a log message with timestamp and level"""
        timestamp = datetime.now().isoformat()
        return f"[{timestamp}] {level.value}: {message}"

    def log(self, level: LogLevel, message: str) -> None:
        """Log a message to console and file"""
        formatted_message = self.format_message(level, message)
        print(formatted_message)
        
        try:
            with open(self.current_log_file, mode='a') as f:
                f.write(formatted_message + '\n')
        except Exception as error:
            print(f"Failed to write to log file: {error}")

    def debug(self, message: str) -> None:
        """Log a debug message"""
        self.log(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        """Log an info message"""
        self.log(LogLevel.INFO, message)

    def warn(self, message: str) -> None:
        """Log a warning message"""
        self.log(LogLevel.WARN, message)

    def error(self, message: str, error: Exception = None) -> None:
        """Log an error message with optional stack trace"""
        if error:
            error_message = f"{message}\nStack trace:\n{error.__class__.__name__}: {error}"
            if hasattr(error, "__traceback__"):
                import traceback
                tb_str = "".join(traceback.format_exception(
                    type(error), error, error.__traceback__))
                error_message = f"{message}\nStack trace:\n{tb_str}"
        else:
            error_message = message
            
        self.log(LogLevel.ERROR, error_message)

    def cleanup(self, retain_days: int = 7) -> None:
        """Delete log files older than the specified number of days"""
        try:
            now = datetime.now()
            for file_name in os.listdir(self.log_dir):
                file_path = os.path.join(self.log_dir, file_name)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                diff_days = (now - mtime).days
                
                if diff_days > retain_days:
                    os.unlink(file_path)
                    
        except Exception as error:
            print(f"Failed to cleanup log files: {error}")


# Create the singleton instance
logger = Logger()
