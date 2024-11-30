import logging
import sys
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Credentials
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configuration Settings
HISTORICAL_DATA_LIMIT = int(os.getenv("HISTORICAL_DATA_LIMIT", 50))
CANDLESTICK_INTERVAL = os.getenv("CANDLESTICK_INTERVAL", "15m")
SYMBOLS_TO_MONITOR = os.getenv("SYMBOLS_TO_MONITOR", "").split(",")

# Symbol Mapping
BINANCE_TO_COINGECKO_SYMBOLS = {
    "BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "BNBUSDT": "binancecoin",
    "XRPUSDT": "ripple", "ADAUSDT": "cardano", "SOLUSDT": "solana",
    "DOTUSDT": "polkadot", "DOGEUSDT": "dogecoin", "MATICUSDT": "polygon",
    "LTCUSDT": "litecoin", "XLMUSDT": "stellar"
}
class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

class ColorFormatter(logging.Formatter):
    """Custom colored formatter for console output."""
    COLORS = {
        "DEBUG": "\033[94m",    # Blue
        "INFO": "\033[92m",     # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "CRITICAL": "\033[95m"  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(log_file="sent_data.log"):
    """
    Set up the main application logger.
    
    Args:
        log_file (str): The name of the log file to store persistent logs.

    Returns:
        logger (logging.Logger): Configured logger instance.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Console handler for immediate feedback
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # File handler for persistent logs
    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = JsonFormatter()
    file_handler.setFormatter(file_formatter)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
