from config.logger import setup_logging
from services.symbol_analysis_service import SymbolAnalysisService
from data_fetching.openai_client import OpenAIClient

logger = setup_logging()

class GPTAnalysisService:
    def __init__(self, api_key):
        self.openai_client = OpenAIClient(api_key)

    def analyze_symbols(self, symbols, binance_client, coingecko_data):
        significant_symbols = []
        symbol_analysis_service = SymbolAnalysisService(binance_client, coingecko_data)

        for symbol in symbols:
            try:
                logger.info(f"Analyzing symbol: {symbol}")
                data = symbol_analysis_service.analyze_symbol(symbol)
                if data:
                    logger.info(f"Analysis complete for {symbol}: {data}")
                    significant_symbols.append(data)
                else:
                    logger.info(f"No significant data found for {symbol}")
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)

        logger.info(f"Completed analysis. Found {len(significant_symbols)} significant symbols.")
        return significant_symbols

    def prepare_gpt_input(self, global_metrics, bitcoin_sentiment, significant_symbols):
        input_text = (
            f"Global Market Metrics:\n"
            f"- Fear & Greed Index: {global_metrics.get('fear_greed', 'N/A')}\n"
            f"- BTC Dominance: {global_metrics.get('btc_dominance', 'N/A')}%\n"
            f"- Bitcoin Sentiment: {bitcoin_sentiment}\n\n"
            "Please analyze each of the following cryptocurrencies and provide actionable insights for each:\n"
            "Each cryptocurrency symbol should be a key in a JSON object, and its value should include the recommendation and reasoning with actionable recommendations BUY, SELL, HOLD, SHORT, or LONG.\n\n"
            "Ensure the response meets these criteria:\n"
            "- **Complete**: Include analysis for all symbols.\n"
            "- **Structured**: Use valid JSON format.\n"
            "- **Concise**: Provide clear, actionable recommendations without excessive details.\n\n"
            "Example:\n"
            "{\n"
            "    'SYMBOL': 'Reasoning for the symbol...'\n"
            "}\n\n"
        )

        for data in significant_symbols:
            input_text += (
                f"{data['symbol']} | Price: {data['price']} | RSI: {data.get('rsi', 'N/A')} | MACD: {data.get('macd', 'N/A')} | "
                f"Signal: {data.get('signal', 'N/A')} | Bollinger Bands: Upper: {data.get('bollinger_upper', 'N/A')}, Lower: {data.get('bollinger_lower', 'N/A')} | "
                f"VWAP: {data.get('vwap', 'N/A')} | ATR: {data.get('atr', 'N/A')} | OBV: {data.get('obv', 'N/A')} | "
                f"Stochastic: {data.get('stochastic', 'N/A')} | ADX: {data.get('adx', 'N/A')} | "
                f"Bid-Ask Spread: {data.get('bid_ask_spread', 'N/A')} | Order Book Imbalance: {data.get('order_book_imbalance', 'N/A')} | "
                f"Volume: {data['volume']} | Liquidity: {data['liquidity']} | CoinGecko Price: {data.get('coingecko_price', 'N/A')} | CoinGecko Market Cap: {data.get('coingecko_market_cap', 'N/A')}\n"
            )

        logger.info("GPT input prepared successfully.")
        return input_text

    def analyze_with_openai(self, input_text):
        try:
            suggestion, reasoning = self.openai_client.analyze_data(input_text)

            logger.info("Received GPT analysis:")
            logger.info(reasoning)

            return suggestion, reasoning
        except Exception as e:
            logger.error("Error during GPT analysis.", exc_info=True)
            raise