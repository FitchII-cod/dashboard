#!/usr/bin/env python3
import csv, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # dossier "dash"
IN_CSV   = BASE_DIR / "data" / "kanji_min.csv"
OUT_JSON = BASE_DIR / "data" / "kanji.json"

def split_multi_commas(s: str):
    """
    Coupe uniquement sur des virgules. Ne touche pas aux points (ex. た.べる, tabe.ru).
    Tolère '・' en le convertissant en virgule.
    """
    if not s:
        return []
    s = s.replace("・", ",")
    parts = [p.strip() for p in s.split(",")]
    return [p for p in parts if p]

def parse_vocab_list(s: str):
    """
    'w|r,w|r,...' -> [{'w':w,'r':r}, ...]
    Ne découpe que sur des virgules pour séparer les entrées.
    """
    out = []
    if not s:
        return out
    for entry in s.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if "|" in entry:
            w, r = entry.split("|", 1)
            out.append({"w": w.strip(), "r": r.strip()})
        else:
            out.append({"w": entry, "r": ""})
    return out

def main():
    rows = []
    # delimiter=';' pour respecter ton CSV
    with IN_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        for r in reader:
            rows.append({
                "char":    (r.get("char") or "").strip(),
                "on":      split_multi_commas(r.get("on") or ""),
                "kun":     split_multi_commas(r.get("kun") or ""),
                "level":   (r.get("level") or "N5").strip().upper(),
                "meaning": (r.get("meaning") or "").strip() or None,
                "vocab":   parse_vocab_list(r.get("vocab_list") or "")
            })
    # filtre lignes invalides
    rows = [x for x in rows if x["char"] and x["level"]]
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK → {OUT_JSON} ({len(rows)} entrées)")

if __name__ == "__main__":
    main()
