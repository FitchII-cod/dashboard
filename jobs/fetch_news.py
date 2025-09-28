#!/usr/bin/env python3
import feedparser, datetime, zoneinfo, json, re
from pathlib import Path
from backend.config import DATA_DIR, TZ

# Exemple : NHK Easy
FEED = "https://www3.nhk.or.jp/news/easy/news-list.rss"

def simplify_html(txt: str) -> str:
    # ici tu peux rajouter des ruby manuellement, ou juste renvoyer brut
    return re.sub(r"<.*?>", "", txt)[:300]  # simplification pour démo

def main():
    today = datetime.datetime.now(zoneinfo.ZoneInfo(TZ)).date().isoformat()
    out = DATA_DIR / "news" / f"{today}.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    feed = feedparser.parse(FEED)
    if not feed.entries:
        return
    e = feed.entries[0]  # premier article
    item = {
        "title": e.title,
        "lead": getattr(e, "summary", "")[:150],
        "html": f"<p>{simplify_html(getattr(e,'summary',''))}</p>",
        "url": e.link,
    }
    out.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
