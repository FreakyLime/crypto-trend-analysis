````markdown
# Copilot / AI Agent Instructions — crypto-trend-analysis

Short, actionable guidance to help an AI coding agent be immediately useful in this repository.

**Big Picture**
- **Purpose**: This repo fetches crypto market data, computes technical indicators, runs an OpenAI-powered analysis, generates charts, and posts results to Telegram (and optionally uploads to Supabase).
- **Entry point**: `main.py` — calls `analysis.analyze_top_cryptos()` and may run `services.upload_to_supabase_service.sync_to_supabase()` after success.

**Architecture & Dataflow (quick)**
- **Data sources**: `data_fetching/` contains clients (e.g. `binance_client.py`, `coingecko_client.py`) that return raw JSON or pandas DataFrames for historical candles.
- **Aggregation**: `services/data_aggregator_service.py` centralizes calls to external APIs and builds `coingecko_data`, `global_metrics`, and sentiment strings used later.
- **Symbol analysis**: `services/symbol_analysis_service.py` consumes a `BinanceClient` (or similar) and the coingecko map from `config/settings.py` to compute indicator values using `analysis/technical_indicators/*` functions and returns a dict of metrics per symbol.
- **GPT analysis**: `services/gpt_analysis_service.py` prepares a structured text prompt from symbol metrics and calls `data_fetching/openai_client.py` to obtain structured JSON analysis.
- **Charting / Notifications**: `services/chart_generator_service.py` creates chart images stored under `charts/` and `notifications/telegram_notifications.py` handles async sending to Telegram.

**Important files to reference**
- `config/settings.py` — canonical source for env vars, symbol list (`symbols.json`) and runtime constants (e.g., `CANDLESTICK_INTERVAL`, `TELEGRAM_MESSAGE_DELAY`).
- `analysis/analysis.py` — orchestrates the full pipeline and contains the token count guard (`> 3500` tokens) and the async Telegram send loop.
- `services/` — contains domain services (`gpt_analysis_service.py`, `symbol_analysis_service.py`, `data_aggregator_service.py`, `chart_generator_service.py`, `upload_to_supabase_service.py`).
- `data_fetching/*_client.py` — pattern for external API clients: class-based, methods like `fetch_historical_data` returning pandas DataFrame or primitives.
- `utils/*` and `analysis/technical_indicators/*` — helper utilities and indicator implementations; indicator functions generally accept a DataFrame and return Series/values.

**Project-specific conventions and patterns**
- API clients return pandas DataFrames for historical candle data (see `BinanceClient._parse_historical_data`). Assume DataFrame indexing and `.iloc[-1]` usage.
- Services are synchronous classes, but `analysis.analyze_top_cryptos` is async — treat network/IO in that orchestration as `await` where appropriate (e.g., Telegram sending is async).
- Logging: code uses a centralized `config.logger.setup_logging()`; prefer using `logger.info()/warning()/error()` and preserve `exc_info=True` on caught exceptions.
- Rate-limiting: uses `TELEGRAM_MESSAGE_DELAY` from settings — respect this when inserting sleeps between sends.
- Symbol mapping comes from `config/symbols.json` and `BINANCE_TO_COINGECKO_SYMBOLS` — when adding/remapping symbols, update both files/components.

**Developer workflows / commands**
- Install and activate the virtualenv: `python -m venv env && source env/bin/activate`.
- Install deps: `pip install -r requirements.txt`.
- Run migrations: `python database/migrate.py` (this initializes the SQLite DB referenced by `SQLITE3_DATABASE_FILE`).
- Run the analysis (quick modes):
  - Full run (GPT + Telegram + charts + upload): `python main.py`
  - Charts only: `python main.py --mode charts-only`
  - Skip GPT but still chart: `python main.py --mode skip-gpt`
  - Skip Telegram (useful for dev): `python main.py --mode skip-telegram`
- Tests: run `pytest` from repo root. Integration tests require real API keys — run unit tests locally and mock integration tests in CI.

**Integration points & secrets**
- `OPENAI_API_KEY`, `BINANCE_API_KEY`, `BINANCE_API_SECRET`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and Supabase keys come from env or `.env` (`config/settings.py`).
- Charts are saved under `charts/` timestamped folders by `chart_generator_service.py` — messages reference those files when posting.

**When you edit code — concrete guidelines**
- If adding a new external client, follow `data_fetching/binance_client.py` style: class, small methods, return DataFrame for historical data and raw dicts for order book endpoints.
- If changing the GPT prompt, update `services/gpt_analysis_service.prepare_gpt_input()` and note token-size enforcement in `analysis/analysis.py`. Always log the prompt for debugging (existing code does this).
- When updating indicators, modify functions in `analysis/technical_indicators/*.py` — callers expect Series-like returns and `iloc[-1]` usage.

**Examples (how to make common changes)**
- Add a new symbol: update `config/symbols.json` -> `SYMBOLS_TO_MONITOR` and `BINANCE_TO_COINGECKO_SYMBOLS` in `config/settings.py` mapping will load it.
- Add a new client (e.g., `kraken_client.py`): mirror `BinanceClient` methods `fetch_historical_data`, `fetch_volume`, `fetch_order_book` and register usage in `services/data_aggregator_service.py`.

If anything is unclear or you want this expanded into PR checklist items, tell me which area to expand (prompts, tests, CI, or adding a new data source).
````
