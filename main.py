import asyncio
import argparse
from config.logger import setup_logging
from analysis.analysis import analyze_top_cryptos

logger = setup_logging()

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