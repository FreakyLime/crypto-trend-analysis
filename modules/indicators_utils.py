import numpy as np
import pandas as pd

def calculate_rsi(data, period=14):
    """Calculate the Relative Strength Index (RSI)."""
    delta = data["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    """Calculate the MACD and Signal Line."""
    short_ema = data["close"].ewm(span=short_period, adjust=False).mean()
    long_ema = data["close"].ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal

def calculate_bollinger_bands(data, window=20):
    """Calculate Bollinger Bands."""
    sma = data["close"].rolling(window=window).mean()
    std = data["close"].rolling(window=window).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    return upper_band, lower_band
