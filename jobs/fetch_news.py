# jobs/fetch_news.py
from pathlib import Path
import json, sys, datetime as dt
from zoneinfo import ZoneInfo
import feedparser  # installé
# Optionnel: si tu veux aussi tester une source JSON plus tard:
import urllib.request

# ==== chemins portables (Windows & Linux) ====
BASE_DIR = Path(__file__).resolve().parents[1]        # racine du projet
NEWS_DIR = BASE_DIR / "data" / "news"
NEWS_DIR.mkdir(parents=True, exist_ok=True)

# ==== date du jour en Europe/Paris ====
TZ = ZoneInfo("Europe/Paris")
today = dt.datetime.now(TZ).date()
fname = NEWS_DIR / f"{today.isoformat()}.json"

def save_payload(payload: dict):
    fname.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[news] wrote {fname}")

def try_rss(url: str):
    print(f"[news] fetching RSS: {url}")
    feed = feedparser.parse(url)
    if feed.bozo:
        print(f"[news] RSS parse error: {getattr(feed, 'bozo_exception', '')}", file=sys.stderr)
        return None
    if not feed.entries:
        print("[news] RSS empty", file=sys.stderr)
        return None
    e = feed.entries[0]
    title = e.get("title") or "—"
    link  = e.get("link") or ""
    # summary/detail peuvent varier selon le flux
    lead = (e.get("summary") or "").strip()
    body_html = e.get("content", [{}])[0].get("value") if e.get("content") else lead
    if not body_html:
        body_html = f"<p>{lead}</p>" if lead else "<p>—</p>"
    return {
        "title": title,
        "lead": lead,
        "html": body_html,
        "url": link
    }

def main():
    # 1) Essaye un flux RSS japonais “général”
    sources = [
        "https://www3.nhk.or.jp/rss/news/cat0.xml",        # NHK RSS général
        "https://www3.nhk.or.jp/rss/news/cat5.xml",        # économie
        "https://feeds.bbci.co.uk/japanese/rss.xml"        # BBC Japanese (ex)
    ]

    for src in sources:
        try:
            payload = try_rss(src)
            if payload:
                save_payload(payload)
                return
        except Exception as ex:
            print(f"[news] RSS fetch failed: {ex}", file=sys.stderr)

    # 2) (Option) exemple JSON NHK Easy plus tard (commenté par défaut)
    # try:
    #     print("[news] trying NHK Easy JSON list")
    #     with urllib.request.urlopen("https://www3.nhk.or.jp/news/easy/news-list.json", timeout=10) as resp:
    #         data = json.loads(resp.read().decode("utf-8"))
    #         # data est un dict { "YYYY-MM-DD": [ { "news_id": "...", "title": "...", ...}, ... ] }
    #         # on prend le premier titre du jour s'il existe
    #         arr = data.get(today.isoformat(), [])
    #         if arr:
    #             t = arr[0]
    #             payload = {
    #                 "title": t.get("title", "—"),
    #                 "lead": "",
    #                 "html": "<p>本文は個別ニュースのHTML取得が必要です（未実装）。</p>",
    #                 "url": f"https://www3.nhk.or.jp/news/easy/{t.get('news_id')}/{t.get('news_id')}.html"
    #             }
    #             save_payload(payload)
    #             return
    # except Exception as ex:
    #     print(f"[news] NHK Easy JSON failed: {ex}", file=sys.stderr)

    # 3) Si tout échoue, on écrit un placeholder propre
    print("[news] all sources failed; writing placeholder", file=sys.stderr)
    save_payload({
        "title": "—",
        "lead": "",
        "html": "<p>きょうのニュースはありません。</p>",
        "url": ""
    })

if __name__ == "__main__":
    main()
