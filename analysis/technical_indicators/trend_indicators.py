import pandas as pd
import numpy as np
import logging

logger = logging.getLogger()

def calculate_adx(data, period=14):
    try:
        high_low = data["high"] - data["low"]
        high_close = np.abs(data["high"] - data["close"].shift())
        low_close = np.abs(data["low"] - data["close"].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        plus_dm = (data["high"] - data["high"].shift()).clip(lower=0)
        minus_dm = (data["low"].shift() - data["low"]).clip(lower=0)
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        return dx.rolling(window=period).mean()
    except Exception as e:
        logger.error(f"Error calculating ADX: {e}")
        return None
