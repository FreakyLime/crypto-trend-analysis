import pandas as pd
import numpy as np
from config.logger import setup_logging

logger = setup_logging()

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

def calculate_order_book_imbalance(order_book):
    try:
        total_bid_volume = sum(float(bid[1]) for bid in order_book["bids"])
        total_ask_volume = sum(float(ask[1]) for ask in order_book["asks"])
        return total_bid_volume / (total_bid_volume + total_ask_volume)
    except (IndexError, ValueError, TypeError, ZeroDivisionError) as e:
        logger.error(f"Error calculating order book imbalance: {e}")
        return None
    
def calculate_vwap(data):
    try:
        return (data["volume"] * data["close"]).cumsum() / data["volume"].cumsum()
    except Exception as e:
        logger.error(f"Error calculating VWAP: {e}")
        return None
