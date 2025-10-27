import os
import json
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from storage3 import SyncStorageClient

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET = "charts"
TZ = ZoneInfo("Asia/Tbilisi")

storage = SyncStorageClient(
    f"{SUPABASE_URL}/storage/v1",
    headers={
        "Authorization": f"Bearer {SERVICE_KEY}",
        "apikey": SERVICE_KEY,
    },
)

def sync_to_supabase(db_path="database/crypto_analysis.db"):
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
            continue

        file_name = os.path.basename(img_path)
        rel_path = f"{today_str}/{file_name}"

        with open(img_path, "rb") as f:
            storage.from_(BUCKET).upload(
                rel_path,
                f,
                {"content-type": "image/png", "x-upsert": "true"},
            )

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{rel_path}"
        manifest.append({"symbol": symbol, "analysis": analysis, "img": public_url})

        print(f"✅ Uploaded {symbol} → {public_url}")

    if manifest:
        manifest_path = f"{today_str}/history.json"
        data = json.dumps(manifest, ensure_ascii=False).encode("utf-8")

        storage.from_(BUCKET).upload(
            manifest_path,
            data,
            {"content-type": "application/json", "x-upsert": "true"},
        )

        print(f"📄 Manifest saved: {SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{manifest_path}")
    else:
        print(f"ℹ️  No records for {today_str}")

    conn.close()

if __name__ == "__main__":
    sync_to_supabase()
