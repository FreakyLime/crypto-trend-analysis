import asyncio
import argparse
import sys
import re
from modules.config import (
    BINANCE_API_KEY, BINANCE_API_SECRET, OPENAI_API_KEY, TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID, SYMBOLS_TO_MONITOR, BINANCE_TO_COINGECKO_SYMBOLS,
    CANDLESTICK_INTERVAL, setup_logging
)
from modules.data_fetchers import fetch_global_metrics, fetch_sentiment, fetch_coingecko_data
from modules.analysis import analyze_symbols, prepare_gpt_input, analyze_with_openai
from modules.chart_generator import generate_single_chart
from modules.notifications import send_analysis_to_telegram_with_image
from modules.binance_utils import BinanceUtils

logger = setup_logging()

def count_tokens(input_text, model="gpt-3.5-turbo"):
    """Count tokens in the input text for a specific GPT model."""
    from tiktoken import encoding_for_model
    encoding = encoding_for_model(model)
    return len(encoding.encode(input_text))

def prepare_currency_data(symbols, binance_utils):
    """Fetch and prepare candlestick data for the last intervals."""
    currency_data = {}
    for symbol in symbols:
        candles = binance_utils.fetch_historical_data(symbol, interval=CANDLESTICK_INTERVAL, limit=50)
        if candles is not None:
            currency_data[symbol] = candles.tail(30)
        else:
            logger.warning(f"Skipping {symbol} due to missing data.")
    return currency_data

import re

def split_reasoning_by_symbol(reasoning, symbols):
    """
    Split the reasoning text into blocks based on currency symbols.

    Args:
        reasoning (str): The full reasoning text from GPT.
        symbols (list): List of currency symbols to detect.

    Returns:
        dict: A dictionary with currency symbols as keys and their respective reasoning blocks as values.
    """
    # Initialize the dictionary to store reasoning blocks
    blocks = {}

    # Ensure symbols like BTCUSDT are matched correctly; match non-greedy to capture full blocks
    pattern = re.compile(rf"({'|'.join(re.escape(symbol) for symbol in symbols)})\s*:", re.IGNORECASE)

    current_symbol = None
    current_block = []

    # Process each line in the reasoning text
    for line in reasoning.splitlines():
        match = pattern.match(line.strip())
        if match:
            # Save the previous block (if any)
            if current_symbol and current_block:
                blocks[current_symbol] = " ".join(current_block).strip()
                current_block = []

            # Start a new block for the matched symbol
            current_symbol = match.group(1).upper()
            current_block.append(line.strip())
        elif current_symbol:
            # Append the line to the current block
            current_block.append(line.strip())

    # Save the last block after processing all lines
    if current_symbol and current_block:
        blocks[current_symbol] = " ".join(current_block).strip()

    return blocks


async def analyze_top_cryptos(mode="full-analysis"):
    """Analyze cryptocurrencies, generate charts, and optionally send analysis to Telegram."""
    logger.info("Starting cryptocurrency analysis...")
    binance_utils = BinanceUtils(BINANCE_API_KEY, BINANCE_API_SECRET)

    try:
        global_metrics, bitcoin_sentiment, coingecko_data = None, None, None
        significant_symbols, chart_files = [], []

        # Fetch data if not in 'charts-only' mode
        if mode != "charts-only":
            logger.info("Fetching global metrics and sentiment data...")
            global_metrics = fetch_global_metrics()
            bitcoin_sentiment = fetch_sentiment("BTCUSDT") or "No sentiment data available for Bitcoin."
            coingecko_data = fetch_coingecko_data(SYMBOLS_TO_MONITOR, BINANCE_TO_COINGECKO_SYMBOLS)

            # Analyze symbols
            logger.info("Analyzing significant symbols...")
            significant_symbols = analyze_symbols(SYMBOLS_TO_MONITOR, binance_utils, coingecko_data)
            if not significant_symbols:
                logger.warning("No significant symbols to process.")
                if mode == "charts-only":
                    return

            # Prepare GPT input if not in 'skip-gpt' or 'charts-only' mode
            if mode != "skip-gpt":
                logger.info("Preparing input for GPT...")
                input_text = prepare_gpt_input(global_metrics, bitcoin_sentiment, significant_symbols)
                token_count = count_tokens(input_text)
                logger.info(f"Token count for GPT input: {token_count}")

                # Log input text into sent_data.log
                logger.info(f"GPT Request:\n{input_text}")

                if token_count > 3500:
                    logger.warning(f"Input exceeds the recommended token limit (3500 tokens).")
                    sys.exit(1)

                _, reasoning = analyze_with_openai(OPENAI_API_KEY, input_text)
            else:
                reasoning = "Test reasoning for debugging purposes."

        # Generate charts
        logger.info("Fetching candlestick data...")
        currency_data = prepare_currency_data(SYMBOLS_TO_MONITOR, binance_utils)

        logger.info("Generating charts...")
        for symbol, df in currency_data.items():
            if not df.empty:
                chart_file = generate_single_chart(symbol, df, CANDLESTICK_INTERVAL)
                if chart_file:
                    chart_files.append((symbol, chart_file))
            else:
                logger.warning(f"No data for {symbol}. Skipping chart generation.")

        if chart_files:
            logger.info(f"Generated {len(chart_files)} charts.")
        else:
            logger.warning("No charts generated.")

        # Send charts and reasoning to Telegram unless in 'charts-only' or 'skip-telegram' mode
        if mode not in ["charts-only", "skip-telegram"]:
            # Split reasoning into blocks based on currency pairs
            reasoning_blocks = split_reasoning_by_symbol(reasoning, SYMBOLS_TO_MONITOR)

            # Pair each chart with its corresponding reasoning block
            for symbol, chart_file in chart_files:
                message = reasoning_blocks.get(symbol, f"No specific analysis for {symbol}.")
                await send_analysis_to_telegram_with_image(
                    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, chart_file
                )

        if mode == "skip-telegram":
            logger.info("Skipping Telegram notifications as per mode configuration.")

    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cryptocurrency analysis tool.",
        formatter_class=argparse.RawTextHelpFormatter  # Allows for better formatting
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="full-analysis",
        choices=["full-analysis", "charts-only", "skip-telegram", "skip-gpt"],
        help=(
            "Mode of operation:\n\n"
            "  full-analysis   : Runs the complete analysis workflow. (default)\n"
            "  charts-only     : Only generates charts, skips GPT and Telegram.\n"
            "  skip-telegram   : Runs everything but skips sending to Telegram.\n"
            "  skip-gpt        : Skips GPT analysis but continues with chart generation and Telegram notifications."
        )
    )
    args = parser.parse_args()

    asyncio.run(analyze_top_cryptos(mode=args.mode))
