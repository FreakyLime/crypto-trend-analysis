import pandas as pd
import numpy as np
from config.config import setup_logging

logger = setup_logging()

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

def calculate_bollinger_bands(data, window=20):
    try:
        sma = data["close"].rolling(window=window).mean()
        std = data["close"].rolling(window=window).std()
        return sma + (2 * std), sma - (2 * std)
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        return None, None

def calculate_vwap(data):
    try:
        return (data["volume"] * data["close"]).cumsum() / data["volume"].cumsum()
    except Exception as e:
        logger.error(f"Error calculating VWAP: {e}")
        return None

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

def calculate_obv(data):
    try:
        obv = [0]
        for i in range(1, len(data["close"])):
            if data["close"][i] > data["close"][i - 1]:
                obv.append(obv[-1] + data["volume"][i])
            elif data["close"][i] < data["close"][i - 1]:
                obv.append(obv[-1] - data["volume"][i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=data.index)
    except Exception as e:
        logger.error(f"Error calculating OBV: {e}")
        return None

def calculate_bid_ask_spread(order_book):
    try:
        if not order_book["bids"] or not order_book["asks"]:
            return None
        highest_bid = float(order_book["bids"][0][0])
        lowest_ask = float(order_book["asks"][0][0])
        return lowest_ask - highest_bid
    except (IndexError, ValueError, TypeError) as e:
        logger.error(f"Error calculating bid-ask spread: {e}")
        return None

def calculate_order_book_imbalance(order_book):
    try:
        total_bid_volume = sum(float(bid[1]) for bid in order_book["bids"])
        total_ask_volume = sum(float(ask[1]) for ask in order_book["asks"])
        return total_bid_volume / (total_bid_volume + total_ask_volume)
    except (IndexError, ValueError, TypeError, ZeroDivisionError) as e:
        logger.error(f"Error calculating order book imbalance: {e}")
        return None

def calculate_momentum(data, period=10):
    try:
        return data["close"] - data["close"].shift(period)
    except Exception as e:
        logger.error(f"Error calculating momentum: {e}")
        return None

def calculate_stochastic_oscillator(data, period=14):
    try:
        lowest_low = data["low"].rolling(window=period).min()
        highest_high = data["high"].rolling(window=period).max()
        return (data["close"] - lowest_low) / (highest_high - lowest_low) * 100
    except Exception as e:
        logger.error(f"Error calculating Stochastic Oscillator: {e}")
        return None

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

def calculate_support_resistance(data, window=20):
    try:
        return data["low"].rolling(window=window).min(), data["high"].rolling(window=window).max()
    except Exception as e:
        logger.error(f"Error calculating support and resistance: {e}")
        return None, None
