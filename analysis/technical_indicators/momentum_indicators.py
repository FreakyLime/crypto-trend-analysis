import pandas as pd
import numpy as np
import logging

logger = logging.getLogger()

def calculate_rsi(data, period=14):
    try:
        delta = data["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
        avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return None

def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    try:
        short_ema = data["close"].ewm(span=short_period, adjust=False).mean()
        long_ema = data["close"].ewm(span=long_period, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        return macd, signal
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        return None, None
    
def calculate_stochastic_oscillator(data, period=14):
    try:
        lowest_low = data["low"].rolling(window=period).min()
        highest_high = data["high"].rolling(window=period).max()
        return (data["close"] - lowest_low) / (highest_high - lowest_low) * 100
    except Exception as e:
        logger.error(f"Error calculating Stochastic Oscillator: {e}")
        return None

