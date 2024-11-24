import asyncio
import json
from modules.config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    OPENAI_API_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    BINANCE_TO_COINGECKO_SYMBOLS,
    SYMBOLS_TO_MONITOR,
    setup_logging,
)
from modules.binance_utils import BinanceUtils
from modules.fear_and_greed_utils import fetch_fear_and_greed
from modules.senticrypt_utils import fetch_sentiment_from_senticrypt
from modules.telegram_utils import TelegramUtils
from modules.openai_utils import OpenAIUtils
from modules.analyze_utils import analyze_symbol
from modules.coingecko_utils import fetch_all_coin_data, fetch_bitcoin_dominance

# Configure logging
logger = setup_logging()

async def analyze_top_cryptos():
    logger.info("Starting cryptocurrency analysis...")
    binance_utils = BinanceUtils(BINANCE_API_KEY, BINANCE_API_SECRET)
    telegram_utils = TelegramUtils(TELEGRAM_BOT_TOKEN)
    openai_utils = OpenAIUtils(OPENAI_API_KEY)

    try:
        # Fetch Fear & Greed index and BTC Dominance
        fear_greed = fetch_fear_and_greed()
        btc_dominance = fetch_bitcoin_dominance()
        logger.info(f"Fear & Greed Index: {fear_greed}")
        logger.info(f"Bitcoin Dominance: {btc_dominance}%")
    except Exception as e:
        logger.error(f"Error fetching global market metrics: {e}")
        return

    # Fetch Bitcoin-specific sentiment for the current date
    bitcoin_sentiment = "No sentiment data available for Bitcoin."
    if "BTCUSDT" in SYMBOLS_TO_MONITOR:
        try:
            bitcoin_sentiment_data = fetch_sentiment_from_senticrypt()
            if bitcoin_sentiment_data:
                bitcoin_sentiment = (
                    f"Mean: {bitcoin_sentiment_data['mean']}, Sum: {bitcoin_sentiment_data['sum']}, "
                    f"Count: {bitcoin_sentiment_data['count']}, Date: {bitcoin_sentiment_data['date']}"
                )
        except Exception as e:
            logger.error(f"Error fetching Bitcoin sentiment: {e}")

    # Fetch CoinGecko data in batches
    crypto_ids = [BINANCE_TO_COINGECKO_SYMBOLS[symbol] for symbol in SYMBOLS_TO_MONITOR if symbol in BINANCE_TO_COINGECKO_SYMBOLS]
    coingecko_data = fetch_all_coin_data(crypto_ids)

    # Analyze each symbol
    significant_symbols = []
    for symbol in SYMBOLS_TO_MONITOR:
        try:
            symbol_data = analyze_symbol(symbol, binance_utils, coingecko_data)
            if symbol_data:
                significant_symbols.append(symbol_data)
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")

    if not significant_symbols:
        logger.warning("No significant symbols to process.")
        return

    # Prepare data for OpenAI
    data_for_gpt = {
        "fear_greed": fear_greed,
        "btc_dominance": btc_dominance,
        "bitcoin_sentiment": bitcoin_sentiment,
        "significant_symbols": significant_symbols,
    }

    # Save the data to the log file before sending it to GPT
    logger.info("Data sent to GPT:\n" + json.dumps(data_for_gpt, indent=2))

    # Format input text for GPT
    input_text = (
        f"Global Market Metrics:\n"
        f"Fear & Greed Index: {fear_greed}\n"
        f"BTC Dominance: {btc_dominance}%\n"
        f"Bitcoin Sentiment: {bitcoin_sentiment}\n\n"
        "Analyze the following cryptocurrency data and provide actionable insights (Buy, Sell, Hold, Long, Short):\n\n"
    )
    for symbol_data in significant_symbols:
        input_text += (
            f"{symbol_data['symbol']} | Price: {symbol_data['price']} | RSI: {symbol_data['rsi']} | "
            f"MACD: {symbol_data['macd']} | Signal: {symbol_data['signal']} | "
            f"Bollinger Bands: Upper: {symbol_data['bollinger_upper']}, Lower: {symbol_data['bollinger_lower']} | "
            f"Volume: {symbol_data['volume']} | Liquidity: {symbol_data['liquidity']}\n"
        )

    try:
        # Get analysis from OpenAI
        suggestion, reasoning = openai_utils.analyze_data(input_text)

        if not suggestion or not reasoning:
            logger.error("OpenAI API did not return valid suggestions or reasoning. Aborting Telegram message.")
            return

        logger.info(f"OpenAI Analysis:\n{reasoning}")

        # Send the analysis to Telegram
        await telegram_utils.send_message(
            TELEGRAM_CHAT_ID,
            f"*Analysis and Suggestions:*\n\n{reasoning}",
            parse_mode="Markdown"
        )
        logger.info("Message sent to Telegram successfully.")

    except Exception as e:
        logger.error(f"An error occurred during OpenAI analysis or Telegram notification: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("Starting crypto monitoring script...")
    asyncio.run(analyze_top_cryptos())
    logger.info("Crypto monitoring script finished.")