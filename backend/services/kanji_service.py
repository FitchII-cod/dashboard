import json, datetime, zoneinfo
from pathlib import Path
from backend.config import DATA_DIR, TZ

TZI = zoneinfo.ZoneInfo(TZ)
KPATH = DATA_DIR / "kanji.json"
LEVELS = {"N5","N4","N3","N2","N1"}

def _as_list(data):
    return data if isinstance(data, list) else [data]

def _norm(x: dict) -> dict:
    return {
        "char":   x.get("char"),
        "on":     x.get("on") or [],
        "kun":    x.get("kun") or [],
        "level":  (x.get("level") or "N5").upper(),
        "meaning":x.get("meaning") or None,   # non affiché
        "vocab":  x.get("vocab") or []        # [{w, r}]
    }

def _load_all() -> list[dict]:
    data = json.loads(KPATH.read_text(encoding="utf-8"))
    items = [_norm(e) for e in _as_list(data) if isinstance(e, dict) and e.get("char")]
    # sécurise le level
    for it in items:
        if it["level"] not in LEVELS:
            it["level"] = "N5"
    return items

def kanji_of_the_day() -> dict:
    items = _load_all()
    if not items:
        # fallback minimal
        return {"char":"一","on":["イチ","イツ"],"kun":["ひと","ひと.つ"],"level":"N5","meaning":"un","vocab":[]}
    today = datetime.datetime.now(TZI).date()
    key = int(f"{today.year}{today.month:02}{today.day:02}")
    return items[key % len(items)]
