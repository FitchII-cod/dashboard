# backend/services/kanji_service.py
import json, random
from datetime import datetime
from pathlib import Path
from backend.config import DATA_DIR, TZ

KANJI_PATH = DATA_DIR / "kanji.json"
LEVELS = {"N5","N4","N3","N2","N1"}

def _as_list(data):
    return data if isinstance(data, list) else [data]

def _norm(x: dict) -> dict:
    return {
        "char":    x.get("char"),
        "on":      x.get("on") or [],
        "kun":     x.get("kun") or [],
        "level":   (x.get("level") or "N5").upper(),
        "meaning": x.get("meaning") or "",
        "vocab":   x.get("vocab") or []
    }

def _load_all() -> list[dict]:
    data = json.loads(KANJI_PATH.read_text(encoding="utf-8"))
    items = [_norm(e) for e in _as_list(data) if isinstance(e, dict) and e.get("char")]
    for it in items:
        if it["level"] not in LEVELS:
            it["level"] = "N5"
    return items

def get_kanji_today():
    items = _load_all()
    if not items:
        return {"char":"一","on":["イチ","イツ"],"kun":["ひと","ひと.つ"],"level":"N5","meaning":"un","vocab":[]}
    i = int(datetime.now().strftime("%Y%m%d")) % len(items)
    return items[i]

def get_random_kanji(exclude=None):
    items = _load_all()
    ex = set(exclude or [])
    pool = [k for k in items if k["char"] not in ex] or items
    return random.choice(pool)
