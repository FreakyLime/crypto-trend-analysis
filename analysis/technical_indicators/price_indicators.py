import pandas as pd
import numpy as np
from config.logger import setup_logging

logger = setup_logging()

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
