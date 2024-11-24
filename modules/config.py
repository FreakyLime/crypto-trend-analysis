from dotenv import load_dotenv
import os
import logging
import sys

# Load environment variables from .env
load_dotenv()

# Binance API credentials
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Configuration for historical data and candlestick intervals
HISTORICAL_DATA_LIMIT = int(os.getenv("HISTORICAL_DATA_LIMIT", 50))  # Default to 50 if not set
CANDLESTICK_INTERVAL = os.getenv("CANDLESTICK_INTERVAL", "15m")  # Default to "15m" if not set

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Symbol mapping
BINANCE_TO_COINGECKO_SYMBOLS = {
    'BTCUSDT': 'bitcoin', 'ETHUSDT': 'ethereum', 'BNBUSDT': 'binancecoin',
    'XRPUSDT': 'ripple', 'ADAUSDT': 'cardano', 'SOLUSDT': 'solana',
    'DOTUSDT': 'polkadot', 'DOGEUSDT': 'dogecoin', 'MATICUSDT': 'polygon',
    'LTCUSDT': 'litecoin', 'XLMUSDT': 'stellar'
}

# List of symbols to monitor (parsed from .env)
SYMBOLS_TO_MONITOR = os.getenv("SYMBOLS_TO_MONITOR", "").split(",")  # Default to empty list if not set

# Logging configuration
class CustomFormatter(logging.Formatter):
    """Custom formatter for color-coded logs in the console."""
    COLORS = {
        "DEBUG": "\033[94m",   # Blue
        "INFO": "\033[92m",    # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "CRITICAL": "\033[95m" # Magenta
    }
    RESET = "\033[0m"  # Reset color

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        formatted_message = super().format(record)
        return f"\n{formatted_message}\n"  # Add spacing between logs for readability

def setup_logging(log_file='sent_data.log'):
    """Setup logging with color-coded console logs and file logging."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Log all levels to the file

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Log INFO and above to the console
    console_formatter = CustomFormatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # File Handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)  # Log all levels to the file
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Add Handlers to Logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
