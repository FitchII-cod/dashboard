from flask import Blueprint, jsonify
from backend.services.fx_service import eurjpy_cached, fetch_eurjpy_from_ecb

bp = Blueprint("fx", __name__, url_prefix="/api/fx")

@bp.get("/eurjpy")
def api_fx_eurjpy():
    # simple: renvoyer le cache (rafraîchi par un cron), ou fetch direct si absent
    return jsonify(eurjpy_cached())
