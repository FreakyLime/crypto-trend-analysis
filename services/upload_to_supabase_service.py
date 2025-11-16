import os
import json
import sqlite3
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from storage3 import SyncStorageClient

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET = "charts"
TZ = ZoneInfo("Asia/Tbilisi")


def _make_storage_client():
    if not SUPABASE_URL or not SERVICE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment")

    return SyncStorageClient(
        f"{SUPABASE_URL}/storage/v1",
        headers={
            "Authorization": f"Bearer {SERVICE_KEY}",
            "apikey": SERVICE_KEY,
        },
    )


def _upload_with_retries(storage_from, rel_path, data, headers, max_retries=3):
    attempt = 0
    while True:
        try:
            # If `data` is a file-like object, ensure we seek to start for each attempt
            try:
                if hasattr(data, "seek"):
                    data.seek(0)
            except Exception:
                pass

            storage_from.upload(rel_path, data, headers)
            return True
        except Exception as e:
            attempt += 1
            if attempt >= max_retries:
                print(f"❌ Failed to upload {rel_path} after {attempt} attempts: {e}")
                return False
            backoff = 2 ** attempt
            print(f"⚠️  Upload failed for {rel_path} (attempt {attempt}), retrying in {backoff}s: {e}")
            time.sleep(backoff)


def sync_to_supabase(db_path="database/crypto_analysis.db"):
    if not SUPABASE_URL or not SERVICE_KEY:
        print("SUPABASE_URL or SUPABASE_SERVICE_KEY not configured; skipping upload to Supabase.")
        return

    # Allow overriding DB path via env var when executed in CI/workflow
    db_path = os.getenv("SQLITE3_DATABASE_FILE", db_path)

    storage = _make_storage_client()
    today_str = datetime.now(TZ).strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, symbol, analysis, img FROM history")
    rows = cur.fetchall()

    manifest = []
    for _, symbol, analysis, img_path in rows:
        if not img_path or not os.path.exists(img_path):
            print(f"⚠️  Skipping {symbol} — image not found: {img_path}")
            continue

        src_folder = os.path.basename(os.path.dirname(img_path)) or "unknown"
        if src_folder != today_str:
            # only upload today's files
            continue

        file_name = os.path.basename(img_path)
        rel_path = f"{today_str}/{file_name}"

        try:
            with open(img_path, "rb") as f:
                ok = _upload_with_retries(
                    storage.from_(BUCKET), rel_path, f, {"content-type": "image/png", "x-upsert": "true"}
                )
            if not ok:
                print(f"❌ Giving up on {symbol} upload: {rel_path}")
                continue

            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{rel_path}"
            manifest.append({"symbol": symbol, "analysis": analysis, "img": public_url})

            print(f"✅ Uploaded {symbol} → {public_url}")
        except Exception as e:
            print(f"❌ Exception while uploading {img_path}: {e}")

    if manifest:
        manifest_path = f"{today_str}/history.json"
        data = json.dumps(manifest, ensure_ascii=False).encode("utf-8")

        ok = _upload_with_retries(
            storage.from_(BUCKET), manifest_path, data, {"content-type": "application/json", "x-upsert": "true"}
        )

        if ok:
            print(f"📄 Manifest saved: {SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{manifest_path}")
        else:
            print(f"❌ Failed to save manifest: {manifest_path}")
    else:
        print(f"ℹ️  No records for {today_str}")

    conn.close()


if __name__ == "__main__":
    sync_to_supabase()
