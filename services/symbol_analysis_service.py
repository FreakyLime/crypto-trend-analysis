from config.settings import BINANCE_TO_COINGECKO_SYMBOLS
from analysis.technical_indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_vwap,
    calculate_atr,
    calculate_obv,
    calculate_stochastic_oscillator,
    calculate_adx,
    calculate_order_book_imbalance,
    calculate_bid_ask_spread
)

def analyze_symbol(symbol, binance_utils, coingecko_data):
    try:
        historical_data = binance_utils.fetch_historical_data(symbol)
        if historical_data is None:
            return None

        historical_data["RSI"] = calculate_rsi(historical_data)
        macd, signal = calculate_macd(historical_data)
        upper_band, lower_band = calculate_bollinger_bands(historical_data)
        historical_data["VWAP"] = calculate_vwap(historical_data)
        historical_data["ATR"] = calculate_atr(historical_data)
        historical_data["OBV"] = calculate_obv(historical_data)
        historical_data["Stochastic"] = calculate_stochastic_oscillator(historical_data)
        historical_data["ADX"] = calculate_adx(historical_data)

        order_book = binance_utils.fetch_order_book(symbol)
        bid_ask_spread = calculate_bid_ask_spread(order_book)
        order_book_imbalance = calculate_order_book_imbalance(order_book)

        volume = binance_utils.fetch_volume(symbol)
        liquidity = binance_utils.fetch_liquidity(symbol)

        coingecko_symbol = BINANCE_TO_COINGECKO_SYMBOLS.get(symbol)
        coingecko_entry = coingecko_data.get(coingecko_symbol, {})

        return {
            "symbol": symbol,
            "price": historical_data["close"].iloc[-1],
            "rsi": historical_data["RSI"].iloc[-1],
            "macd": macd.iloc[-1],
            "signal": signal.iloc[-1],
            "bollinger_upper": upper_band.iloc[-1],
            "bollinger_lower": lower_band.iloc[-1],
            "vwap": historical_data["VWAP"].iloc[-1],
            "atr": historical_data["ATR"].iloc[-1],
            "obv": historical_data["OBV"].iloc[-1],
            "stochastic": historical_data["Stochastic"].iloc[-1],
            "adx": historical_data["ADX"].iloc[-1],
            "volume": volume,
            "liquidity": liquidity,
            "order_book_imbalance": order_book_imbalance,
            "bid_ask_spread": bid_ask_spread,
            "coingecko_price": coingecko_entry.get("usd", "N/A"),
            "coingecko_market_cap": coingecko_entry.get("usd_market_cap", "N/A"),
        }
    except Exception as e:
        raise RuntimeError(f"Error analyzing symbol {symbol}: {e}")
