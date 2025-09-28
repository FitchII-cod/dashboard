from flask import Blueprint, jsonify
from backend.utils.profile import get_profile
from backend.services.weather_service import get_weather_today

bp = Blueprint("weather", __name__)

@bp.get("/api/weather/today")
def api_weather_today():
    pid, _ = get_profile()
    return jsonify(get_weather_today(pid))
