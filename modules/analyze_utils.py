from modules.config import BINANCE_TO_COINGECKO_SYMBOLS
from modules.coingecko_utils import fetch_all_coin_data
from modules.indicators_utils import calculate_rsi, calculate_macd, calculate_bollinger_bands
from modules.binance_utils import BinanceUtils

def analyze_symbol(symbol, binance_utils, coingecko_data):
    """
    Analyze data for a single symbol using pre-fetched CoinGecko data.
    """
    try:
        # Fetch historical data
        historical_data = binance_utils.fetch_historical_data(symbol)
        if historical_data is None:
            return None

        # Calculate technical indicators
        historical_data["RSI"] = calculate_rsi(historical_data)
        macd, signal = calculate_macd(historical_data)
        upper_band, lower_band = calculate_bollinger_bands(historical_data)

        # Fetch additional metrics
        volume = binance_utils.fetch_volume(symbol)
        liquidity = binance_utils.fetch_liquidity(symbol)
        order_book = binance_utils.fetch_order_book(symbol)

        # Get CoinGecko data for the symbol
        coingecko_symbol = BINANCE_TO_COINGECKO_SYMBOLS.get(symbol, None)
        coingecko_entry = coingecko_data.get(coingecko_symbol, {})

        # Prepare the result
        return {
            "symbol": symbol,
            "price": historical_data["close"].iloc[-1],
            "rsi": historical_data["RSI"].iloc[-1],
            "macd": macd.iloc[-1],
            "signal": signal.iloc[-1],
            "bollinger_upper": upper_band.iloc[-1],
            "bollinger_lower": lower_band.iloc[-1],
            "volume": volume,
            "liquidity": liquidity,
            "order_book": order_book,
            "coingecko_price": coingecko_entry.get("usd", "N/A"),
            "coingecko_market_cap": coingecko_entry.get("usd_market_cap", "N/A"),
        }
    except Exception as e:
        raise RuntimeError(f"Error analyzing symbol {symbol}: {e}")


