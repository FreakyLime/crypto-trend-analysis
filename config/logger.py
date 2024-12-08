import logging
import os
import sys
from json import dumps
from dotenv import load_dotenv

load_dotenv()

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return dumps(log_record)

class ColorFormatter(logging.Formatter):
    def format(self, record):
        level_colors = {
            "DEBUG": "\033[94m",     # Blue
            "INFO": "\033[92m",      # Green (log level only)
            "WARNING": "\033[93m",   # Yellow (entire text)
            "ERROR": "\033[91m",     # Red (entire text)
            "CRITICAL": "\033[95m",  # Magenta (entire text)
        }
        reset_color = "\033[0m"

        if record.levelno > logging.INFO:  # Entire log message colored for WARNING and above
            log_message = f"{level_colors.get(record.levelname, '')}{super().format(record)}{reset_color}"
        else:  # Only log level colored for DEBUG and INFO
            levelname = f"{level_colors.get(record.levelname, '')}{record.levelname}{reset_color}"
            record.levelname = levelname
            log_message = super().format(record)

        return log_message


def setup_logging():
    environment = os.getenv("ENVIRONMENT", "development").lower()
    log_dir = os.getenv("DEV_LOG_DIR") if environment == "development" else os.getenv("PROD_LOG_DIR")
    log_file_name = os.getenv("LOG_FILE_NAME", "application.log")
    log_file_path = os.path.join(log_dir, log_file_name)

    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(log_file_path, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = JsonFormatter()
    file_handler.setFormatter(file_formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
