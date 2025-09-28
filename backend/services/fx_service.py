import json, requests, datetime, zoneinfo
from xml.etree import ElementTree as ET
from backend.config import DATA_DIR, TZ

CACHE = DATA_DIR / "cache" / "fx_eurjpy.json"
TZI = zoneinfo.ZoneInfo(TZ)

ECB_90D = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"

def fetch_eurjpy_from_ecb() -> dict:
    r = requests.get(ECB_90D, timeout=15)
    r.raise_for_status()
    dom = ET.fromstring(r.text)
    # namespace-free parse
    hist = []
    for cube_time in dom.iter():
        if cube_time.tag.endswith("Cube") and "time" in cube_time.attrib:
            t = cube_time.attrib["time"]
            for cube in cube_time:
                if cube.attrib.get("currency") == "JPY":
                    v = float(cube.attrib["rate"])
                    hist.append({"date": t, "value": v})
    hist.sort(key=lambda x: x["date"])
    last = hist[-1] if hist else None
    data = {"date": last["date"] if last else "", "spot": last["value"] if last else None,
            "history": hist[-7:]}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data

def eurjpy_cached() -> dict:
    try:
        if CACHE.exists():
            return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fetch_eurjpy_from_ecb()
