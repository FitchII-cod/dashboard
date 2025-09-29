# backend/routes/weather.py
from flask import Blueprint, jsonify
from pathlib import Path
import json
from backend.config import DATA_DIR

bp = Blueprint("weather", __name__)
CACHE = DATA_DIR / "cache" / "weather_today.json"

@bp.get("/api/weather/today")
def api_weather_today():
    if CACHE.exists():
        return jsonify(json.loads(CACHE.read_text(encoding="utf-8")))
    return jsonify({
        "city":"—","cond":"—","tmax":None,"tmin":None,"tmaxApparent":None,
        "rainProb":None,"rainHours":None,"precipMm":None,"snowMm":None,
        "windMs":None,"windDir":"—","humidityAvg":None,
        "sunrise":None,"sunset":None,"deltaFromYesterday":None,"hint":""
    })
