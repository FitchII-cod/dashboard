# backend/services/fx_service.py
from pathlib import Path
import json, datetime as dt
import requests
from backend.config import DATA_DIR

CACHE = DATA_DIR / "cache" / "fx_eurjpy.json"
ECB_SERIES = "EXJPUS"   # EUR/JPY via ECB (euro foreign exchange reference rates)
# NB: si tu utilises déjà une autre série, garde-la, l’important est d’avoir 5 ans d’historique.

def fetch_eurjpy_from_ecb():
    """Récupère assez d'historique (≥ 6 ans) pour calculer -5y."""
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    end = dt.date.today()
    start = end - dt.timedelta(days=365*6 + 30)  # marge
    # API ECB SDW JSON (ex: https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.JPY.EUR.SP00.A?startPeriod=2019-01-01)
    url = (
        "https://sdw-wsrest.ecb.europa.eu/service/data/EXR/"
        "D.JPY.EUR.SP00.A"  # JPY per EUR, daily, spot
        f"?startPeriod={start.isoformat()}&endPeriod={end.isoformat()}&format=jsondata"
    )

    r = requests.get(url, timeout=20)
    r.raise_for_status()
    js = r.json()

    # parse: la structure ECB est un peu verbeuse; on extrait (date, value)
    # On tolère échecs: si parsing échoue, on garde l'ancien cache.
    history = []
    try:
        # Cherche la série et ses observations
        datasets = js["dataSets"][0]["series"]
        # Il n'y a qu'une série: key "0:0:0:0:0"
        serie_key = list(datasets.keys())[0]
        obs = datasets[serie_key]["observations"]
        # mapping des index -> dates dans structure "structure" -> "dimensions" -> "observation"
        obs_dim = js["structure"]["dimensions"]["observation"][0]["values"]  # dates
        for idx_str, val_arr in obs.items():
            i = int(idx_str)
            date = obs_dim[i]["id"]  # "YYYY-MM-DD"
            value = float(val_arr[0])
            history.append({"date": date, "value": value})
        # trie par date croissante
        history.sort(key=lambda x: x["date"])
    except Exception as e:
        # Si souci, ne casse pas le run
        raise

    spot = history[-1]["value"] if history else None
    payload = {"date": end.isoformat(), "spot": spot, "history": history}
    CACHE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

def _load_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {"date": None, "spot": None, "history": []}

def _value_at_or_before(target_iso: str, history: list[dict]):
    """Prend la valeur du jour cible si dispo, sinon la dernière avant (marchés fermés week-end)."""
    # history est triée
    lo, hi = 0, len(history)-1
    ans = None
    while lo <= hi:
        mid = (lo+hi)//2
        d = history[mid]["date"]
        if d == target_iso:
            return history[mid]["value"], d
        if d < target_iso:
            ans = history[mid]
            lo = mid + 1
        else:
            hi = mid - 1
    return (ans["value"], ans["date"]) if ans else (None, None)

def fx_summary_points():
    """Construit le résumé spot + (-7j, -30j, -1y, -5y) avec écarts en %."""
    data = _load_cache()
    spot = data.get("spot")
    hist = data.get("history", [])
    if not spot or not hist:
        return {"spot": spot, "points": []}

    today = dt.date.today()
    targets = [
        ("-7d",  today - dt.timedelta(days=7)),
        ("-30d", today - dt.timedelta(days=30)),
        ("-1y",  today.replace(year=today.year-1)),
        ("-5y",  today.replace(year=today.year-5)),
    ]

    pts = []
    for label, d in targets:
        # gérer 29/02 etc. si année non bissextile
        try:
            t = d
        except ValueError:
            # fallback: 28 février
            t = d.replace(day=28)
        val, date_found = _value_at_or_before(t.isoformat(), hist)
        if val is None:
            pts.append({"label": label, "date": None, "value": None, "diffPct": None, "diffAbs": None})
        else:
            diff_abs = round(spot - val, 4)
            diff_pct = round((spot - val) / val * 100, 3)
            pts.append({
                "label": label,
                "date": date_found,
                "value": round(val, 4),
                "diffAbs": diff_abs,
                "diffPct": diff_pct
            })

    return {"spot": round(spot, 4), "asOf": data.get("date"), "points": pts}
