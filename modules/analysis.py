from modules.config import setup_logging
from modules.analyze_utils import analyze_symbol
from modules.openai_utils import OpenAIUtils

# Main application logger
logger = setup_logging()

def analyze_symbols(symbols, binance_utils, coingecko_data):
    """
    Analyze symbols to extract actionable insights from Binance and CoinGecko data.

    Args:
        symbols (list): List of cryptocurrency symbols to analyze.
        binance_utils (object): Binance utilities instance for fetching data.
        coingecko_data (dict): Pre-fetched CoinGecko data for the symbols.

    Returns:
        list: A list of dictionaries containing significant symbols and their analysis.
    """
    logger.info("Starting symbol analysis...")
    significant_symbols = []

    for symbol in symbols:
        try:
            logger.info(f"Analyzing symbol: {symbol}")
            # Analyze symbol using a helper function
            data = analyze_symbol(symbol, binance_utils, coingecko_data)
            if data:
                logger.info(f"Symbol {symbol} analysis complete: {data}")
                significant_symbols.append(data)
            else:
                logger.info(f"No significant data found for symbol: {symbol}")
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}", exc_info=True)

    logger.info(f"Completed symbol analysis. {len(significant_symbols)} significant symbols found.")
    return significant_symbols


def prepare_gpt_input(global_metrics, bitcoin_sentiment, significant_symbols):
    """
    Prepare the input text for OpenAI GPT analysis and log it using the main logger.

    Args:
        global_metrics (dict): Global cryptocurrency metrics (e.g., Fear & Greed Index).
        bitcoin_sentiment (str): Sentiment analysis for Bitcoin.
        significant_symbols (list): List of analyzed symbols with their details.

    Returns:
        str: Formatted input text for GPT analysis.
    """
    logger.info("Preparing input for GPT...")
    input_text = (
        f"Global Market Metrics:\n"
        f"Fear & Greed Index: {global_metrics.get('fear_greed', 'N/A')}\n"
        f"BTC Dominance: {global_metrics.get('btc_dominance', 'N/A')}%\n"
        f"Bitcoin Sentiment: {bitcoin_sentiment}\n\n"
        "Please analyze each of the following cryptocurrencies individually and provide actionable insights "
        "(Buy, Sell, Hold, Long, Short) for each one:\n"
    )

    # Append symbol-specific data
    for data in significant_symbols:
        input_text += (
            f"{data['symbol']} | Price: {data['price']} | RSI: {data['rsi']} | MACD: {data['macd']} | "
            f"Signal: {data['signal']} | Bollinger Bands: Upper: {data['bollinger_upper']}, Lower: {data['bollinger_lower']} | "
            f"Volume: {data['volume']} | Liquidity: {data['liquidity']}\n"
        )

    # Log GPT input in the main logger
    logger.info("Logging GPT Input:")
    logger.info(input_text)

    logger.info("GPT input preparation complete.")
    return input_text

def analyze_with_openai(api_key, input_text):
    """
    Send the prepared input text to OpenAI GPT for analysis and log the response.

    Args:
        api_key (str): OpenAI API key.
        input_text (str): Input text to analyze.

    Returns:
        tuple: Suggestion and reasoning returned from GPT analysis.
    """
    logger.info("Sending data to OpenAI for analysis...")
    openai_utils = OpenAIUtils(api_key)

    try:
        # Send input to GPT and receive response
        suggestion, reasoning = openai_utils.analyze_data(input_text)

        # Log GPT input and response in `sent_data.log`
        logger.info("--- GPT Input ---")
        logger.info(input_text)
        logger.info("--- GPT Response ---")
        logger.info(reasoning)

        logger.info("Received analysis from OpenAI and logged response.")
        return suggestion, reasoning
    except Exception as e:
        logger.error("Error during OpenAI analysis.", exc_info=True)
        raise
