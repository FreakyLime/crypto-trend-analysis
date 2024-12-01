import pandas as pd
import numpy as np
from config.logger import setup_logging

logger = setup_logging()

def calculate_bollinger_bands(data, window=20):
    try:
        sma = data["close"].rolling(window=window).mean()
        std = data["close"].rolling(window=window).std()
        return sma + (2 * std), sma - (2 * std)
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        return None, None

def calculate_atr(data, period=14):
    try:
        high_low = data["high"] - data["low"]
        high_close = np.abs(data["high"] - data["close"].shift())
        low_close = np.abs(data["low"] - data["close"].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    except Exception as e:
        logger.error(f"Error calculating ATR: {e}")
        return None
