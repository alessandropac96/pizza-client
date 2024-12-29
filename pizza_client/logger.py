from datetime import datetime 
from enum import Enum

class LogLevels(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class Logger:
    def __init__(self, log_level : LogLevels):
        self.log_level = log_level

    def _log(self, messages, log_level : LogLevels):
        if log_level.value >= self.log_level.value:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] [{log_level.name}]"
            print(formatted_message, *messages)
        return
    
    def info(self, *messages):
        self._log(messages, LogLevels.INFO)
        return
    
    def debug(self, *messages):
        self._log(messages, LogLevels.DEBUG)
        return
    
    def warning(self, *messages):
        self._log(messages, LogLevels.WARNING)
        return
    
    def error(self, *messages):
        self._log(messages, LogLevels.ERROR)
        return
    
