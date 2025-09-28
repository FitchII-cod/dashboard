#!/usr/bin/env python3
import requests, datetime, zoneinfo, json
from pathlib import Path
from backend.config import DATA_DIR, TZ

def fetch_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation&forecast_days=1"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    tz = zoneinfo.ZoneInfo(TZ)
    now = datetime.datetime.now(tz)
    out = DATA_DIR / "cache" / "weather_today.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    # Exemple : Nantes
    data = fetch_weather(47.22, -1.55)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("weather cache updated", now)

if __name__ == "__main__":
    main()
