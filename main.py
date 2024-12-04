import asyncio
import argparse
import sys
import json
import ast
import re
from datetime import datetime, timezone
from config.logger import setup_logging
from config.settings import (
    BINANCE_API_KEY, BINANCE_API_SECRET, OPENAI_API_KEY, TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID, TELEGRAM_MESSAGE_DELAY, SYMBOLS_TO_MONITOR, BINANCE_TO_COINGECKO_SYMBOLS,
    CANDLESTICK_INTERVAL
)
from services.data_aggregator_service import DataAggregatorService
from services.gpt_analysis_service import GPTAnalysisService
from services.chart_generator_service import ChartGeneratorService
from notifications.telegram_notifications import send_analysis_to_telegram_with_image
from data_fetching.binance_client import BinanceClient

logger = setup_logging()

def count_tokens(input_text, model="gpt-3.5-turbo"):
    from tiktoken import encoding_for_model
    encoding = encoding_for_model(model)
    return len(encoding.encode(input_text))

def prepare_currency_data(symbols, binance_client):
    currency_data = {}
    for symbol in symbols:
        candles = binance_client.fetch_historical_data(symbol, interval=CANDLESTICK_INTERVAL, limit=50)
        if candles is not None:
            currency_data[symbol] = candles.tail(30)
        else:
            logger.warning(f"Skipping {symbol} due to missing data.")
    return currency_data

def split_reasoning_by_symbol(reasoning, symbols):
    blocks = {}

    try:
        reasoning_data = json.loads(reasoning)
    except json.JSONDecodeError:
        try:
            reasoning_data = ast.literal_eval(reasoning)
        except (SyntaxError, ValueError):
            reasoning_data = {}

    if not reasoning_data:
        for symbol in symbols:
            pattern = re.compile(rf"'{re.escape(symbol)}'\s*:\s*'(.*?)'", re.DOTALL)
            match = pattern.search(reasoning)
            if match:
                blocks[symbol] = match.group(1)
            else:
                blocks[symbol] = None
    else:
        blocks = {symbol: reasoning_data.get(symbol, None) for symbol in symbols}

    unmatched_symbols = [symbol for symbol, reasoning in blocks.items() if reasoning is None]
    if unmatched_symbols:
        logger.warning(f"Unmatched symbols in reasoning: {unmatched_symbols}")

    return blocks

async def analyze_top_cryptos(mode="full-analysis"):
    logger.info("Starting cryptocurrency analysis...")
    BC = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)
    gpt_service = GPTAnalysisService(api_key=OPENAI_API_KEY)
    data_aggregator_service = DataAggregatorService()
    chart_generator_service = ChartGeneratorService()

    try:
        global_metrics, bitcoin_sentiment, coingecko_data = None, None, None
        significant_symbols, chart_files = [], []

        global_metrics = data_aggregator_service.fetch_global_metrics()
        bitcoin_sentiment = data_aggregator_service.fetch_sentiment("BTCUSDT") or "No sentiment data available for Bitcoin."
        coingecko_data = data_aggregator_service.fetch_coingecko_data(SYMBOLS_TO_MONITOR, BINANCE_TO_COINGECKO_SYMBOLS)

        significant_symbols = gpt_service.analyze_symbols(SYMBOLS_TO_MONITOR, BC, coingecko_data)
        if not significant_symbols:
            logger.warning("No significant symbols to process.")
            if mode == "charts-only":
                return
            
        input_text = gpt_service.prepare_gpt_input(global_metrics, bitcoin_sentiment, significant_symbols)
        token_count = count_tokens(input_text)

        logger.info(f"Token count for GPT input: {token_count}")

        # Log the entire input text sent to GPT
        logger.info("--- GPT Input ---")
        logger.info(input_text)

        if token_count > 3500:
            logger.warning("Input exceeds the recommended token limit (3500 tokens).")
            sys.exit(1)
                
        if mode not in ["charts-only", "skip-gpt"]:
            _, reasoning = gpt_service.analyze_with_openai(input_text)

        else:
            reasoning = "Test reasoning for debugging purposes."

        currency_data = prepare_currency_data(SYMBOLS_TO_MONITOR, BC)

        for symbol, df in currency_data.items():
            if not df.empty:
                chart_file = chart_generator_service.generate_single_chart(symbol, df, CANDLESTICK_INTERVAL)
                if chart_file:
                    chart_files.append((symbol, chart_file))

        if chart_files and mode not in ["charts-only", "skip-telegram"]:
            reasoning_blocks = split_reasoning_by_symbol(reasoning, SYMBOLS_TO_MONITOR)
            for symbol, chart_file in chart_files:
                message = reasoning_blocks.get(symbol, f"No specific analysis for {symbol}.")
                current_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                message = f"{symbol} - {message}\n\n{current_datetime} (UTC)"
                await send_analysis_to_telegram_with_image(
                    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, chart_file
                )
                logger.info(f"Sent message for {symbol} to Telegram.")
                await asyncio.sleep(TELEGRAM_MESSAGE_DELAY)

        logger.info("Program finished with no errors.")

    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cryptocurrency analysis tool.")
    parser.add_argument(
        "--mode",
        type=str,
        default="full-analysis",
        choices=["full-analysis", "charts-only", "skip-telegram", "skip-gpt"],
    )
    args = parser.parse_args()

    asyncio.run(analyze_top_cryptos(mode=args.mode))