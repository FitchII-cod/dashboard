from flask import Blueprint, jsonify
from backend.services.fx_service import _load_cache, fx_summary_points

bp = Blueprint("fx", __name__, url_prefix="/api/fx")

@bp.get("/eurjpy")
def eurjpy_raw():
    # compatibilité: renvoie le cache brut (spot + history)
    return jsonify(_load_cache())

@bp.get("/eurjpy/summary")
def eurjpy_summary():
    return jsonify(fx_summary_points())