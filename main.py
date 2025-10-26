import asyncio
import argparse
from config.logger import setup_logging
from analysis.analysis import analyze_top_cryptos

logger = setup_logging()

async def run(mode: str):
    await analyze_top_cryptos(mode=mode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cryptocurrency analysis tool.")
    parser.add_argument(
        "--mode",
        type=str,
        default="full-analysis",
        choices=["full-analysis", "charts-only", "skip-telegram", "skip-gpt"],
    )
    args = parser.parse_args()

    try:
        asyncio.run(run(args.mode))
    except Exception as e:
        logger.exception("Analysis failed; skipping upload.")
    else:
        try:
            # Upload only if analysis finished without errors
            from services.upload_to_supabase_service import sync_to_supabase
            sync_to_supabase()
            logger.info("✅ Upload to Supabase completed.")
        except Exception:
            logger.exception("Upload failed.")
