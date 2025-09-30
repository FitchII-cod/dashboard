from flask import Blueprint, jsonify
from backend.services.news_service import today_news

bp = Blueprint("news", __name__, url_prefix="/api/news")

@bp.get("/today")
def api_news_today():
    return jsonify(today_news())
