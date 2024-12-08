import json
import ast
import re
from tiktoken import encoding_for_model
import logging

logger = logging.getLogger()

def count_tokens(input_text, model="gpt-3.5-turbo"):
    encoding = encoding_for_model(model)
    return len(encoding.encode(input_text))

def prepare_currency_data(symbols, binance_client, interval, limit=50):
    currency_data = {}
    for symbol in symbols:
        candles = binance_client.fetch_historical_data(symbol, interval=interval, limit=limit)
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