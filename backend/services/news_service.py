import os, json, glob, datetime, zoneinfo
from backend.config import DATA_DIR, TZ

TZI = zoneinfo.ZoneInfo(TZ)

def today_news() -> dict:
    today = datetime.datetime.now(TZI).date().isoformat()
    path = DATA_DIR / "news" / f"{today}.json"
    if not path.exists():
        files = sorted(glob.glob(str(DATA_DIR / "news" / "*.json")))
        if not files:
            return {"title":"—","lead":"","html":"<p>きょうのニュースはありません。</p>","url":""}
        path = files[-1]
    with open(path, encoding="utf-8") as f:
        return json.load(f)
