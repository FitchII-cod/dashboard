# backend/routes/kanji.py
from flask import Blueprint, jsonify, request
from backend.services.kanji_service import get_kanji_today, get_random_kanji

bp = Blueprint("kanji", __name__, url_prefix="/api/kanji")

@bp.get("/today")
def api_kanji_today():
    return jsonify(get_kanji_today())

@bp.get("/random")
def api_kanji_random():
    exclude = request.args.get("exclude", "")
    ex = [x for x in exclude.split(",") if x] if exclude else []
    return jsonify(get_random_kanji(exclude=ex))
