from flask import Blueprint, jsonify
from backend.services.news_service import today_news

bp = Blueprint("news", __name__)

@bp.get("/api/news/today")
def api_news_today():
    return jsonify(today_news())
