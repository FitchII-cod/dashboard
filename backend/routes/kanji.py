from flask import Blueprint, jsonify
from backend.services.kanji_service import kanji_of_the_day

bp = Blueprint("kanji", __name__)

@bp.get("/api/kanji/today")
def api_kanji_today():
    return jsonify(kanji_of_the_day())
