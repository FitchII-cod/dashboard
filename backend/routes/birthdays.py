from flask import Blueprint, jsonify
from backend.utils.profile import get_profile
from backend.services.birthdays import get_birthdays_view

bp = Blueprint("birthdays", __name__, url_prefix="/api/birthdays")

@bp.get("/")
def api_birthdays():
    pid, prof = get_profile()
    data = get_birthdays_view(str(prof["birthdays_csv"]))
    return jsonify({"profile": pid, "label": prof["label"], **data})
