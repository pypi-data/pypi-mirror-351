import inspect
import datetime
import os
import sys
import threading
from typing import Optional

class LogMaster:
    # Log level thresholds (higher = more severe)
    TRACEBACK = 5
    TRACE = 10
    DEBUG = 20
    VERBOSE = 25
    TIMING = 30
    AUDIT = 35
    INFO = 40
    NOTIFY = 45
    SUCCESS = 50
    WARNING = 60
    ALERT = 70
    ERROR = 80
    CRITICAL = 90
    FATAL = 100

    # ANSI color codes
    COLORS = {
        'SUCCESS': 92,   # Green
        'INFO': 96,      # Cyan
        'WARNING': 93,   # Yellow
        'ERROR': 91,     # Red
        'DEBUG': 94,     # Blue
        'CRITICAL': 91,  # Red
        'TRACE': 95,     # Magenta
        'FATAL': 91,     # Red
        'ALERT': 93,     # Yellow
        'NOTIFY': 92,    # Green
        'AUDIT': 90,     # Dark Gray
        'TIMING': 96,    # Cyan
        'VERBOSE': 92,   # Green
        'TRACEBACK': 91  # Red
    }

    def __init__(
        self,
        level: int = DEBUG,
        log_file: Optional[str] = None,
        use_color: bool = True,
        show_caller: bool = True
    ):
        """
        Initialize logger
        
        :param level: Minimum log level to display
        :param log_file: Path to log file (optional)
        :param use_color: Enable colored output
        :param show_caller: Show caller file/line info
        """
        self.level = level
        self.log_file = log_file
        self.use_color = use_color and sys.stdout.isatty()
        self.show_caller = show_caller
        self.lock = threading.Lock()

    def set_level(self, level: int):
        """Change log level dynamically"""
        self.level = level

    def _get_caller_info(self) -> tuple:
        """Get caller file and line number, skipping debugger frames."""
        try:
            frame = inspect.currentframe()
            # Traverse back through call stack frames (skip debugger frames)
            depth = 0
            while frame:
                frame = frame.f_back
                depth += 1
                # Check if we have reached the actual user code, not debugger frames
                if frame.f_code.co_filename != "<string>" and "pydevd" not in frame.f_code.co_filename:
                    filename = os.path.basename(frame.f_code.co_filename)
                    return filename, frame.f_lineno
                # Avoid too much recursion in case of an error in stack inspection
                if depth > 10:  
                    break
        except (AttributeError, TypeError):
            pass
        return ("unknown", 0)

    def _log(
        self,
        level: str,
        message: str,
        custom_color: Optional[int] = None
    ):
        """Core logging method with thread safety"""
        if self.level > self.__class__.__dict__[level]:
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caller_info = f"[{self._get_caller_info()[0]}:{self._get_caller_info()[1]}]" if self.show_caller else ""
        log_message = f"{timestamp} [{level}] {caller_info} {message}"

        # Choose color
        color_code = custom_color or self.COLORS.get(level, 97)  # Default to white
        
        with self.lock:
            # Console output
            if self.use_color:
                print(f"\033[1;{color_code}m{log_message}\033[0m")
            else:
                print(log_message)
                
            # File output (no color)
            if self.log_file:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_message + "\n")

    # Convenience methods
    def success(self, message): self._log("SUCCESS", message)
    def info(self, message): self._log("INFO", message)
    def warning(self, message): self._log("WARNING", message)
    def error(self, message): self._log("ERROR", message)
    def debug(self, message): self._log("DEBUG", message)
    def critical(self, message): self._log("CRITICAL", message)
    def trace(self, message): self._log("TRACE", message)
    def fatal(self, message): self._log("FATAL", message)
    def alert(self, message): self._log("ALERT", message)
    def notify(self, message): self._log("NOTIFY", message)
    def audit(self, message): self._log("AUDIT", message)
    def timing(self, message): self._log("TIMING", message)
    def verbose(self, message): self._log("VERBOSE", message)
    def traceback(self, message): self._log("TRACEBACK", message)
    
    def custom(self, 
        level: str, 
        message: str, 
        color: int, 
        level_value: int = INFO
    ):
        """Create custom log entry"""
        if not hasattr(self, level):
            setattr(self, level, level_value)
            self.COLORS[level] = color
        self._log(level, message, color)
