import os
from json import load
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = os.path.dirname(__file__)
SYMBOLS_FILE_PATH = os.path.join(CONFIG_DIR, "symbols.json")

with open(SYMBOLS_FILE_PATH, "r") as file:
    symbols_config = load(file)

SYMBOLS_TO_MONITOR = symbols_config.get("symbols_to_monitor", [])
BINANCE_TO_COINGECKO_SYMBOLS = symbols_config.get("binance_to_coingecko_symbols", {})

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CANDLESTICK_INTERVAL = os.getenv("CANDLESTICK_INTERVAL", "15m")
TELEGRAM_MESSAGE_DELAY = float(os.getenv("TELEGRAM_MESSAGE_DELAY", 1.0))
